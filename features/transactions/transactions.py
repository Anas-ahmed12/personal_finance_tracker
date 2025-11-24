import questionary
from rich.console import Console
from rich.table import Table
from datetime import datetime
from typing import NamedTuple

# --- Transaction Data Structure ---
class Transaction(NamedTuple):
    date: str
    type: str # "expense" or "income"
    category: str # specific category or source
    description: str
    amount: int # stored in paisa

# Initialize Rich console
console = Console()

# --- Constants ---
EXPENSE_CATEGORIES = [
    "Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"
]
INCOME_SOURCES = [
    "Salary", "Freelance", "Business", "Investment", "Gift", "Other"
]

# --- Money Handling ---
def to_paisa(amount: float) -> int:
    """Converts a float amount (e.g., 12.50) to integer paisa (e.g., 1250)."""
    return int(round(amount * 100))

def from_paisa(paisa_amount: int) -> float:
    """Converts integer paisa (e.g., 1250) back to float amount (e.g., 12.50)."""
    return paisa_amount / 100.0

# --- Date Handling ---
def get_valid_date(prompt: str) -> str:
    """
    Prompts the user for a date and validates the input.
    Returns the date as a 'YYYY-MM-DD' string.
    """
    while True:
        date_str = questionary.text(
            prompt,
            default=datetime.now().strftime("%Y-%m-%d")
        ).ask()
        try:
            # Attempt to parse the date to validate it
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            console.print("[red]Invalid date format. Please use YYYY-MM-DD.[/red]")

import os

TRANSACTIONS_FILE = "database/transactions.txt"

def load_transactions() -> list[Transaction]:
    """Loads transactions from the transactions file."""
    transactions = []
    if not os.path.exists(TRANSACTIONS_FILE):
        return transactions

    with open(TRANSACTIONS_FILE, "r") as f:
        for line in f:
            try:
                date_str, type_str, category, description, amount_paisa_str = line.strip().split(",", 4)
                transactions.append(
                    Transaction(
                        date=date_str,
                        type=type_str,
                        category=category,
                        description=description,
                        amount=int(amount_paisa_str)
                    )
                )
            except ValueError:
                console.print(f"[red]Skipping malformed transaction: {line.strip()}[/red]")
    return transactions

def save_transaction(transaction: Transaction):
    """Appends a single transaction to the transactions file."""
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(
            f"{transaction.date},"
            f"{transaction.type},"
            f"{transaction.category},"
            f"{transaction.description},"
            f"{transaction.amount}\n"
        )

def get_valid_amount(prompt: str) -> int:
    """
    Prompts the user for an amount, validates it's a positive number,
    and returns the amount in paisa.
    """
    while True:
        amount_str = questionary.text(prompt).ask()
        try:
            amount_float = float(amount_str)
            if amount_float <= 0:
                console.print("[red]Amount must be a positive number.[/red]")
            else:
                return to_paisa(amount_float)
        except ValueError:
            console.print("[red]Invalid amount. Please enter a number.[/red]")

def get_category_choice(prompt: str, choices: list[str]) -> str:
    """
    Prompts the user to choose from a list of categories/sources.
    """
    return questionary.select(
        prompt,
        choices=choices
    ).ask()

def add_expense():
    """Adds a new expense transaction."""
    console.print("\n[bold blue]Add New Expense[/bold blue]")
    amount = get_valid_amount("Enter amount (e.g., 12.50):")
    category = get_category_choice("Select category:", EXPENSE_CATEGORIES)
    description = questionary.text("Enter description (e.g., 'Coffee with friends'):").ask()
    date = get_valid_date("Enter date (YYYY-MM-DD):")

    transaction = Transaction(
        date=date,
        type="expense",
        category=category,
        description=description,
        amount=amount
    )
    save_transaction(transaction)
    console.print(f"[green]Expense of {from_paisa(amount):.2f} added successfully![/green]")

def add_income():
    """Adds a new income transaction."""
    console.print("\n[bold green]Add New Income[/bold green]")
    amount = get_valid_amount("Enter amount (e.g., 1000.00):")
    source = get_category_choice("Select source:", INCOME_SOURCES)
    description = questionary.text("Enter description (e.g., 'Monthly Salary'):").ask()
    date = get_valid_date("Enter date (YYYY-MM-DD):")

    transaction = Transaction(
        date=date,
        type="income",
        category=source,
        description=description,
        amount=amount
    )
    save_transaction(transaction)
    console.print(f"[green]Income of {from_paisa(amount):.2f} added successfully![/green]")

def list_transactions():
    """Displays a list of transactions with optional filters."""
    transactions = load_transactions()

    if not transactions:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    # Sort transactions by date, newest first
    transactions.sort(key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"), reverse=True)

    # Filtering options
    filter_choice = questionary.select(
        "Filter transactions:",
        choices=["All", "Last 7 Days", "Only Expenses", "Only Income"]
    ).ask()

    filtered_transactions = []
    today = datetime.now()

    for t in transactions:
        include = True
        transaction_date = datetime.strptime(t.date, "%Y-%m-%d")

        if filter_choice == "Last 7 Days":
            if (today - transaction_date).days > 7:
                include = False
        elif filter_choice == "Only Expenses":
            if t.type != "expense":
                include = False
        elif filter_choice == "Only Income":
            if t.type != "income":
                include = False
        
        if include:
            filtered_transactions.append(t)

    if not filtered_transactions:
        console.print("[yellow]No transactions found matching the filter criteria.[/yellow]")
        return

    table = Table(
        title="[bold]Transactions[/bold]",
        show_footer=True,
        footer_style="bold"
    )
    table.add_column("Date", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Category", style="blue")
    table.add_column("Description", style="white")
    table.add_column("Amount", style="green", justify="right")

    total_income = 0
    total_expense = 0

    for t in filtered_transactions:
        amount_display = f"{from_paisa(t.amount):.2f}"
        if t.type == "expense":
            amount_style = "red"
            total_expense += t.amount
        else:
            amount_style = "green"
            total_income += t.amount
        
        table.add_row(
            t.date,
            t.type.capitalize(),
            t.category,
            t.description,
            f"[{amount_style}]{amount_display}[/{amount_style}]"
        )
    
    total_balance = total_income - total_expense
    balance_style = "green" if total_balance >= 0 else "red"

    table.columns[4].footer = (
        f"[green]Income: {from_paisa(total_income):.2f}[/green]\n"
        f"[red]Expense: {from_paisa(total_expense):.2f}[/red]\n"
        f"[{balance_style}]Balance: {from_paisa(total_balance):.2f}[/{balance_style}]"
    )

    console.print(table)

def display_balance():
    """Displays the balance for the current month."""
    transactions = load_transactions()
    
    if not transactions:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    current_month = datetime.now().strftime("%Y-%m")
    monthly_income = 0
    monthly_expense = 0

    for t in transactions:
        if t.date.startswith(current_month):
            if t.type == "income":
                monthly_income += t.amount
            else: # expense
                monthly_expense += t.amount
    
    monthly_balance = monthly_income - monthly_expense
    balance_style = "green" if monthly_balance >= 0 else "red"

    console.print(f"\n[bold underline]Balance for {current_month}[/bold underline]")
    console.print(f"[green]Total Income: {from_paisa(monthly_income):.2f}[/green]")
    console.print(f"[red]Total Expenses: {from_paisa(monthly_expense):.2f}[/red]")
    console.print(f"[{balance_style}]Current Balance: {from_paisa(monthly_balance):.2f}[/{balance_style}]")

