# OPS445 Assignment 2: System Monitoring and Alerts

## 👥 Group Members

| Name                 | Role / Contribution                        |
|----------------------|---------------------------------------------|
| Thomas Chan          | Metric collection using `psutil` and `subprocess` |
| Vishwanand Doobay    | Threshold checking and logging with `logging` |
| Tania Chaudhary      | Email alert system using `smtplib`         |
| Vick Panchal         | Scheduling monitoring with interval and dry-run options |

---

## 📁 Project Structure

```
assignment2/
├── assignment2.py         # Main entry point to run the project
├── Monitor.py             # Collects system metrics (CPU, memory, disk, etc.)
├── monitoralerts.py       # Checks thresholds and logs system status
├── alert.py               # Sends alert emails when problems are detected
├── scheduler.py           # Repeats checks at custom intervals
└── system_monitor.log     # Log file (auto-generated)
```

---

## ▶️ How to Run

```bash
python3 assignment2.py --interval 10 --count 3 --dry-run --verbose
```

### Arguments

| Option         | Description                                                  |
|----------------|--------------------------------------------------------------|
| `--interval`   | Time (in seconds) between each monitoring check (default: 60)|
| `--count`      | Number of checks before the script stops (default: infinite) |
| `--dry-run`    | Run without sending email alerts (for testing)               |
| `--verbose`    | Print full system status and alerts to terminal              |

---

## ✅ What This Project Does

- Collects real-time system metrics like CPU, memory, disk, network, and uptime.
- Checks against thresholds (e.g., CPU > 85%, disk usage > 90%) for alerts.
- Logs system status to `system_monitor.log`.
- Sends alerts via email when issues are detected.
- Runs continuously at a customizable interval, or for a set number of checks.
- Optionally prints real-time system status to the terminal for testing (`--verbose`).

---

## 🛠 Requirements

- Python 3.x
- Runs on Linux
- Only uses **standard Python libraries** (`psutil`, `subprocess`, `logging`, `smtplib`)

---

## 💡 Notes

- Make sure all `.py` files are in the same folder.
- Update email credentials in `alert.py` with an App Password before demoing.
- Use `Ctrl+C` to interrupt if running indefinitely.

---

## 🔁 Example Use Cases

### 🔹 Full Monitoring + Terminal Output + Email Alerts

```bash
python3 assignment2.py --interval 15 --count 5 --verbose
```

### 🔹 Test Mode (Prints status, no emails)

```bash
python3 assignment2.py --interval 10 --count 2 --dry-run --verbose
```

### 🔹 Quiet Mode (No terminal output, only logs and emails)

```bash
python3 assignment2.py --interval 20
```

