#!/usr/bin/env python3
# Thomas Chan, Tania Chaudhary & Vick Panchal, Vishwanand Doobay
# OPS 445 Assignment 2
# Date Created: 2025/08/04 – Updated: 2025/08/06
# Lab: Metric Collection + Alerting System with Scheduler

import argparse
import json
import subprocess
import time
import datetime
import psutil
import logging
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==== Email Configuration ====
SMTP_SERVER      = 'smtp.gmail.com'
SMTP_PORT        = 587
SENDER_EMAIL     = 'partilos9669@gmail.com'   # Updated sender email
SENDER_PASSWORD  = 'Partilos999'              # Updated sender password
RECIPIENT_EMAIL  = 'tchan73@myseneca.ca'      # Updated recipient email

# Configure logging
logging.basicConfig(
    filename='system_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Default thresholds
THRESHOLDS = {
    'cpu_percent':       85.0,  # CPU usage threshold (%)
    'memory_used_ratio':  0.90, # Memory used threshold (90%)
    'disk_used_ratio':    0.90  # Disk usage threshold (90%)
}


def run_diagnostics():
    # Define and execute system diagnostic commands
    commands = {
        'uname':      ['uname', '-a'],         # Kernel & OS info
        'disk_usage': ['df', '-h'],            # Disk usage in human-readable form
        'net_routes': ['ip', 'route', 'show'], # Kernel IP routing table
    }
    results = {}
    for name, cmd in commands.items():
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True)
            output = completed.stdout.strip() or completed.stderr.strip()
        except Exception as e:
            output = f"Error running {name}: {e}"
        results[name] = output.splitlines()
    return results


def collect_metrics():
    # Gather metrics: timestamp, CPU, memory, disk, network I/O, uptime, diagnostics
    timestamp = datetime.datetime.now().isoformat()
    cpu_pct   = psutil.cpu_percent(interval=None)
    vm        = psutil.virtual_memory()
    memory    = {'used': vm.used, 'available': vm.available}

    disk = {}
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        disk[part.mountpoint] = {
            'total':   usage.total,
            'used':    usage.used,
            'free':    usage.free,
            'percent': usage.percent
        }

    net_io      = psutil.net_io_counters()._asdict()
    uptime      = time.time() - psutil.boot_time()
    diagnostics = run_diagnostics()

    return {
        'timestamp':      timestamp,
        'cpu_percent':    cpu_pct,
        'memory':         memory,
        'disk':           disk,
        'network_io':     net_io,
        'uptime_seconds': uptime,
        'diagnostics':    diagnostics,
    }


def check_thresholds(metrics):
    """Check metrics against thresholds; return (alerts, details)."""
    alerts = []
    details = []

    # CPU
    cpu = metrics['cpu_percent']
    details.append(f"CPU Usage: {cpu:.2f}%")
    if cpu > THRESHOLDS['cpu_percent']:
        alerts.append(f"High CPU usage: {cpu:.2f}%")

    # Memory
    used  = metrics['memory']['used']
    avail = metrics['memory']['available']
    total = used + avail
    mem_ratio = used / total if total else 0
    mem_pct   = mem_ratio * 100
    details.append(
        f"Memory Usage: {mem_pct:.2f}% "
        f"({used/(1024**2):.1f}MB used / {total/(1024**2):.1f}MB total)"
    )
    if mem_ratio > THRESHOLDS['memory_used_ratio']:
        alerts.append(f"High memory usage: {mem_pct:.2f}%")

    # Disk
    for mount, info in metrics['disk'].items():
        pct = info['percent']
        details.append(
            f"Disk Usage on {mount}: {pct:.2f}% "
            f"(Used: {info['used']/(1024**3):.2f}GB / Total: {info['total']/(1024**3):.2f}GB)"
        )
        if pct > THRESHOLDS['disk_used_ratio'] * 100:
            alerts.append(f"High disk usage on {mount}: {pct:.2f}%")

    return alerts, details


def send_email_alert(alerts, timestamp):
    """Send an email alert with the given alert messages."""
    hostname = socket.gethostname()
    subject  = f"System Alert from {hostname}"
    body = (
        f"System Alert Detected at {timestamp}\n\n"
        f"Host: {hostname}\n\n"
        "The following issues were detected:\n"
        + "\n".join(f"- {a}" for a in alerts)
        + "\n\nPlease check the system.\n"
    )

    msg = MIMEMultipart()
    msg['From']    = SENDER_EMAIL
    msg['To']      = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[INFO] Alert email sent to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"[ERROR] Failed to send alert email: {e}")


def main(interval=60, count=None, dry_run=False, verbose=False):
    i = 0  # Track how many checks have been done

    try:
        while True:
            print(f"\n[INFO] Running system check #{i+1}")
            metrics = collect_metrics()            # Collect latest system metrics
            alerts, details = check_thresholds(metrics)  # Compare metrics to thresholds

            # Show full system status only if verbose is enabled
            if verbose:
                print("==== System Status ====")
                for line in details:
                    print("INFO:", line)
                if alerts:
                    for alert in alerts:
                        print("ALERT:", alert)
                else:
                    print("INFO: All systems within normal thresholds.")

            # Send email alert if needed and not a dry run
            if alerts and not dry_run:
                send_email_alert(alerts, metrics['timestamp'])

            i += 1
            if count and i >= count:
                break

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[INFO] Monitoring loop interrupted by user.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Schedule system monitoring checks at custom intervals.'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=60,
        help='Interval in seconds between each monitoring check (default: 60)'
    )
    parser.add_argument(
        '--count', '-c',
        type=int,
        help='Number of monitoring checks to run (default: infinite)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run checks but do not send email alerts (for testing)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print full system status output (for testing)'
    )

    args = parser.parse_args()
    main(
        interval=args.interval,
        count=args.count,
        dry_run=args.dry_run,
        verbose=args.verbose
    )
