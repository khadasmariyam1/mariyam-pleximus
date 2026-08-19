"""
Currency Converter Tool — Pleximus Hackathon (Extension Tool)
External API call + parsing, using Frankfurter (free, no API key, ECB daily rates).

Run: python currency.py
"""

import requests


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

        print("RAW RESPONSE:", data)  # always log raw JSON before parsing

        rates = data.get("rates", {})
        rate = rates.get(to_currency)
        if rate is None:
            return {
                "ok": False,
                "error": f"No rate found for {to_currency}. Check the currency code is valid (e.g. USD, INR, EUR).",
                "raw": data,
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


# --- CLI so you can test/demo it standalone -------------------------------
if __name__ == "__main__":
    print("Currency Converter ready.")
    print("Format: <amount> <from> <to>   e.g.  100 USD INR")
    print("Type 'quit' to exit.\n")

    while True:
        line = input(">>> ").strip()
        if line.lower() in {"quit", "exit"}:
            break
        if not line:
            continue

        parts = line.split()
        if len(parts) != 3:
            print({"ok": False, "error": "Give amount, from-currency, to-currency, e.g. '100 USD INR'"})
            continue

        amount_str, frm, to = parts
        try:
            amount = float(amount_str)
        except ValueError:
            print({"ok": False, "error": f"'{amount_str}' isn't a valid number"})
            continue

        print(convert_currency(amount, frm, to))