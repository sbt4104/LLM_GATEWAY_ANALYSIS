#!/usr/bin/env python3
"""
Visualize overhead_ratio_pct per session from turns.csv
"""

import csv
from collections import defaultdict
from pathlib import Path


def read_turns_csv(csv_path):
    """Read the turns CSV and aggregate overhead_ratio_pct by session"""
    session_data = defaultdict(list)

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session_id = row['session_id']
            overhead_pct = float(row['overhead_ratio_pct'])
            session_data[session_id].append(overhead_pct)

    return session_data


def calculate_session_average(session_data):
    """Calculate average overhead_ratio_pct per session"""
    session_avg = {}
    for session_id, values in session_data.items():
        session_avg[session_id] = sum(values) / len(values)
    return session_avg


def print_bar_chart(session_avg):
    """Print a text-based bar chart of overhead_ratio_pct per session"""

    # Sort sessions by ID for consistent display
    sorted_sessions = sorted(session_avg.items())

    # Find the max value for scaling
    max_value = max(session_avg.values())

    # Bar chart configuration
    max_bar_width = 60

    print("\n" + "="*80)
    print("Overhead Ratio % by Session (Average)")
    print("="*80)
    print()

    for session_id, avg_overhead in sorted_sessions:
        # Calculate bar width proportional to value
        bar_width = int((avg_overhead / max_value) * max_bar_width)
        bar = "█" * bar_width

        # Print session ID, bar, and value
        print(f"{session_id:4s} │ {bar:<{max_bar_width}} {avg_overhead:6.2f}%")

    print()
    print("="*80)
    print(f"Scale: Each █ represents ~{max_value/max_bar_width:.1f}%")
    print("="*80)
    print()


def main():
    # Locate the CSV file
    script_dir = Path(__file__).parent
    csv_path = script_dir.parent / 'analysis' / 'turns.csv'

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return

    # Read and process data
    session_data = read_turns_csv(csv_path)
    session_avg = calculate_session_average(session_data)

    # Display the chart
    print_bar_chart(session_avg)

    # Print summary statistics
    print("Session Summary:")
    print("-" * 80)
    for session_id in sorted(session_avg.keys()):
        avg = session_avg[session_id]
        turns = len(session_data[session_id])
        min_val = min(session_data[session_id])
        max_val = max(session_data[session_id])
        print(f"{session_id}: {avg:6.2f}% avg | {turns:2d} turns | "
              f"range: {min_val:6.2f}% - {max_val:6.2f}%")
    print("-" * 80)


if __name__ == "__main__":
    main()
