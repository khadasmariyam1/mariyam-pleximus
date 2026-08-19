"""
AI Agent — Pleximus Hackathon
Wires an LLM (Gemini, function-calling) up to local tools.
The model decides which tool to call, we run it, and feed the result back.

Setup:
  pip install requests google-generativeai
  export GEMINI_API_KEY="your-key-from-aistudio.google.com"

Run:
  python agent.py
"""

import os
import json
import google.generativeai as genai

from tools import calculator, get_weather, text_utility, convert_currency

# ---------------------------------------------------------------------------
# 1. Configure the LLM
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit(
        "Missing GEMINI_API_KEY.\n"
        "Get one free at aistudio.google.com, then:\n"
        "  export GEMINI_API_KEY='your-key-here'"
    )

genai.configure(api_key=API_KEY)

# ---------------------------------------------------------------------------
# 2. Describe the tools to the model (this is what lets it "decide" to call them)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '12 * (3 + 4)'.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Math expression to evaluate"}
            },
            "required": ["expression"],
        },
    },
    {
        "name": "get_weather",
        "description": "Get current weather (temperature, windspeed) for a location by latitude/longitude.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
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
                "from_currency": {"type": "string", "description": "3-letter currency code, e.g. USD"},
                "to_currency": {"type": "string", "description": "3-letter currency code, e.g. INR"},
            },
            "required": ["amount", "from_currency", "to_currency"],
        },
    },
]

# Map tool name -> actual Python function to run
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_weather": get_weather,
    "text_utility": text_utility,
    "convert_currency": convert_currency,
}

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant with access to tools: calculator, get_weather, "
    "text_utility, and convert_currency. Use a tool whenever the user's request needs it instead of "
    "guessing the answer yourself. If a tool call fails or returns an error, tell "
    "the user clearly what went wrong instead of making something up. Common city "
    "coordinates: Mumbai (19.07, 72.87), Ratnagiri (16.99, 73.31), Delhi (28.61, 77.21), "
    "New York (40.71, -74.01)."
)

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    tools=[{"function_declarations": TOOLS}],
    system_instruction=SYSTEM_INSTRUCTION,
)


# ---------------------------------------------------------------------------
# 3. The agent loop: send message -> handle tool calls -> get final answer
# ---------------------------------------------------------------------------

def run_agent(chat, user_message: str) -> str:
    response = chat.send_message(user_message)

    # A model turn can request one or more tool (function) calls.
    # Keep resolving them until the model responds with plain text.
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
            print(f"  -> calling tool: {tool_name}({args})")

            fn = TOOL_FUNCTIONS.get(tool_name)
            if fn is None:
                result = {"ok": False, "error": f"Unknown tool '{tool_name}'"}
            else:
                try:
                    result = fn(**args)
                except Exception as e:
                    result = {"ok": False, "error": f"Tool crashed: {e}"}

            print(f"     result: {json.dumps(result)}")
            tool_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=tool_name, response={"result": result}
                    )
                )
            )

        response = chat.send_message(tool_responses)


# ---------------------------------------------------------------------------
# 4. Simple CLI loop for demoing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    chat = model.start_chat()
    print("Hackathon agent ready. Try things like:")
    print("  - what's 45 * 12 + 3?")
    print("  - what's the weather in Ratnagiri right now?")
    print("  - how many words are in 'the quick brown fox jumps'?")
    print("  - convert 100 dollars to rupees")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            break
        if not user_input:
            continue
        answer = run_agent(chat, user_input)
        print(f"Agent: {answer}\n")