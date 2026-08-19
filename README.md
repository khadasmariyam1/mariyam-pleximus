# Hackathon Agent — Core Tools

A tool-calling AI agent built for the Pleximus AI Hackathon (FAMT Ratnagiri).

## Files
- `tools.py` — the 3 core tools: `calculator`, `get_weather`, `text_utility`
- `agent.py` — Gemini function-calling loop that wires the LLM to those tools
- `requirements.txt` — dependencies

## Setup
```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your-key-from-aistudio.google.com"
```

## Run
```bash
python agent.py
```

Try:
- `what's 45 * 12 + 3?` → calculator
- `what's the weather in Ratnagiri right now?` → get_weather
- `how many words are in 'the quick brown fox jumps'?` → text_utility

## How it works
1. `tools.py` has plain Python functions, each returning a JSON-safe dict.
2. `agent.py` describes those functions to Gemini as `function_declarations` (name,
   description, parameter schema) — this is what lets the model decide *when* and
   *which* tool to call, rather than you hardcoding intent detection.
3. When Gemini responds with a `function_call` instead of text, `agent.py` runs the
   matching Python function and sends the result back as a `function_response`.
4. The loop repeats until Gemini has enough info to answer in plain text.

## Adding an extension tool (next step)
To add one of the extension tools (currency converter, Wikipedia lookup, etc.):
1. Write the function in `tools.py`, following the same pattern (take simple
   args, return a dict with `"ok"` + either `"result"` or `"error"`).
2. Add its `function_declarations` entry to the `TOOLS` list in `agent.py`.
3. Add it to `TOOL_FUNCTIONS`.

That's the whole pattern — no other code changes needed.

## Notes
- Not using OpenAI/Anthropic? Swap the `google.generativeai` calls in `agent.py`
  for the equivalent client — the `tools.py` functions and JSON schema translate
  directly to OpenAI's `tools` param or Anthropic's `tools` param.
- Always check the console output — every tool call and its raw result is printed,
  which makes debugging "the tool isn't working" issues much faster.
