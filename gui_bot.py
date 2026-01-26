import tkinter as tk
import subprocess

# ---------- Functions ----------

def show_disk():
    output = subprocess.getoutput("df -h")
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, output)

def cleanup():
    subprocess.call("rm -rf /tmp/* ~/.cache/* ~/.local/share/Trash/files/*", shell=True)
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "✔ Cleanup completed successfully")

def run_command():
    cmd = command_entry.get()
    output = subprocess.getoutput(cmd)
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, output)

# ---------- Main Window ----------

root = tk.Tk()
root.title("Linux Lab Command Bot")
root.geometry("820x500")
root.configure(bg="#1e1e2e")

# ---------- Title ----------

title = tk.Label(
    root,
    text="Linux Lab Command Bot",
    bg="#1e1e2e",
    fg="white",
    font=("Arial", 20, "bold")
)
title.pack(pady=15)

# ---------- Button Frame ----------

button_frame = tk.Frame(root, bg="#1e1e2e")
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Disk Usage",
    width=18,
    bg="#4caf50",
    fg="white",
    font=("Arial", 11, "bold"),
    command=show_disk
).grid(row=0, column=0, padx=10)

tk.Button(
    button_frame,
    text="Cleanup System",
    width=18,
    bg="#e53935",
    fg="white",
    font=("Arial", 11, "bold"),
    command=cleanup
).grid(row=0, column=1, padx=10)

# ---------- Command Input ----------

tk.Label(
    root,
    text="Run Custom Command",
    bg="#1e1e2e",
    fg="white",
    font=("Arial", 12)
).pack(pady=10)

command_entry = tk.Entry(root, width=55, font=("Consolas", 11))
command_entry.pack(pady=5)

tk.Button(
    root,
    text="Run Command",
    bg="#2196f3",
    fg="white",
    font=("Arial", 11, "bold"),
    width=20,
    command=run_command
).pack(pady=10)

# ---------- Output Box ----------

output_box = tk.Text(
    root,
    height=12,
    width=95,
    bg="#2e2e3e",
    fg="white",
    font=("Consolas", 10)
)
output_box.pack(pady=10)

root.mainloop()
