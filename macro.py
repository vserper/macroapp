import tkinter as tk
from tkinter import ttk
import pyautogui
import time
import threading

pyautogui.PAUSE = 0.05

def run_macro():
    raw = text_input.get("1.0", tk.END)
    items = [line.strip() for line in raw.splitlines() if line.strip()]
    if not items:
        status_var.set("No items to type.")
        return

    delay = delay_var.get()
    separator = separator_var.get()

    status_var.set(f"Starting in {delay}s — click into your form now...")
    run_btn.config(state=tk.DISABLED)

    def do_typing():
        time.sleep(delay)
        for i, item in enumerate(items):
            pyautogui.typewrite(item, interval=0.03)
            if separator == "Tab":
                pyautogui.press("tab")
            elif separator == "Enter":
                pyautogui.press("enter")
            elif separator == "Tab+Enter":
                pyautogui.press("tab")
                pyautogui.press("enter")
            status_var.set(f"Typed {i+1}/{len(items)}: {item}")
        status_var.set(f"Done. Typed {len(items)} items.")
        run_btn.config(state=tk.NORMAL)

    threading.Thread(target=do_typing, daemon=True).start()

root = tk.Tk()
root.title("Form Macro")
root.resizable(True, True)

frame = ttk.Frame(root, padding=12)
frame.grid(sticky="nsew")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)

# Input
ttk.Label(frame, text="Values (one per line):").grid(row=0, column=0, columnspan=2, sticky="w")
text_input = tk.Text(frame, height=15, width=40)
text_input.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(4, 8))
frame.rowconfigure(1, weight=1)

# Separator key
ttk.Label(frame, text="Key between fields:").grid(row=2, column=0, sticky="w")
separator_var = tk.StringVar(value="Tab")
sep_menu = ttk.Combobox(frame, textvariable=separator_var, values=["Tab", "Enter", "Tab+Enter"], state="readonly", width=14)
sep_menu.grid(row=2, column=1, sticky="w", padx=(4, 0))

# Delay
ttk.Label(frame, text="Start delay (seconds):").grid(row=3, column=0, sticky="w", pady=(6, 0))
delay_var = tk.IntVar(value=3)
delay_spin = ttk.Spinbox(frame, from_=1, to=30, textvariable=delay_var, width=5)
delay_spin.grid(row=3, column=1, sticky="w", padx=(4, 0), pady=(6, 0))

# Run button
run_btn = ttk.Button(frame, text="Run Macro", command=run_macro)
run_btn.grid(row=4, column=0, columnspan=2, pady=(10, 4))

# Status
status_var = tk.StringVar(value="Paste values above, then click Run.")
ttk.Label(frame, textvariable=status_var, foreground="gray").grid(row=5, column=0, columnspan=2)

root.mainloop()
