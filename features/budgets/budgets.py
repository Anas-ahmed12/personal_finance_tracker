import os
from typing import NamedTuple
from rich.console import Console
import questionary # Added this import

# Import necessary components from transactions feature
from features.transactions.transactions import (
    to_paisa, from_paisa, EXPENSE_CATEGORIES, get_valid_amount, get_category_choice
)

console = Console()

BUDGETS_FILE = "database/budgets.txt"

class Budget(NamedTuple):
    category: str
    amount: int # stored in paisa

def load_budgets() -> list[Budget]:
    """Loads budgets from the budgets file."""
    budgets = []
    if not os.path.exists(BUDGETS_FILE):
        return budgets

    with open(BUDGETS_FILE, "r") as f:
        for line in f:
            try:
                category, amount_paisa_str = line.strip().split(",", 1)
                budgets.append(
                    Budget(
                        category=category,
                        amount=int(amount_paisa_str)
                    )
                )
            except ValueError:
                console.print(f"[red]Skipping malformed budget: {line.strip()}[/red]")
    return budgets

def save_budgets(budgets: list[Budget]):
    """Saves all budgets to the budgets file, overwriting existing content."""
    with open(BUDGETS_FILE, "w") as f:
        for budget in budgets:
            f.write(f"{budget.category},{budget.amount}\n")

import questionary
from rich.console import Console

def set_budget():
    """Allows the user to set or update a monthly budget for a category."""
    console.print("\n[bold blue]Set Monthly Budget[/bold blue]")

    category = questionary.select(
        "Select category to set budget for:",
        choices=EXPENSE_CATEGORIES
    ).ask()

    if not category: # User cancelled selection
        console.print("[yellow]Budget setting cancelled.[/yellow]")
        return

    amount = get_valid_amount(f"Enter monthly budget amount for {category} (e.g., 500.00):")

    current_budgets = load_budgets()
    
    # Check if budget for this category already exists
    updated = False
    for i, budget in enumerate(current_budgets):
        if budget.category == category:
            current_budgets[i] = Budget(category=category, amount=amount)
            updated = True
            console.print(f"[green]Budget for {category} updated to {from_paisa(amount):.2f}.[/green]")
            break
    
    if not updated:
        current_budgets.append(Budget(category=category, amount=amount))
        console.print(f"[green]Budget for {category} set to {from_paisa(amount):.2f}.[/green]")
    
    save_budgets(current_budgets)

from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, MofNCompleteColumn
from datetime import datetime

# Import load_transactions from transactions module
from features.transactions.transactions import load_transactions

def view_budgets():
    """Displays current month's budget vs actual spending for each category."""
    console.print("\n[bold green]Monthly Budget Overview[/bold green]")

    budgets = load_budgets()
    if not budgets:
        console.print("[yellow]No budgets set yet. Use 'Set Budget' to add one.[/yellow]")
        return

    transactions = load_transactions()
    current_month_str = datetime.now().strftime("%Y-%m")

    # Calculate spending for the current month per category
    category_spending = {budget.category: 0 for budget in budgets}
    for t in transactions:
        if t.date.startswith(current_month_str) and t.type == "expense":
            if t.category in category_spending:
                category_spending[t.category] += t.amount
    
    table = Table(
        title=f"[bold]Budget for {current_month_str}[/bold]",
        show_footer=True,
        footer_style="bold"
    )
    table.add_column("Category", style="cyan")
    table.add_column("Budget", justify="right", style="magenta")
    table.add_column("Spent", justify="right", style="red")
    table.add_column("Remaining", justify="right", style="green")
    table.add_column("Utilization", justify="left")
    table.add_column("Status", style="yellow")

    total_budget_amount = 0
    total_spent_amount = 0
    over_budget_categories = []

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        console=console,
        transient=True
    ) as progress:
        for budget in budgets:
            task = progress.add_task(f"Processing [blue]{budget.category}[/blue]...", total=budget.amount)

            spent = category_spending.get(budget.category, 0)
            remaining = budget.amount - spent
            utilization_percent = (spent / budget.amount * 100) if budget.amount > 0 else 0

            status_text = ""
            status_style = ""

            if utilization_percent >= 100:
                status_text = "OVER"
                status_style = "bold red"
                over_budget_categories.append(budget.category)
            elif utilization_percent >= 70:
                status_text = "WARNING"
                status_style = "bold yellow"
            else:
                status_text = "OK"
                status_style = "bold green"
            
            # Progress bar color based on utilization
            bar_color = "green"
            if utilization_percent >= 70 and utilization_percent < 100:
                bar_color = "yellow"
            elif utilization_percent >= 100:
                bar_color = "red"

            progress.update(task, completed=min(spent, budget.amount)) # Cap completed at budget for bar
            
            table.add_row(
                budget.category,
                f"{from_paisa(budget.amount):.2f}",
                f"{from_paisa(spent):.2f}",
                f"[{'green' if remaining >= 0 else 'red'}]{from_paisa(remaining):.2f}[/]",
                f"[{bar_color}]{utilization_percent:.0f}%[/]",
                f"[{status_style}]{status_text}[/{status_style}]"
            )

            total_budget_amount += budget.amount
            total_spent_amount += spent
    
    total_remaining_amount = total_budget_amount - total_spent_amount
    overall_utilization_percent = (total_spent_amount / total_budget_amount * 100) if total_budget_amount > 0 else 0
    overall_balance_style = "green" if total_remaining_amount >= 0 else "red"

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{from_paisa(total_budget_amount):.2f}[/bold]",
        f"[bold]{from_paisa(total_spent_amount):.2f}[/bold]",
        f"[bold {overall_balance_style}]{from_paisa(total_remaining_amount):.2f}[/bold {overall_balance_style}]",
        f"[bold]{overall_utilization_percent:.0f}%[/bold]",
        ""
    )

    console.print(table)

    if over_budget_categories:
        console.print(f"\n[bold red]Categories over budget:[/bold red] {', '.join(over_budget_categories)}")
    console.print(f"\n[italic blue]Overall utilization: {overall_utilization_percent:.0f}%[/italic blue]")
    if overall_utilization_percent >= 90:
        console.print("[yellow]Recommendation: Review your spending for the month![/yellow]")
    elif overall_utilization_percent < 50:
        console.print("[green]Recommendation: You're doing great with your budget![/green]")
