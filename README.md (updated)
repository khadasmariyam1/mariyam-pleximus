# Hackathon Agent — Pleximus AI Hackathon (FAMT Ratnagiri)

A tool-calling AI agent that takes a natural-language request and correctly decides
which tool to call: calculator, weather lookup, text utility, and currency converter.

## What's in this repo

**The actual agent (main deliverable):**
- `agent.py` — Gemini function-calling loop that wires the LLM to the tools below
- `tools.py` — all 4 tools combined in one file, imported by `agent.py`:
  - `calculator` — pure local logic, no API
  - `get_weather` — external API call + parsing (Open-Meteo)
  - `text_utility` — local string manipulation
  - `convert_currency` — external API call + parsing (Frankfurter) — **extension tool**

**Standalone versions (for testing/demo of each tool individually):**
- `calculator.py` / `calculator_gui.py` — terminal and popup-window versions
- `weather.py` / `weather_gui.py` — terminal and popup-window versions
- `textutility.py` — terminal version
- `currency.py` — terminal version

**Other:**
- `requirements.txt` — dependencies
- `README.md` — this file

## Setup
```bash
pip install -r requirements.txt
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com) (no
billing required for the free tier), then set it in your terminal:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your-key-here"

# Mac/Linux
export GEMINI_API_KEY="your-key-here"
```

## Run the agent
```bash
python agent.py
```

Try:
- `what's 45 * 12 + 3?` → calculator
- `what's the weather in Ratnagiri right now?` → get_weather
- `how many words are in 'the quick brown fox jumps'?` → text_utility
- `convert 100 dollars to rupees` → convert_currency

## Run an individual tool
Each standalone file also runs on its own, e.g.:
```bash
python calculator.py       # terminal version
python calculator_gui.py   # popup window version
python weather_gui.py      # popup window version
```

## How the agent works
1. `tools.py` has plain Python functions, each returning a JSON-safe dict with
   `"ok": True/False` so errors are handled consistently.
2. `agent.py` describes those functions to Gemini as `function_declarations`
   (name, description, parameter schema) — this is what lets the model decide
   *when* and *which* tool to call, rather than hardcoding intent detection.
3. When Gemini responds with a `function_call` instead of text, `agent.py` runs
   the matching Python function and sends the result back as a `function_response`.
4. The loop repeats until Gemini has enough info to answer in plain text.

## Edge cases handled
- Calculator: division by zero, invalid syntax — returns a clean error, no crash
- Weather / Currency: request timeouts, unexpected API responses, invalid inputs
- Text utility: unknown action, empty text

## Notes
- Uses `gemini-3.6-flash` as the model.
- Not using Gemini? The `tools.py` functions and JSON schema in `agent.py`
  translate directly to OpenAI's `tools` param or Anthropic's `tools` param.
