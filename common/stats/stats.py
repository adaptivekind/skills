import json
import os
import re
import subprocess


class Stats:
    HISTORY_FILE = ".stats-history.json"

    @staticmethod
    def parse_token_value(value: str) -> int:
        """Parse token value like '2.2M', '228.9K', '1,234' to integer."""
        if not value:
            return 0

        value = value.replace(",", "")

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

    @staticmethod
    def parse_cost_value(value: str) -> int:
        """Parse cost value like '$5.63' to cents (int)."""
        if not value:
            return 0

        value = value.replace("$", "").strip()

        try:
            dollars = float(value)
            return int(dollars * 100)
        except ValueError:
            return 0

    @staticmethod
    def parse_stats(output: str) -> dict:
        """Parse opencode stats output into a dictionary."""
        stats = {
            "total_cost_cents": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read": 0,
            "cache_write": 0,
        }

        for line in output.split("\n"):
            line = line.replace("│", "").replace("├", "").replace("┤", "").strip()

            if not line:
                continue

            if "$" in line and "Total Cost" in line:
                match = re.search(r"\$([\d.]+)", line)
                if match:
                    stats["total_cost_cents"] = Stats.parse_cost_value(match.group(1))

            elif line.startswith("Input "):
                parts = line.split()
                if len(parts) >= 2:
                    stats["input_tokens"] = Stats.parse_token_value(parts[1])

            elif line.startswith("Output "):
                parts = line.split()
                if len(parts) >= 2:
                    stats["output_tokens"] = Stats.parse_token_value(parts[1])

            elif "Cache Read" in line:
                parts = line.split()
                if parts:
                    stats["cache_read"] = Stats.parse_token_value(parts[-1])

            elif "Cache Write" in line:
                parts = line.split()
                if parts:
                    stats["cache_write"] = Stats.parse_token_value(parts[-1])

        return stats

    @staticmethod
    def load_history() -> list:
        """Load history from JSON file."""
        if not os.path.exists(Stats.HISTORY_FILE):
            return []

        try:
            with open(Stats.HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    @staticmethod
    def save_history(history: list) -> None:
        """Save history to JSON file."""
        with open(Stats.HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)

    @staticmethod
    def get_last_stats_for_name(history: list, name: str) -> dict | None:
        """Get the most recent stats entry for a given name."""
        for entry in reversed(history):
            if entry.get("name") == name:
                return entry
        return None

    @staticmethod
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

    @staticmethod
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
