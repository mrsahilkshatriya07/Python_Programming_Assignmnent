import re
import sys
from collections import defaultdict


def extract_email_intelligence(file_path: str):
    """
    Processes a large text file to extract valid email addresses ending in .com, .edu, or .org,
    and prints domain statistics in lexicographical order.

    Expected Time Complexity: O(total characters)
    Expected Space Complexity: O(unique valid emails)
    """
    # Regex breakdown:
    # \b                       : Word boundary
    # [a-zA-0-9+._-]+          : Username with letters, digits, plus, dot, underscore, or hyphen
    # @                        : Single @ symbol
    # [a-zA-0-9.-]+\.          : Domain name (letters, digits, dots, hyphens ending with dot)
    # (?:com|edu|org)          : Top-Level Domain restricted strictly to com, edu, or org
    # \b                       : Word boundary
    email_pattern = re.compile(
        r'\b[a-zA-Z0-9+._-]+@[a-zA-Z0-9.-]+\.(?:com|edu|org)\b'
    )

    # Dictionary mapping domain -> set of unique full email addresses
    domain_data = defaultdict(set)

    try:
        # Stream file line-by-line to manage memory efficiently for files up to 1 GB
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                # Find all valid email matches in the line
                matches = email_pattern.findall(line)
                for email in matches:
                    # Extract the domain portion after '@'
                    _, domain = email.rsplit('@', 1)
                    domain_data[domain].add(email)

        # Sort domains lexicographically as required by the output format
        sorted_domains = sorted(domain_data.keys())

        # Print the output for each domain
        for domain in sorted_domains:
            emails = domain_data[domain]
            unique_user_count = len(emails)
            # Lexicographically smallest email in the set
            smallest_email = min(emails)

            print(f"{domain} {unique_user_count} {smallest_email}")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)


if __name__ == "__main__":
    # Example usage: Replace 'sample.txt' with your file path
    file_path = "sample.txt"
    extract_email_intelligence(file_path)
