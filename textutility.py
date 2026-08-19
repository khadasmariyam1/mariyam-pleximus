"""
Word/Text Utility Tool — Pleximus Hackathon
Pure local string manipulation. No API dependency.

Run: python text_utility.py
"""


def text_utility(action: str, text: str) -> dict:
    """
    Perform a simple text operation.
    action: one of 'word_count', 'char_count', 'reverse', 'uppercase',
            'lowercase', 'title_case', 'remove_spaces', 'count_vowels'
    """
    action = action.lower().strip()

    if not text:
        return {"ok": False, "error": "No text provided"}

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
    elif action == "remove_spaces":
        result = text.replace(" ", "")
    elif action == "count_vowels":
        result = sum(1 for ch in text.lower() if ch in "aeiou")
    else:
        return {
            "ok": False,
            "error": (
                f"Unknown action '{action}'. Try: word_count, char_count, reverse, "
                f"uppercase, lowercase, title_case, remove_spaces, count_vowels"
            ),
        }

    return {"ok": True, "action": action, "input": text, "result": result}


ACTIONS = [
    "word_count", "char_count", "reverse", "uppercase",
    "lowercase", "title_case", "remove_spaces", "count_vowels",
]

# --- CLI so you can test/demo it standalone -------------------------------
if __name__ == "__main__":
    print("Word/Text Utility ready.")
    print(f"Actions: {', '.join(ACTIONS)}")
    print("Type: <action> <text>   e.g.  word_count the quick brown fox")
    print("Type 'quit' to exit.\n")

    while True:
        line = input(">>> ").strip()
        if line.lower() in {"quit", "exit"}:
            break
        if not line:
            continue

        parts = line.split(maxsplit=1)
        if len(parts) < 2:
            print({"ok": False, "error": "Give both an action and some text, e.g. 'reverse hello'"})
            continue

        action, text = parts[0], parts[1]
        print(text_utility(action, text))