"""
Course Code: 202044504
Course Title: Programming with Python
Assignment: 1 | Question: 5
Topic: Object-Oriented Bank Settlement System
CO Mapping: CO-1, CO-2
Bloom Level: L6 (Create)

Description:
    Object-Oriented Bank Settlement Engine with atomic batch processing and rollback logic.
    - Encapsulated classes: Account, Transaction, and Bank.
    - Transaction Types: DEPOSIT, WITHDRAW, TRANSFER.
    - Custom Exceptions: InsufficientFundsException, AccountNotFoundException, TransactionException.
    - Atomic Batches: Groups transactions between BATCH_BEGIN and BATCH_END.
      If any operation in a batch fails, all operations in that batch are rolled back.
"""

import sys


class BankException(Exception):
    """Base exception for banking engine operations."""
    pass


class AccountNotFoundException(BankException):
    """Raised when an requested account ID does not exist."""
    pass


class InsufficientFundsException(BankException):
    """Raised when an account balance is insufficient for a withdrawal or transfer."""
    pass


class InvalidTransactionException(BankException):
    """Raised when a transaction payload contains invalid data."""
    pass


class Account:
    """
    Represents a bank account with encapsulated state management.
    """
    def __init__(self, account_id: str, initial_balance: int):
        self._account_id = account_id
        if initial_balance < 0:
            raise InvalidTransactionException("Initial balance cannot be negative.")
        self._balance = initial_balance

    @property
    def account_id(self) -> str:
        return self._account_id

    @property
    def balance(self) -> int:
        return self._balance

    def deposit(self, amount: int) -> None:
        """Adds funds to account."""
        if amount <= 0:
            raise InvalidTransactionException("Deposit amount must be positive.")
        self._balance += amount

    def withdraw(self, amount: int) -> None:
        """Subtracts funds from account if sufficient funds exist."""
        if amount <= 0:
            raise InvalidTransactionException("Withdrawal amount must be positive.")
        if self._balance < amount:
            raise InsufficientFundsException(
                f"Account {self._account_id} insufficient balance: {self._balance} < {amount}"
            )
        self._balance -= amount

    def snapshot(self) -> int:
        """Returns the current balance state for transaction logging/rollbacks."""
        return self._balance

    def restore(self, balance_state: int) -> None:
        """Restores balance from snapshot state."""
        self._balance = balance_state


class Transaction:
    """
    Represents a single atomic operation record.
    """
    def __init__(self, tx_type: str, account_id: str, amount: int, target_account_id: str = None):
        self.tx_type = tx_type
        self.account_id = account_id
        self.amount = amount
        self.target_account_id = target_account_id


class Bank:
    """
    Central Settlement Engine managing accounts, transaction executions, and batch rollbacks.
    """
    def __init__(self):
        self.accounts: dict[str, Account] = {}
        self.history: list[Transaction] = []
        
        # Batch tracking states
        self.in_batch = False
        self.current_batch_id = 0
        self.current_batch_ops: list[dict] = []
        self.failed_batches: list[int] = []

    def create_account(self, account_id: str, initial_balance: int) -> None:
        """Registers a new account in the system."""
        self.accounts[account_id] = Account(account_id, initial_balance)

    def get_account(self, account_id: str) -> Account:
        """Retrieves an account object or raises AccountNotFoundException."""
        if account_id not in self.accounts:
            raise AccountNotFoundException(f"Account '{account_id}' does not exist.")
        return self.accounts[account_id]

    def _execute_deposit(self, acc_id: str, amount: int) -> None:
        acc = self.get_account(acc_id)
        
        # Save snapshot for rollback if inside an active batch
        if self.in_batch:
            self.current_batch_ops.append({
                'type': 'DEPOSIT',
                'acc_id': acc_id,
                'prev_balance': acc.snapshot()
            })
            
        acc.deposit(amount)

    def _execute_withdraw(self, acc_id: str, amount: int) -> None:
        acc = self.get_account(acc_id)
        
        if self.in_batch:
            self.current_batch_ops.append({
                'type': 'WITHDRAW',
                'acc_id': acc_id,
                'prev_balance': acc.snapshot()
            })
            
        acc.withdraw(amount)

    def _execute_transfer(self, src_acc_id: str, dest_acc_id: str, amount: int) -> None:
        src_acc = self.get_account(src_acc_id)
        dest_acc = self.get_account(dest_acc_id)
        
        if self.in_batch:
            self.current_batch_ops.append({
                'type': 'TRANSFER',
                'src_acc_id': src_acc_id,
                'dest_acc_id': dest_acc_id,
                'src_prev_balance': src_acc.snapshot(),
                'dest_prev_balance': dest_acc.snapshot()
            })
            
        # Withdraw first, then deposit
        src_acc.withdraw(amount)
        dest_acc.deposit(amount)

    def begin_batch(self) -> None:
        """Starts a new atomic batch transaction session."""
        self.in_batch = True
        self.current_batch_id += 1
        self.current_batch_ops = []

    def end_batch(self) -> None:
        """Finalizes an active batch session."""
        self.in_batch = False
        self.current_batch_ops = []

    def rollback_current_batch((self) -> None:
        """Rolls back all state changes performed during the current failed batch."""
        # Reverse apply state snapshots
        for op in reversed(self.current_batch_ops):
            if op['type'] in ('DEPOSIT', 'WITHDRAW'):
                acc = self.accounts[op['acc_id']]
                acc.restore(op['prev_balance'])
            elif op['type'] == 'TRANSFER':
                src_acc = self.accounts[op['src_acc_id']]
                dest_acc = self.accounts[op['dest_acc_id']]
                src_acc.restore(op['src_prev_balance'])
                dest_acc.restore(op['dest_prev_balance'])

        self.failed_batches.append(self.current_batch_id)
        self.in_batch = False
        self.current_batch_ops = []

    def process_operation(self, command_line: str) -> None:
        """Parses and executes command lines."""
        tokens = command_line.strip().split()
        if not tokens:
            return

        cmd = tokens[0].upper()

        try:
            if cmd == "BATCH_BEGIN":
                self.begin_batch()

            elif cmd == "BATCH_END":
                self.end_batch()

            elif cmd == "DEPOSIT":
                acc_id = tokens[1]
                amount = int(tokens[2])
                self._execute_deposit(acc_id, amount)
                self.history.append(Transaction("DEPOSIT", acc_id, amount))

            elif cmd == "WITHDRAW":
                acc_id = tokens[1]
                amount = int(tokens[2])
                self._execute_withdraw(acc_id, amount)
                self.history.append(Transaction("WITHDRAW", acc_id, amount))

            elif cmd == "TRANSFER":
                src_acc_id = tokens[1]
                dest_acc_id = tokens[2]
                amount = int(tokens[3])
                self._execute_transfer(src_acc_id, dest_acc_id, amount)
                self.history.append(Transaction("TRANSFER", src_acc_id, amount, dest_acc_id))

        except BankException as e:
            if self.in_batch:
                self.rollback_current_batch()
            else:
                # Individual transaction error outside batch (log error / ignore)
                pass


def main():
    """Main execution block processing stdin input."""
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return

    iterator = iter(input_data)
    
    try:
        # Read Initial Account Count
        num_accounts_str = next(iterator).strip()
        if not num_accounts_str:
            return
        num_accounts = int(num_accounts_str)

        bank = Bank()

        # Load Initial Accounts
        for _ in range(num_accounts):
            line = next(iterator).strip()
            parts = line.split()
            acc_id = parts[0]
            initial_bal = int(parts[1])
            bank.create_account(acc_id, initial_bal)

        # Read Operation Count
        num_ops_str = next(iterator).strip()
        num_ops = int(num_ops_str)

        # Process Operations
        for _ in range(num_ops):
            op_line = next(iterator).strip()
            bank.process_operation(op_line)

        # Output Failed Batches
        for failed_batch_id in bank.failed_batches:
            print(f"FAILED {failed_batch_id}")

        # Output Final Account Balances in Account ID Order
        for acc_id in sorted(bank.accounts.keys()):
            acc = bank.accounts[acc_id]
            print(f"{acc.account_id} {acc.balance}")

    except StopIteration:
        pass


if __name__ == "__main__":
    main()
