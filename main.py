import questionary
from rich.console import Console
from features.transactions.transactions import add_expense, add_income, list_transactions, display_balance
from features.budgets.budgets import set_budget, view_budgets # Import budget functions
from features.analytics.analytics import ( # Import analytics functions
    spending_analysis, 
    income_analysis, 
    savings_analysis, 
    financial_health_score, 
    generate_monthly_report
)
from features.smart_assistant.assistant import (
    daily_financial_check,
    smart_recommendations,
)

console = Console()

def main():
    while True:
        console.print("\n[bold magenta]Personal Finance Tracker Menu[/bold magenta]")
        choice = questionary.select(
            "What do you want to do?",
            choices=[
                "Add Expense",
                "Add Income",
                "List Transactions",
                "View Balance",
                "Set Budget",
                "View Budgets",
                "Spending Analysis",      # New option
                "Income Analysis",        # New option
                "Savings Analysis",       # New option
                "Financial Health Score", # New option
                "Generate Monthly Report",# New option
                "Daily Financial Check",
                "Smart Recommendations",
                "Exit"
            ]
        ).ask()

        if choice == "Add Expense":
            add_expense()
        elif choice == "Add Income":
            add_income()
        elif choice == "List Transactions":
            list_transactions()
        elif choice == "View Balance":
            display_balance()
        elif choice == "Set Budget":
            set_budget()
        elif choice == "View Budgets":
            view_budgets()
        elif choice == "Spending Analysis":
            spending_analysis()
        elif choice == "Income Analysis":
            income_analysis()
        elif choice == "Savings Analysis":
            savings_analysis()
        elif choice == "Financial Health Score":
            financial_health_score()
        elif choice == "Generate Monthly Report":
            generate_monthly_report()
        elif choice == "Daily Financial Check":
            daily_financial_check()
        elif choice == "Smart Recommendations":
            smart_recommendations()
        elif choice == "Exit":
            console.print("[bold green]Exiting Personal Finance Tracker. Goodbye![/bold green]")
            break

if __name__ == "__main__":
    main()