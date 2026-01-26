import tkinter as tk
import paramiko

# ---------- CONFIG ----------

CLIENT_FILE = "clients.txt"
SSH_USER = "labuser"   # CHANGE if needed
SSH_TIMEOUT = 5

# ---------- LOAD CLIENT IPS ----------

def load_clients():
    try:
        with open(CLIENT_FILE, "r") as file:
            clients = [line.strip() for line in file if line.strip()]
        return clients
    except FileNotFoundError:
        return []

CLIENTS = load_clients()

# ---------- SSH EXECUTION FUNCTION ----------

def run_remote_command(command):
    output_data = ""

    if not CLIENTS:
        return "❌ No clients found in clients.txt"

    for ip in CLIENTS:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(
                hostname=ip,
                username=SSH_USER,
                timeout=SSH_TIMEOUT
            )

            stdin, stdout, stderr = ssh.exec_command(command)

            out = stdout.read().decode()
            err = stderr.read().decode()

            ssh.close()

            output_data += f"\n========== {ip} ==========\n"
            output_data += out if out else err

        except Exception as e:
            output_data += f"\n========== {ip} ==========\nERROR: {str(e)}\n"

    return output_data

# ---------- BUTTON FUNCTIONS ----------

def show_disk():
    output = run_remote_command("df -h")
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, output)

def cleanup():
    cmd = "rm -rf /tmp/* ~/.cache/* ~/.local/share/Trash/files/*"
    output = run_remote_command(cmd)
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "✔ Cleanup completed\n" + output)

def run_command():
    cmd = command_entry.get()
    if not cmd.strip():
        return

    output = run_remote_command(cmd)
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, output)

# ---------- GUI ----------

root = tk.Tk()
root.title("Linux Lab Command Bot (Centralized)")
root.geometry("820x500")
root.configure(bg="#1e1e2e")

# ---------- TITLE ----------

title = tk.Label(
    root,
    text="Linux Lab Command Bot",
    bg="#1e1e2e",
    fg="white",
    font=("Arial", 20, "bold")
)
title.pack(pady=15)

# ---------- BUTTON FRAME ----------

button_frame = tk.Frame(root, bg="#1e1e2e")
button_frame.pack(pady=10)

tk.Button(
    button_frame,
    text="Disk Usage (All PCs)",
    width=20,
    bg="#4caf50",
    fg="white",
    font=("Arial", 11, "bold"),
    command=show_disk
).grid(row=0, column=0, padx=10)

tk.Button(
    button_frame,
    text="Cleanup All PCs",
    width=20,
    bg="#e53935",
    fg="white",
    font=("Arial", 11, "bold"),
    command=cleanup
).grid(row=0, column=1, padx=10)

# ---------- COMMAND INPUT ----------

tk.Label(
    root,
    text="Run Command on All Lab PCs",
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

# ---------- OUTPUT BOX ----------

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
