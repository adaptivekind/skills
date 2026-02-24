#!/usr/bin/env python3
"""
cost-check.py - Parse opencode stats and track history

This script parses the opencode stats command output into JSON,
converts units (M to int, K to int, $ to cents),
and saves to a history file.

Usage: python3 cost-check.py [--name NAME]

Output: JSON with "current" and "delta" fields
"""
import os
import sys

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import argparse
import json
from datetime import datetime

from common.stats import Stats


def main():
    parser = argparse.ArgumentParser(description="Parse opencode stats")
    parser.add_argument(
        "--name",
        default="default",
        help="Name for this stats snapshot (default: default)",
    )
    args = parser.parse_args()

    # Get stats from opencode
    output = Stats.get_opencode_stats()

    if not output:
        print(json.dumps({"error": "Failed to get opencode stats"}))
        sys.exit(1)

    # Parse stats
    current_stats = Stats.parse_stats(output)

    # Add metadata
    current_entry = {
        "name": args.name,
        "timestamp": int(datetime.now().timestamp()),
        **current_stats,
    }

    # Load history
    history = Stats.load_history()

    # Get last stats for this name
    last_stats = Stats.get_last_stats_for_name(history, args.name)

    # Calculate delta
    delta = Stats.calculate_delta(current_stats, last_stats)

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
        Stats.save_history(history)

    # Output result
    result = {
        "current": current_entry,
        "delta": delta,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
