"""
Core tools for the AI agent.
Each function does ONE job and returns a plain dict (JSON-serializable),
so it's easy to hand the result back to the LLM.
"""

import ast
import operator
import requests


# ---------------------------------------------------------------------------
# 1. CALCULATOR — pure local logic, no API
# ---------------------------------------------------------------------------

# Only allow safe math operators (never use bare eval() on LLM/user input)
_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant):  # numbers
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculator(expression: str) -> dict:
    """Safely evaluate a basic arithmetic expression like '12 * (3 + 4)'."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return {"ok": True, "expression": expression, "result": result}
    except ZeroDivisionError:
        return {"ok": False, "expression": expression, "error": "Division by zero"}
    except Exception as e:
        return {"ok": False, "expression": expression, "error": f"Could not evaluate: {e}"}


# ---------------------------------------------------------------------------
# 2. WEATHER LOOKUP — Open-Meteo (external API call + parsing)
# ---------------------------------------------------------------------------

def get_weather(latitude: float, longitude: float) -> dict:
    """Get current weather for a lat/lon using Open-Meteo (no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": latitude, "longitude": longitude, "current_weather": "true"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print("RAW WEATHER RESPONSE:", data)  # always log raw JSON while debugging

        current = data.get("current_weather")
        if not current:
            return {"ok": False, "error": "No 'current_weather' in response", "raw": data}

        return {
            "ok": True,
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": current.get("temperature"),
            "windspeed_kmh": current.get("windspeed"),
            "weather_code": current.get("weathercode"),
            "time": current.get("time"),
        }
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": f"Weather API request failed: {e}"}


# ---------------------------------------------------------------------------
# 3. WORD / TEXT UTILITY — local string manipulation
# ---------------------------------------------------------------------------

def text_utility(action: str, text: str) -> dict:
    """
    Perform a simple text operation.
    action: one of 'word_count', 'char_count', 'reverse', 'uppercase', 'lowercase', 'title_case'
    """
    action = action.lower().strip()

    if action == "word_count":
        result = len(text.split())
    elif action == "char_count":
        result = len(text)
    elif action == "reverse":
        result = text[::-1]
    elif action == "uppercase":
        result = text.upper()
    elif action == "lowercase":
        result = text.lower()
    elif action == "title_case":
        result = text.title()
    else:
        return {
            "ok": False,
            "error": f"Unknown action '{action}'. Try: word_count, char_count, "
                     f"reverse, uppercase, lowercase, title_case",
        }

    return {"ok": True, "action": action, "input": text, "result": result}


# ---------------------------------------------------------------------------
# 4. CURRENCY CONVERTER — Frankfurter (extension tool)
# ---------------------------------------------------------------------------

def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount from one currency to another using live ECB reference rates."""
    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    url = "https://api.frankfurter.dev/v1/latest"
    params = {"from": from_currency, "to": to_currency}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        print("RAW CURRENCY RESPONSE:", data)

        rates = data.get("rates", {})
        rate = rates.get(to_currency)
        if rate is None:
            return {
                "ok": False,
                "error": f"No rate found for {to_currency}. Check the currency code (e.g. USD, INR, EUR).",
            }

        converted = round(amount * rate, 2)
        return {
            "ok": True,
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "rate": rate,
            "converted": converted,
            "date": data.get("date"),
        }
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Request timed out — check your internet connection"}
    except requests.exceptions.RequestException as e:
        return {"ok": False, "error": f"Currency API request failed: {e}"}


# Quick manual test — run `python tools.py` to sanity-check all three tools
if __name__ == "__main__":
    print(calculator("3 + 4 * 2"))
    print(calculator("10 / 0"))
    print(get_weather(19.07, 72.87))  # Mumbai
    print(text_utility("word_count", "hello there hackathon world"))
    print(text_utility("reverse", "hello"))
    print(convert_currency(100, "USD", "INR"))