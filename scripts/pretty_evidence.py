#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def format_event(event):
    event_type = event.get('event_type', 'unknown').upper()
    timestamp = event.get('timestamp', '')
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        time_str = timestamp

    metric = event.get('metric', '')
    value = event.get('value', '')
    context = event.get('context', '')
    notes = event.get('notes', '')
    artifact_ref = event.get('artifact_ref', '')

    lines = [f"[{time_str}] {event_type}"]
    if metric or value:
        lines.append(f"  Metric: {metric} = {value}")
    if context:
        lines.append(f"  Context: {context}")
    if notes:
        lines.append(f"  Notes: {notes}")
    if artifact_ref:
        lines.append(f"  Artifact Ref: {artifact_ref}")

    return "\n".join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python pretty_evidence.py <path_to_evidence.jsonl>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    print(format_event(event))
                    print("-" * 40)
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON: {line}")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        sys.exit(1)

if __name__ == "__main__":
    main()
