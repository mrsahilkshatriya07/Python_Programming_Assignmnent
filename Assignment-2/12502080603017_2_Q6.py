import re
import sys
from collections import defaultdict, deque


def parse_timestamp_to_minutes(ts_str: str) -> int:
    """
    Converts a timestamp string in "HH:MM" or "DD:HH:MM" format to absolute minutes.
    Assumes "HH:MM" for standard daily logs.
    """
    parts = list(map(int, ts_str.split(':')))
    if len(parts) == 2:
        hours, minutes = parts
        return hours * 60 + minutes
    elif len(parts) == 3:
        days, hours, minutes = parts
        return days * 1440 + hours * 60 + minutes
    return 0


def detect_log_anomalies(x_failures: int, t_window_minutes: int, log_lines: list):
    """
    Detects users with >= X failed logins within a T-minute sliding window followed
    by a SUCCESS login from a different IP address.

    Expected Time Complexity: O(n)
    Expected Space Complexity: O(active failures per user)
    """
    # Regex to parse timestamp, user, IP, and status from each line
    log_pattern = re.compile(
        r'^(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?)\s+'
        r'(?P<user>\S+)\s+'
        r'(?P<ip>\S+)\s+'
        r'(?P<status>FAIL|SUCCESS)$'
    )

    # Dictionary mapping user -> deque of active failures: (timestamp_in_minutes, ip)
    user_failures = defaultdict(deque)

    # Tracks detected suspicious users and the timestamp of their FIRST suspicious success
    # user -> timestamp_string
    suspicious_users = {}

    for line in log_lines:
        line = line.strip()
        if not line:
            continue

        match = log_pattern.match(line)
        if not match:
            continue

        ts_str = match.group('timestamp')
        user = match.group('user')
        ip = match.group('ip')
        status = match.group('status')

        current_time = parse_timestamp_to_minutes(ts_str)

        # 1. Slide window: Remove expired failures older than current_time - T
        failures_queue = user_failures[user]
        while failures_queue and (current_time - failures_queue[0][0] > t_window_minutes):
            failures_queue.popleft()

        # 2. Process event status
        if status == 'FAIL':
            failures_queue.append((current_time, ip))

        elif status == 'SUCCESS':
            # Check conditions if user isn't already flagged
            if user not in suspicious_users:
                # Condition 1: At least X failed attempts in current window
                if len(failures_queue) >= x_failures:
                    # Condition 2: Success must originate from a DIFFERENT IP address than the failures
                    # Check if at least one failure in the window came from a different IP
                    different_ip_found = any(fail_ip != ip for _, fail_ip in failures_queue)

                    if different_ip_found:
                        suspicious_users[user] = ts_str

    # Print detected suspicious users in lexicographical order
    for user in sorted(suspicious_users.keys()):
        print(f"{user} {suspicious_users[user]}")


if __name__ == "__main__":
    # Standard input reader handling batch execution
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        sys.exit(0)

    # Line 1: X T
    first_line = input_data[0].split()
    x_failures = int(first_line[0])
    t_window = int(first_line[1])

    # Line 2: n
    n = int(input_data[1])

    # Next n lines: Log entries
    logs = input_data[2:2 + n]

    detect_log_anomalies(x_failures, t_window, logs)
