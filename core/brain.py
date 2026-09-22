import re
import json
import ollama
from typing import Generator
from core.tools import TOOL_REGISTRY
from core.memory import JarvisMemory

SYSTEM_PROMPT = (
    "You are JAVI, a razor-sharp, concise, and efficient desktop AI assistant. "
    "Keep replies crisp (1-2 sentences). "
    "When asked about computer hardware, opening apps, searching the web, volume, media playback, "
    "daily briefings, or analyzing the screen, always invoke your tools. "
    "Never fabricate telemetry data; only report values received from tool execution."
)

class JarvisBrain:
    def __init__(self, model_name: str = "qwen2.5:3b"):
        self.model_name = model_name
        self.memory = JarvisMemory()

        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        recent = self.memory.get_recent_history(limit=6)
        if recent:
            self.messages.extend(recent)

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_system_diagnostics",
                    "description": "Fetch real-time CPU utilization, RAM usage, and battery state.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "launch_application",
                    "description": "Launch a Windows application such as calc, notepad, mspaint, or chrome.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "app_name": {"type": "string", "description": "Executable or alias of the app"}
                        },
                        "required": ["app_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the live web for facts, latest news, or real-time info.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query keywords"}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_system_volume",
                    "description": "Set master audio volume level as an integer percentage from 0 to 100.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level": {"type": "integer", "description": "Volume level between 0 and 100"}
                        },
                        "required": ["level"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "toggle_mute",
                    "description": "Toggle master audio mute state on or off.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "control_media",
                    "description": "Control system media playback (play_pause, next, previous, stop).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["play_pause", "next", "previous", "stop"],
                                "description": "The media playback action to perform"
                            }
                        },
                        "required": ["action"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_daily_briefing",
                    "description": "Provide a comprehensive daily briefing covering date, time, battery level, and weather conditions.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_screen",
                    "description": "Capture a live screenshot of the computer monitor and answer questions or diagnose what is displayed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "Specific question or request about the screen content"}
                        },
                        "required": ["prompt"],
                    },
                },
            },
        ]

    def chat_stream(self, user_input: str) -> Generator[str, None, None]:
        self.messages.append({"role": "user", "content": user_input})
        self.memory.save_message("user", user_input)

        response = ollama.chat(
            model=self.model_name,
            messages=self.messages,
            tools=self.tools,
        )

        message = response.get("message", {})

        if message.get("tool_calls"):
            self.messages.append(message)

            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                args = tool_call["function"].get("arguments", {})

                print(f"\n[JAVI Action] -> Executing {func_name}({args})")

                if func_name in TOOL_REGISTRY:
                    tool_output = TOOL_REGISTRY[func_name](**args)
                else:
                    tool_output = {"error": f"Tool '{func_name}' not implemented."}

                self.messages.append({
                    "role": "tool",
                    "content": json.dumps(tool_output),
                })

        stream = ollama.chat(
            model=self.model_name,
            messages=self.messages,
            stream=True,
        )

        buffer = ""
        full_reply = ""
        sentence_end = re.compile(r'([.!?]+(?:\s+|\n+))')

        for chunk in stream:
            token = chunk["message"]["content"]
            buffer += token
            full_reply += token

            parts = sentence_end.split(buffer)
            if len(parts) > 1:
                completed_sentence = parts[0] + parts[1]
                buffer = "".join(parts[2:])
                clean_sentence = completed_sentence.strip()
                if clean_sentence:
                    yield clean_sentence

        remaining = buffer.strip()
        if remaining:
            yield remaining

        self.messages.append({"role": "assistant", "content": full_reply})
        self.memory.save_message("assistant", full_reply)