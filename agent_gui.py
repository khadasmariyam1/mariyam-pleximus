"""
AI Agent — Pleximus Hackathon (GUI version)
Same Gemini function-calling logic as agent.py, wrapped in a tkinter chat window.

Setup:
  pip install requests google-generativeai
  Set GEMINI_API_KEY in your terminal before running (see README).

Run:
  python agent_gui.py
"""
#this isthe filewhich contains all theprojects integrated at once.. if u want to see em alll seperately plz refer to the files namely calculator.py currency.py weather.py and textutility.py
import os
import json
import threading
import tkinter as tk
from tkinter import font as tkfont, scrolledtext

import google.generativeai as genai

from tools import calculator, get_weather, text_utility, convert_currency

# ---------------------------------------------------------------------------
# 1. Configure the LLM (same as agent.py)
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit(
        "Missing GEMINI_API_KEY.\n"
        "Get one free at aistudio.google.com, then:\n"
        "  $env:GEMINI_API_KEY='your-key-here'   (PowerShell)"
    )

genai.configure(api_key=API_KEY)

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '12 * (3 + 4)'.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get current weather (temperature, windspeed) for a location by latitude/longitude.",
        "parameters": {
            "type": "object",
            "properties": {"latitude": {"type": "number"}, "longitude": {"type": "number"}},
            "required": ["latitude", "longitude"],
        },
    },
    {
        "name": "text_utility",
        "description": "Perform a text operation: word_count, char_count, reverse, uppercase, lowercase, or title_case.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["word_count", "char_count", "reverse", "uppercase", "lowercase", "title_case"],
                },
                "text": {"type": "string"},
            },
            "required": ["action", "text"],
        },
    },
    {
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another using live exchange rates, e.g. 100 USD to INR.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
]

TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_weather": get_weather,
    "text_utility": text_utility,
    "convert_currency": convert_currency,
}

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant with access to tools: calculator, get_weather, "
    "text_utility, and convert_currency. Use a tool whenever the user's request needs it "
    "instead of guessing the answer yourself. If a tool call fails or returns an error, tell "
    "the user clearly what went wrong instead of making something up. Common city "
    "coordinates: Mumbai (19.07, 72.87), Ratnagiri (16.99, 73.31), Delhi (28.61, 77.21), "
    "New York (40.71, -74.01)."
)

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    tools=[{"function_declarations": TOOLS}],
    system_instruction=SYSTEM_INSTRUCTION,
)


def run_agent(chat, user_message: str, log_fn):
    """Same tool-calling loop as agent.py, but calls log_fn(text) to show tool activity in the GUI."""
    response = chat.send_message(user_message)

    while True:
        function_calls = [
            part.function_call
            for part in response.candidates[0].content.parts
            if part.function_call
        ]
        if not function_calls:
            return response.text

        tool_responses = []
        for call in function_calls:
            tool_name = call.name
            args = dict(call.args)
            log_fn(f"  → calling tool: {tool_name}({args})")

            fn = TOOL_FUNCTIONS.get(tool_name)
            if fn is None:
                result = {"ok": False, "error": f"Unknown tool '{tool_name}'"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = {"ok": False, "error": f"Tool crashed: {e}"}

            log_fn(f"     result: {json.dumps(result)}")
            tool_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name, response={"result": result}
                    )
                )
            )

        response = chat.send_message(tool_responses)


# ---------------------------------------------------------------------------
# 2. Chat window GUI
# ---------------------------------------------------------------------------

class AgentApp:
    def __init__(self, root):
        self.root = root
        root.title("Hackathon AI Agent")
        root.geometry("480x560")
        root.configure(bg="#1e1e2e")

        text_font = tkfont.Font(size=11)

        self.chat_box = scrolledtext.ScrolledText(
            root, wrap="word", font=text_font, bg="#2a2a3d", fg="white",
            insertbackground="white", bd=0, state="disabled",
        )
        self.chat_box.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.chat_box.tag_config("user", foreground="#7ee787")
        self.chat_box.tag_config("agent", foreground="#f5a623")
        self.chat_box.tag_config("tool", foreground="#888888")

        input_frame = tk.Frame(root, bg="#1e1e2e")
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.input_var = tk.StringVar()
        entry = tk.Entry(
            input_frame, textvariable=self.input_var, font=text_font,
            bd=0, bg="#2a2a3d", fg="white", insertbackground="white",
        )
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        entry.bind("<Return>", lambda event: self.send())
        entry.focus()

        tk.Button(
            input_frame, text="Send", font=text_font, bd=0, bg="#f5a623", fg="white",
            activebackground="#e0951c", command=self.send,
        ).pack(side="right", ipadx=10, ipady=6)

        self.chat = model.start_chat()
        self.append("agent", "Agent ready. Try: 'what's 45*12?', 'weather in Ratnagiri', "
                              "'convert 100 USD to INR', 'word count of hello world'.")

    def append(self, tag, text):
        self.chat_box.config(state="normal")
        prefix = {"user": "You: ", "agent": "Agent: ", "tool": ""}[tag]
        self.chat_box.insert("end", f"{prefix}{text}\n\n", tag)
        self.chat_box.config(state="disabled")
        self.chat_box.see("end")

    def send(self):
        user_message = self.input_var.get().strip()
        if not user_message:
            return
        self.input_var.set("")
        self.append("user", user_message)
        self.append("agent", "Thinking...")

        # Run the (blocking, network-bound) agent call in a background thread
        # so the GUI window doesn't freeze while waiting on the API.
        threading.Thread(target=self._get_response, args=(user_message,), daemon=True).start()

    def _get_response(self, user_message):
        answer = run_agent(self.chat, user_message, log_fn=lambda t: self.root.after(0, self.append, "tool", t))
        self.root.after(0, self._show_answer, answer)

    def _show_answer(self, answer):
        # remove the "Thinking..." placeholder line, then show the real answer
        self.chat_box.config(state="normal")
        content = self.chat_box.get("1.0", "end")
        lines = content.rstrip("\n").split("\n")
        if lines and lines[-1] == "Agent: Thinking...":
            self.chat_box.delete("end-3l", "end-1l")
        self.chat_box.config(state="disabled")
        self.append("agent", answer)


if __name__ == "__main__":
    root = tk.Tk()
    app = AgentApp(root)
    root.mainloop()
    
