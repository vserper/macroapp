import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import threading
import urllib.request
import json
import os
import sys
import subprocess
import tempfile

VERSION = "1.1.0"
GITHUB_API_URL = "https://api.github.com/repos/vserper/macroapp/releases/latest"

pyautogui.PAUSE = 0.05

def check_for_updates():
    try:
        req = urllib.request.Request(GITHUB_API_URL, headers={"User-Agent": "macroapp-updater"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        remote_version = data["tag_name"].lstrip("v")
        if remote_version == VERSION:
            return

        # Find .exe asset in the release
        exe_url = None
        for asset in data.get("assets", []):
            if asset["name"].endswith(".exe"):
                exe_url = asset["browser_download_url"]
                break

        if not exe_url:
            return

        answer = messagebox.askyesno(
            "Update Available",
            f"A new version ({remote_version}) is available.\nYou have v{VERSION}.\n\nUpdate now?"
        )
        if not answer:
            return

        status_var.set("Downloading update...")

        current_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__)
        new_path = current_path + ".new"
        urllib.request.urlretrieve(exe_url, new_path)

        # Batch script: wait for this process to exit, swap files, relaunch
        batch = (
            f'@echo off\n'
            f'timeout /t 2 /nobreak > nul\n'
            f'move /y "{new_path}" "{current_path}"\n'
            f'start "" "{current_path}"\n'
            f'del "%~f0"\n'
        )
        batch_path = os.path.join(tempfile.gettempdir(), "macroapp_update.bat")
        with open(batch_path, "w") as f:
            f.write(batch)

        subprocess.Popen(["cmd", "/c", batch_path], creationflags=subprocess.CREATE_NO_WINDOW)
        messagebox.showinfo("Updated", "Update downloaded! The app will restart.")
        root.destroy()
        sys.exit()

    except Exception:
        pass  # No internet or GitHub unavailable — silently continue

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

def apply_drop_ships():
    raw = text_input.get("1.0", tk.END)
    lines = [line.rstrip() for line in raw.splitlines()]

    # Extract order number
    order_num = ""
    for line in lines:
        if line.startswith("Order #"):
            order_num = line.replace("Order #", "").strip()
            break

    # Extract customer name (first non-empty line after "Ship To Address")
    customer = ""
    for i, line in enumerate(lines):
        if line.strip() == "Ship To Address":
            for k in range(i + 1, len(lines)):
                if lines[k].strip():
                    customer = lines[k].strip()
                    break
            break

    results = []
    if order_num or customer:
        results.append(f"PO: {order_num} | Customer: {customer}")
        results.append("")

    for i, line in enumerate(lines):
        if line.startswith("SKU:"):
            sku = line[4:].strip()
            if "_" in sku:
                sku = sku.split("_", 1)[1]
            title = lines[i - 1].strip() if i > 0 else ""
            qty = ""
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("$"):
                    for k in range(j + 1, len(lines)):
                        if lines[k].strip():
                            qty = lines[k].strip()
                            break
                    break
            results.append(f"Qty: {qty} - SKU: {sku} | Item: {title}")

    text_input.delete("1.0", tk.END)
    text_input.insert("1.0", "\n".join(results))

def apply_sg():
    raw = text_input.get("1.0", tk.END)
    lines = raw.splitlines()
    result = []
    for line in lines:
        if "\t" in line:
            parts = line.split("\t")
            if len(parts) >= 2 and not parts[1].startswith("SG"):
                parts[1] = "SG" + parts[1]
            result.append("\t".join(parts))
        else:
            result.append(line)
    text_input.delete("1.0", tk.END)
    text_input.insert("1.0", "\n".join(result))

root = tk.Tk()
root.title(f"Form Macro v{VERSION}")
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

# Buttons row
btn_frame = ttk.Frame(frame)
btn_frame.grid(row=4, column=0, columnspan=2, pady=(10, 4))

drop_ships_btn = ttk.Button(btn_frame, text="Drop Ships", command=apply_drop_ships)
drop_ships_btn.pack(side=tk.LEFT, padx=(0, 8))

sg_btn = ttk.Button(btn_frame, text="SG", command=apply_sg)
sg_btn.pack(side=tk.LEFT, padx=(0, 8))

run_btn = ttk.Button(btn_frame, text="Run Macro", command=run_macro)
run_btn.pack(side=tk.LEFT)

# Status
status_var = tk.StringVar(value="Paste values above, then click Run.")
ttk.Label(frame, textvariable=status_var, foreground="gray").grid(row=5, column=0, columnspan=2)

# Check for updates in background so it doesn't slow down startup
threading.Thread(target=check_for_updates, daemon=True).start()

root.mainloop()
