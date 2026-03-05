#!/usr/bin/env python3
"""
Calculate consumption ratios from Claude Code usage logs.

This script analyzes /tmp/claude-usage-log.csv to determine:
  1. How much 5h utilization is consumed per 1% of 7d utilization.
  2. How much sonnet-weekly utilization is consumed per 1% of 7d
     utilization during sonnet-active intervals only.

Usage:
    python3 calc_usage_ratio.py [--log-file PATH]

Output:
    Per-transition breakdown for 5h/7d ratio, interval-based sonnet/7d
    ratio, plus overall ratios for both.
"""

import argparse
import os

DEFAULT_LOG_FILE = "/tmp/claude-usage-log.csv"


def parse_log_file(log_path: str) -> list[tuple[int, int, int, int | None]]:
    """Parse the usage log CSV into a list of (timestamp, 5h%, 7d%, sonnet%) tuples.

    The sonnet% column is optional for backward compatibility with older logs.
    """
    data = []
    with open(log_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) >= 3 and parts[1] and parts[2]:
                try:
                    ts = int(parts[0])
                    h5 = int(parts[1])
                    d7 = int(parts[2])
                    sonnet = int(parts[3]) if len(parts) >= 4 and parts[3] else None
                    data.append((ts, h5, d7, sonnet))
                except ValueError:
                    continue
    return data


def calculate_h5_ratio(data: list[tuple[int, int, int, int | None]]) -> dict:
    """
    Calculate the 5h/7d consumption ratio.

    For each 7d transition (e.g., 11→12), calculates the total 5h climb
    that occurred during that 7d level, accounting for 5h resets.
    """
    if len(data) < 2:
        return {}

    transitions = {}  # (from_7d, to_7d) -> total_5h_climb

    current_7d = data[0][2]
    total_climb_this_level = 0
    prev_h5 = data[0][1]

    for i in range(1, len(data)):
        ts, h5, d7, _sonnet = data[i]

        if d7 != current_7d:
            # 7d transitioned - record the climb for the level we just left
            key = (current_7d, d7)
            if key not in transitions:
                transitions[key] = 0
            transitions[key] += total_climb_this_level

            # Include any climb at the transition itself
            if h5 > prev_h5:
                transitions[key] += (h5 - prev_h5)

            # Reset for new level
            current_7d = d7
            total_climb_this_level = 0
        else:
            # Same level - track climb
            delta = h5 - prev_h5
            if delta > 0:
                total_climb_this_level += delta
            # Reset detection: delta < -5 indicates 5h reset (ignored for climb)

        prev_h5 = h5

    return transitions


def calculate_sonnet_ratio(data: list[tuple[int, int, int, int | None]]) -> dict | None:
    """
    Calculate the sonnet/7d consumption ratio using interval-based filtering.

    Only counts intervals where sonnet% actually increased (i.e., sonnet was
    used). For those intervals, accumulates both sonnet% climb and 7d% climb
    to produce a ratio of sonnet burn per 7d burn during sonnet-active usage.

    Returns None if no sonnet data is available.
    """
    # Check if any sonnet data exists
    has_sonnet = any(row[3] is not None for row in data)
    if not has_sonnet or len(data) < 2:
        return None

    total_sonnet_climb = 0
    total_7d_climb_during_sonnet = 0
    sonnet_intervals = 0

    for i in range(1, len(data)):
        prev_sonnet = data[i - 1][3]
        curr_sonnet = data[i][3]
        prev_d7 = data[i - 1][2]
        curr_d7 = data[i][2]

        if prev_sonnet is None or curr_sonnet is None:
            continue

        sonnet_delta = curr_sonnet - prev_sonnet
        d7_delta = curr_d7 - prev_d7

        # Skip resets (large negative drops)
        if sonnet_delta < -5:
            continue

        # Only count intervals where sonnet was actually used
        if sonnet_delta > 0:
            total_sonnet_climb += sonnet_delta
            if d7_delta > 0:
                total_7d_climb_during_sonnet += d7_delta
            sonnet_intervals += 1

    return {
        "total_sonnet_climb": total_sonnet_climb,
        "total_7d_climb": total_7d_climb_during_sonnet,
        "intervals": sonnet_intervals,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate 5h/7d consumption ratio from usage logs"
    )
    parser.add_argument(
        "--log-file",
        default=DEFAULT_LOG_FILE,
        help=f"Path to usage log CSV (default: {DEFAULT_LOG_FILE})"
    )
    args = parser.parse_args()

    if not os.path.exists(args.log_file):
        print(f"Error: Log file not found: {args.log_file}")
        return 1

    data = parse_log_file(args.log_file)

    if len(data) < 2:
        print("Error: Insufficient data points in log file")
        return 1

    # --- 5h/7d ratio ---
    transitions = calculate_h5_ratio(data)

    if transitions:
        print("=== 5h Climb Per 7d Unit Transition ===\n")
        print(f"{'Transition':<15} {'5h climb':<12}")
        print("-" * 30)

        total = 0
        for (from_7d, to_7d), climb in sorted(transitions.items()):
            print(f"{from_7d}% → {to_7d}%{'':<6} {climb:<12}")
            total += climb

        num_transitions = len(transitions)
        print("-" * 30)
        print(f"\nTotal transitions: {num_transitions}")
        print(f"Total 5h climb: {total}")

        if num_transitions > 0:
            ratio = total / num_transitions
            print(f"\n*** 5h RATIO: {total}/{num_transitions} = {ratio:.2f} 5h% per 1% 7d ***")
            print(f"\nInterpretation: For every 1% of 7d consumed, ~{ratio:.1f}% of 5h is consumed.")
    else:
        print("No 7d transitions found for 5h ratio calculation.")

    # --- Sonnet/7d ratio ---
    sonnet = calculate_sonnet_ratio(data)

    if sonnet is None:
        print("\n(No sonnet% data in log file — skipping sonnet ratio)")
    elif sonnet["intervals"] == 0:
        print("\n(No sonnet-active intervals detected — skipping sonnet ratio)")
    else:
        print(f"\n\n=== Sonnet/7d Ratio (sonnet-active intervals only) ===\n")
        print(f"Sonnet-active intervals:  {sonnet['intervals']}")
        print(f"Total sonnet% climb:      {sonnet['total_sonnet_climb']}")
        print(f"Total 7d% climb (sonnet): {sonnet['total_7d_climb']}")

        if sonnet["total_7d_climb"] > 0:
            s_ratio = sonnet["total_sonnet_climb"] / sonnet["total_7d_climb"]
            print(f"\n*** SONNET RATIO: {sonnet['total_sonnet_climb']}/{sonnet['total_7d_climb']} = {s_ratio:.2f} sonnet% per 1% 7d ***")
            print(f"\nInterpretation: For every 1% of 7d consumed via sonnet, ~{s_ratio:.1f}% of sonnet weekly is consumed.")
        else:
            print(f"\n*** SONNET RATIO: {sonnet['total_sonnet_climb']} sonnet% climb across {sonnet['intervals']} intervals (no 7d movement) ***")

    return 0


if __name__ == "__main__":
    exit(main())
