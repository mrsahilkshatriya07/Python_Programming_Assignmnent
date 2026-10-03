"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 4
Topic: Exception-Safe CSV Transaction Splitter
CO Mapping: CO-1, CO-4
Bloom Level: L5 (Evaluate)

Description:
    Processes financial transaction CSV data with fault-tolerant exception handling:
    1. Validates each row (transaction_id, account_id, type [CREDIT/DEBIT], positive numeric amount, ISO timestamp).
    2. Writes valid transactions into 'credit.csv' or 'debit.csv'.
    3. Captures malformed/invalid rows into 'error.csv' alongside the explicit rejection reason.
    4. Computes net balances per account and prints account-wise net balance changes
       sorted in descending order of absolute balance change.
"""

from collections import defaultdict
import csv
from datetime import datetime
import sys


def validate_row(row: dict) -> tuple[str, str, str, float, str]:
    """
    Validates CSV transaction row fields.

    Args:
        row: Dictionary mapping field names to raw string values.

    Returns:
        tuple: (tid, acc, tx_type, amount_val, timestamp_str)

    Raises:
        ValueError: If any validation condition fails.
    """
    # 1. Check required fields presence
    required_fields = ['tid', 'acc', 'type', 'amount', 'time']
    for field in required_fields:
        if field not in row or not row[field].strip():
            raise ValueError(f"Missing or empty required field: '{field}'")

    tid = row['tid'].strip()
    acc = row['acc'].strip()
    tx_type = row['type'].strip().upper()
    amount_str = row['amount'].strip()
    timestamp_str = row['time'].strip()

    # 2. Validate Transaction Type
    if tx_type not in ('CREDIT', 'DEBIT'):
        raise ValueError(f"Invalid transaction type '{tx_type}'. Must be CREDIT or DEBIT")

    # 3. Validate Numeric Amount (> 0)
    try:
        amount_val = float(amount_str)
    except ValueError:
        raise ValueError(f"Amount '{amount_str}' is not a valid number")

    if amount_val <= 0:
        raise ValueError(f"Amount must be strictly positive (> 0), got {amount_val}")

    # 4. Validate ISO Timestamp format (yyyy-mm-ddThh:mm:ss)
    try:
        datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError(f"Invalid ISO timestamp format '{timestamp_str}'. Expected 'YYYY-MM-DDThh:mm:ss'")

    return tid, acc, tx_type, amount_val, timestamp_str


def process_transactions(input_filepath: str):
    """
    Reads input CSV file row by row, routes rows to credit/debit/error files,
    and calculates net account balances.
    """
    account_balances = defaultdict(float)

    fieldnames = ['tid', 'acc', 'type', 'amount', 'time']
    error_fieldnames = fieldnames + ['reason']

    try:
        with open(input_filepath, mode='r', encoding='utf-8', newline='') as infile, \
             open('credit.csv', mode='w', encoding='utf-8', newline='') as credit_file, \
             open('debit.csv', mode='w', encoding='utf-8', newline='') as debit_file, \
             open('error.csv', mode='w', encoding='utf-8', newline='') as error_file:

            reader = csv.DictReader(infile)
            
            credit_writer = csv.DictWriter(credit_file, fieldnames=fieldnames)
            debit_writer = csv.DictWriter(debit_file, fieldnames=fieldnames)
            error_writer = csv.DictWriter(error_file, fieldnames=error_fieldnames)

            # Write headers
            credit_writer.writeheader()
            debit_writer.writeheader()
            error_writer.writeheader()

            for line_no, raw_row in enumerate(reader, start=2):
                try:
                    tid, acc, tx_type, amount_val, timestamp_str = validate_row(raw_row)

                    cleaned_row = {
                        'tid': tid,
                        'acc': acc,
                        'type': tx_type,
                        'amount': f"{amount_val:g}",
                        'time': timestamp_str
                    }

                    # Route to appropriate output stream
                    if tx_type == 'CREDIT':
                        credit_writer.writerow(cleaned_row)
                        account_balances[acc] += amount_val
                    else:  # DEBIT
                        debit_writer.writerow(cleaned_row)
                        account_balances[acc] -= amount_val

                except Exception as err:
                    # Fault-tolerant exception capture
                    err_row = dict(raw_row)
                    err_row['reason'] = str(err)
                    error_writer.writerow(err_row)

    except FileNotFoundError:
        print(f"Error: Input file '{input_filepath}' not found.", file=sys.stderr)
        return
    except Exception as e:
        print(f"File Processing Error: {e}", file=sys.stderr)
        return

    # Print Console Summary
    # Sort accounts by absolute balance change descending; tie-break by account ID ascending
    sorted_accounts = sorted(
        account_balances.items(),
        key=lambda item: (-abs(item[1]), item[0])
    )

    for acc, net_change in sorted_accounts:
        # Format balance: display integers clean or floats with proper precision
        formatted_val = int(net_change) if net_change.is_integer() else round(net_change, 2)
        print(f"{acc} {formatted_val}")


def main():
    """Main entry point reading input file path from arguments or standard input."""
    if len(sys.argv) > 1:
        input_filepath = sys.argv[1]
    else:
        input_filepath = input().strip()

    if input_filepath:
        process_transactions(input_filepath)


if __name__ == "__main__":
    main()
