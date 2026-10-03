"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 8
Topic: Compressed Log Index using Pickle and Zip
CO Mapping: CO-1, CO-4
Bloom Level: L6 (Create)

Description:
    Implements a two-mode log indexing system:
    1. BUILD Mode: Scans all log files in a given directory, normalizes tokens,
       constructs an inverted index (token -> list of "filename:linenumber"),
       serializes the index via `pickle`, and archives all original logs alongside
       the index file into a compressed ZIP archive.
    2. SEARCH Mode: Loads the pickled inverted index (from a path or direct memory)
       and performs ultra-fast lookup queries for specific tokens.
"""

import os
import pickle
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path


class LogIndexEngine:
    """Handles inverted index generation, serialization, and searching."""

    # Regex token boundary matcher (matches alphanumeric words)
    TOKEN_REGEX = re.compile(r'\b[a-zA-Z0-9_]+\b')

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        """Normalizes and extracts tokens from a line of text."""
        return cls.TOKEN_REGEX.findall(text.lower())

    @classmethod
    def build_index(cls, folder_path: str, zip_output_name: str) -> tuple[int, int, int]:
        """
        Scans all files in folder_path, builds an inverted index, saves index.pkl,
        and packages log files + index.pkl into zip_output_name.

        Returns:
            Tuple of (total_files, total_lines, unique_tokens)
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            raise FileNotFoundError(f"Directory not found: {folder_path}")

        # Inverted index structure: { token: ["filename:line_num", ...] }
        inverted_index: dict[str, list[str]] = defaultdict(list)
        
        total_files = 0
        total_lines = 0

        # Collect log files (sorting guarantees deterministic processing order)
        log_files = sorted([f for f in folder.iterdir() if f.is_file() and f.name != zip_output_name])

        for file_path in log_files:
            total_files += 1
            rel_filename = file_path.name

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_number, line in enumerate(f, start=1):
                        total_lines += 1
                        tokens = cls.tokenize(line)
                        posting = f"{rel_filename}:{line_number}"
                        
                        # Add posting for unique tokens in this line to prevent duplicates
                        for token in set(tokens):
                            inverted_index[token].append(posting)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}", file=sys.stderr)

        # Serialize inverted index using pickle
        pickle_filename = "index.pkl"
        with open(pickle_filename, 'wb') as pkl_file:
            pickle.dump(dict(inverted_index), pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

        # Compress all original logs and the serialized index into a ZIP file
        with zipfile.ZipFile(zip_output_name, 'w', compression=zipfile.ZIP_DEFLATED) as zip_file:
            # Add log files
            for file_path in log_files:
                zip_file.write(file_path, arcname=file_path.name)
            # Add serialized index
            zip_file.write(pickle_filename, arcname=pickle_filename)

        # Clean up temporary standalone index file after zip creation
        if os.path.exists(pickle_filename):
            os.remove(pickle_filename)

        unique_tokens = len(inverted_index)
        return total_files, total_lines, unique_tokens

    @classmethod
    def search_index(cls, pickle_source: str, query_tokens: list[str]):
        """
        Loads the pickled index and queries postings for each token.
        Supports both standalone .pkl files and index.pkl inside a .zip file.
        """
        index_data: dict[str, list[str]] = {}

        # Handle direct ZIP or PKL source path
        if pickle_source.endswith('.zip') and zipfile.is_zipfile(pickle_source):
            with zipfile.ZipFile(pickle_source, 'r') as zf:
                if 'index.pkl' in zf.namelist():
                    with zf.open('index.pkl', 'r') as pkl_file:
                        index_data = pickle.load(pkl_file)
                else:
                    raise KeyError("index.pkl not found inside ZIP archive.")
        else:
            with open(pickle_source, 'rb') as pkl_file:
                index_data = pickle.load(pkl_file)

        # Process lookup queries
        for q in query_tokens:
            q_norm = q.lower()
            matches = index_data.get(q_norm, [])
            if matches:
                print(f"{q_norm}: " + " ".join(matches))
            else:
                print(f"{q_norm}: NO MATCHES")


def main():
    """Main execution block supporting stream and argument-based execution."""
    input_lines = sys.stdin.read().splitlines()
    if not input_lines:
        return

    for line in input_lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        parts = cleaned_line.split()
        mode = parts[0].upper()

        if mode == "BUILD":
            if len(parts) >= 3:
                folder_path = parts[1]
                zip_name = parts[2]
                try:
                    files_cnt, lines_cnt, tokens_cnt = LogIndexEngine.build_index(folder_path, zip_name)
                    print(f"FILES {files_cnt}")
                    print(f"LINES {lines_cnt}")
                    print(f"TOKENS {tokens_cnt}")
                except Exception as e:
                    print(f"BUILD ERROR: {e}")

        elif mode == "SEARCH":
            if len(parts) >= 3:
                pickle_path = parts[1]
                queries = parts[2:]
                try:
                    LogIndexEngine.search_index(pickle_path, queries)
                except Exception as e:
                    print(f"SEARCH ERROR: {e}")


if __name__ == "__main__":
    main()
