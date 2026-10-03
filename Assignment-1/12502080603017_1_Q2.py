"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 2
Topic: Optimized Password Audit with Pattern Constraints
CO Mapping: CO-1, CO-3
Bloom Level: L5 (Evaluate)

Description:
    Classifies n candidate passwords based on strict security constraints:
    1. WEAK_LENGTH: Length is strictly outside the range [6, 12].
    2. COMPROMISED: Contains any banned dictionary word as a contiguous substring (case-insensitive).
       - Evaluated in linear time using the Aho-Corasick string matching algorithm.
    3. WEAK_PATTERN: Fails character diversity checks (lowercase, uppercase, digit, special symbol [$#@])
       OR contains the same character repeated more than 3 times consecutively (>= 4 times).
    4. STRONG: Meets all length, dictionary, character set, and repetition requirements.
"""

from collections import deque
import re
import sys


class AhoCorasick:
    """
    Aho-Corasick Automaton for multi-pattern substring matching in O(N + M) time.
    """

    def __init__(self):
        # trie node structure: list of dicts mapping char -> child_node_id
        self.trie = [{}]
        self.output = [False]  # True if a node terminates a banned pattern
        self.fail = [0]        # Failure links for fallback during traversal

    def insert(self, pattern: str) -> None:
        """Inserts a lowercase pattern into the Trie."""
        current_node = 0
        for char in pattern:
            if char not in self.trie[current_node]:
                new_node_id = len(self.trie)
                self.trie[current_node][char] = new_node_id
                self.trie.append({})
                self.output.append(False)
                self.fail.append(0)
            current_node = self.trie[current_node][char]
        self.output[current_node] = True  # Mark end of pattern

    def build_failure_links(self) -> None:
        """Constructs failure links and output propagation using BFS."""
        queue = deque()

        # Step 1: Initialize depth-1 children failure links to root (0)
        for char, child_id in self.trie[0].items():
            self.fail[child_id] = 0
            queue.append(child_id)

        # Step 2: BFS for deeper nodes
        while queue:
            current_node = queue.popleft()

            # Propagate output status from failure link
            if self.output[self.fail[current_node]]:
                self.output[current_node] = True

            for char, child_id in self.trie[current_node].items():
                # Find failure state for child
                fallback = self.fail[current_node]
                while fallback > 0 and char not in self.trie[fallback]:
                    fallback = self.fail[fallback]

                if char in self.trie[fallback]:
                    self.fail[child_id] = self.trie[fallback][char]
                else:
                    self.fail[child_id] = 0

                # Inherit output flag from failure target
                if self.output[self.fail[child_id]]:
                    self.output[child_id] = True

                queue.append(child_id)

    def contains_any_pattern(self, text: str) -> bool:
        """
        Searches string text (converted to lowercase) for any registered banned pattern.
        
        Returns:
            bool: True if any banned pattern exists as a substring, False otherwise.
        """
        current_node = 0
        for char in text.lower():
            while current_node > 0 and char not in self.trie[current_node]:
                current_node = self.fail[current_node]

            if char in self.trie[current_node]:
                current_node = self.trie[current_node][char]

            if self.output[current_node]:
                return True

        return False


def classify_password(password: str, aho_corasick: AhoCorasick) -> str:
    """
    Evaluates a candidate password against audit rules in priority order.
    
    Priority Rules:
        1. WEAK_LENGTH: If len < 6 or len > 12.
        2. COMPROMISED: If it contains any banned dictionary word as a substring.
        3. WEAK_PATTERN: If missing character diversity OR has >3 consecutive repeated characters.
        4. STRONG: Meets all conditions.
    """
    # Rule 1: Length Check
    if len(password) < 6 or len(password) > 12:
        return "WEAK_LENGTH"

    # Rule 2: Dictionary Word Substring Check (COMPROMISED)
    if aho_corasick.contains_any_pattern(password):
        return "COMPROMISED"

    # Rule 3: Character Set Diversity Check
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[$#@]', password))

    if not (has_lower and has_upper and has_digit and has_special):
        return "WEAK_PATTERN"

    # Rule 4: Consecutive Character Repetition Check (No char repeated > 3 times consecutively)
    if re.search(r'(.)\1{3,}', password):
        return "WEAK_PATTERN"

    return "STRONG"


def main():
    """Main execution block handling stream input and password auditing."""
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    iterator = iter(input_data)

    try:
        # Read Banned Words
        num_banned = int(next(iterator).strip())
        ac_automaton = AhoCorasick()

        for _ in range(num_banned):
            banned_word = next(iterator).strip().lower()
            if banned_word:
                ac_automaton.insert(banned_word)

        ac_automaton.build_failure_links()

        # Read Passwords
        num_passwords = int(next(iterator).strip())

        for index in range(1, num_passwords + 1):
            password = next(iterator).rstrip('\r\n')
            result = classify_password(password, ac_automaton)
            print(f"{index}: {result}")

    except StopIteration:
        pass


if __name__ == "__main__":
    main()
