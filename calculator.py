"""
Calculator Tool — Pleximus Hackathon (GUI version)
Pure local logic, no API dependency. Uses tkinter (built into Python) for a popup window.

Run: python calculator_gui.py
"""

import ast
import operator
import tkinter as tk
from tkinter import font as tkfont

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
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> dict:
    """Same core logic as the terminal version — safe AST-based eval."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return {"ok": True, "expression": expression, "result": result}
    except ZeroDivisionError:
        return {"ok": False, "expression": expression, "error": "Division by zero"}
    except SyntaxError:
        return {"ok": False, "expression": expression, "error": "Invalid expression"}
    except Exception as e:
        return {"ok": False, "expression": expression, "error": f"Could not evaluate: {e}"}


# --- GUI ---------------------------------------------------------------

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Hackathon Calculator")
        root.geometry("320x420")
        root.resizable(False, False)
        root.configure(bg="#1e1e2e")

        display_font = tkfont.Font(size=24)
        btn_font = tkfont.Font(size=14)

        self.display_var = tk.StringVar(value="")
        display = tk.Entry(
            root, textvariable=self.display_var, font=display_font,
            justify="right", bd=0, bg="#2a2a3d", fg="white",
            insertbackground="white",
        )
        display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=15, ipady=15)

        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("C", 4, 2), ("+", 4, 3),
            ("(", 5, 0), (")", 5, 1), ("=", 5, 2, 2),
        ]

        for spec in buttons:
            text, row, col = spec[0], spec[1], spec[2]
            colspan = spec[3] if len(spec) > 3 else 1
            bg = "#f5a623" if text == "=" else ("#3a3a4d" if text == "C" else "#2f2f42")
            btn = tk.Button(
                root, text=text, font=btn_font, bd=0, bg=bg, fg="white",
                activebackground="#4a4a60", command=lambda t=text: self.on_press(t),
            )
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=4, pady=4)

        for i in range(6):
            root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            root.grid_columnconfigure(i, weight=1)

    def on_press(self, key):
        if key == "C":
            self.display_var.set("")
        elif key == "=":
            expr = self.display_var.get()
            result = calculator(expr)
            if result["ok"]:
                self.display_var.set(str(result["result"]))
            else:
                self.display_var.set(f"Error: {result['error']}")
        else:
            current = self.display_var.get()
            # if last result was shown, clear before starting a new expression
            if current.startswith("Error"):
                current = ""
            self.display_var.set(current + key)


if __name__ == "__main__":
    root = tk.Tk()
    app = CalculatorApp(root)
    root.mainloop()