#!/usr/bin/env python3
"""
cost-check.py - Parse opencode stats and track history

This script parses the opencode stats command output into JSON,
converts units (M to int, K to int, $ to cents),
and saves to a history file.

Usage: python3 cost-check.py [--name NAME]

Output: JSON with "current" and "delta" fields
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime

HISTORY_FILE = ".stats-history.json"


def parse_token_value(value: str) -> int:
    """Parse token value like '2.2M', '228.9K', '1,234' to integer."""
    if not value:
        return 0

    # Remove commas
    value = value.replace(",", "")

    # Check for M (million) or K (thousand) suffix
    multiplier = 1
    if value.endswith("M"):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.endswith("K"):
        multiplier = 1_000
        value = value[:-1]

    try:
        return int(float(value) * multiplier)
    except ValueError:
        return 0


def parse_cost_value(value: str) -> int:
    """Parse cost value like '$5.63' to cents (int)."""
    if not value:
        return 0

    # Remove $ and convert to cents
    value = value.replace("$", "").strip()

    try:
        dollars = float(value)
        return int(dollars * 100)
    except ValueError:
        return 0


def parse_stats(output: str) -> dict:
    """Parse opencode stats output into a dictionary."""
    stats = {
        "total_cost_cents": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read": 0,
        "cache_write": 0,
    }

    # Parse each line - look for patterns in the table
    for line in output.split("\n"):
        # Remove table borders and whitespace
        line = line.replace("│", "").replace("├", "").replace("┤", "").strip()

        if not line:
            continue

        # Total Cost - look for $ sign
        if "$" in line and "Total Cost" in line:
            match = re.search(r"\$([\d.]+)", line)
            if match:
                stats["total_cost_cents"] = parse_cost_value(match.group(1))

        # Input tokens - look for line starting with Input (after pipe chars removed)
        elif line.startswith("Input "):
            parts = line.split()
            if len(parts) >= 2:
                stats["input_tokens"] = parse_token_value(parts[1])

        # Output tokens
        elif line.startswith("Output "):
            parts = line.split()
            if len(parts) >= 2:
                stats["output_tokens"] = parse_token_value(parts[1])

        # Cache Read
        elif "Cache Read" in line:
            parts = line.split()
            # Last part is the value
            if parts:
                stats["cache_read"] = parse_token_value(parts[-1])

        # Cache Write
        elif "Cache Write" in line:
            parts = line.split()
            if parts:
                stats["cache_write"] = parse_token_value(parts[-1])

    return stats


def load_history() -> list:
    """Load history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list) -> None:
    """Save history to JSON file."""
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def get_last_stats_for_name(history: list, name: str) -> dict | None:
    """Get the most recent stats entry for a given name."""
    for entry in reversed(history):
        if entry.get("name") == name:
            return entry
    return None


def calculate_delta(current: dict, last: dict | None) -> dict:
    """Calculate delta between current and last stats."""
    if last is None:
        return {
            "total_cost_cents": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read": 0,
            "cache_write": 0,
        }

    return {
        "total_cost_cents": current["total_cost_cents"]
        - last.get("total_cost_cents", 0),
        "input_tokens": current["input_tokens"] - last.get("input_tokens", 0),
        "output_tokens": current["output_tokens"] - last.get("output_tokens", 0),
        "cache_read": current["cache_read"] - last.get("cache_read", 0),
        "cache_write": current["cache_write"] - last.get("cache_write", 0),
    }


def get_opencode_stats() -> str:
    """Get stats from opencode command."""
    try:
        result = subprocess.run(
            ["opencode", "stats"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout
    except FileNotFoundError:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Parse opencode stats")
    parser.add_argument(
        "--name",
        default="default",
        help="Name for this stats snapshot (default: default)",
    )
    args = parser.parse_args()

    # Get stats from opencode
    output = get_opencode_stats()

    if not output:
        print(json.dumps({"error": "Failed to get opencode stats"}))
        sys.exit(1)

    # Parse stats
    current_stats = parse_stats(output)

    # Add metadata
    current_entry = {
        "name": args.name,
        "timestamp": int(datetime.now().timestamp()),
        **current_stats,
    }

    # Load history
    history = load_history()

    # Get last stats for this name
    last_stats = get_last_stats_for_name(history, args.name)

    # Calculate delta
    delta = calculate_delta(current_stats, last_stats)

    # Check if stats changed - only save if different from last
    should_save = True
    if last_stats is not None:
        # Compare only the stats fields (not name/timestamp)
        current_compare = {
            "total_cost_cents": current_stats.get("total_cost_cents", 0),
            "input_tokens": current_stats.get("input_tokens", 0),
            "output_tokens": current_stats.get("output_tokens", 0),
            "cache_read": current_stats.get("cache_read", 0),
            "cache_write": current_stats.get("cache_write", 0),
        }
        last_compare = {
            "total_cost_cents": last_stats.get("total_cost_cents", 0),
            "input_tokens": last_stats.get("input_tokens", 0),
            "output_tokens": last_stats.get("output_tokens", 0),
            "cache_read": last_stats.get("cache_read", 0),
            "cache_write": last_stats.get("cache_write", 0),
        }
        if current_compare == last_compare:
            should_save = False

    # Save to history only if changed
    if should_save:
        history.append(current_entry)
        save_history(history)

    # Output result
    result = {
        "current": current_entry,
        "delta": delta,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
