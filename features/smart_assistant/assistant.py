from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from features.transactions.transactions import load_transactions, from_paisa
from features.budgets.budgets import load_budgets
from features.analytics.analytics import (
    get_total_income,
    get_total_spending,
    filter_transactions_by_month,
)

console = Console()


def daily_financial_check():
    """
    Provides a daily financial check with spending, budget alerts, and tips.
    """
    console.print(Panel(
        f"[bold cyan]📊 Daily Financial Check ({datetime.now().strftime('%b %d, %Y')})[/bold cyan]",
        expand=False
    ))

    today_str = datetime.now().strftime("%Y-%m-%d")
    all_transactions = load_transactions()
    all_budgets = load_budgets()

    # --- Today's Spending ---
    todays_spending = sum(
        t.amount for t in all_transactions
        if t.date == today_str and t.type == "expense"
    )
    console.print(f"Today's Spending: [bold red]Rs {from_paisa(todays_spending):.2f}[/bold red]")

    # --- Daily Budget ---
    if all_budgets:
        monthly_budget = sum(b.amount for b in all_budgets)
        days_in_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        daily_budget = monthly_budget / days_in_month.day
        remaining_daily_budget = daily_budget - todays_spending

        status_icon = "✅" if remaining_daily_budget >= 0 else "❌"
        style = "green" if remaining_daily_budget >= 0 else "red"

        console.print(
            f"Daily Budget: [bold {style}]Rs {from_paisa(daily_budget):.2f}[/bold {style}] {status_icon}"
        )
        console.print(
            f"Remaining: [bold {style}]Rs {from_paisa(remaining_daily_budget):.2f}[/bold {style}]"
        )
    else:
        console.print("Daily Budget: [yellow]Not set. Consider setting monthly budgets.[/yellow]")

    # --- Alerts ---
    alerts = get_spending_alerts()
    if alerts:
        console.print("\n[bold yellow]⚠️ Alerts:[/bold yellow]")
        for alert in alerts:
            console.print(f"• {alert}")
    else:
        console.print("\n[bold green]✅ No immediate alerts.[/bold green]")

    # --- Quick Tip ---
    console.print("\n[bold magenta]💡 Quick Tip:[/bold magenta]")
    console.print(f"{get_quick_tip()}")


def get_spending_alerts() -> list[str]:
    """
    Generates a list of spending alerts based on current financial data.
    """
    alerts = []
    all_transactions = load_transactions()
    all_budgets = load_budgets()
    today = datetime.now()
    current_month_str = today.strftime("%Y-%m")

    # --- Budget Alerts (>80% used) ---
    if all_budgets:
        category_spending = {b.category: 0 for b in all_budgets}
        for t in all_transactions:
            if t.date.startswith(current_month_str) and t.type == "expense":
                if t.category in category_spending:
                    category_spending[t.category] += t.amount

        for budget in all_budgets:
            utilization = (category_spending[budget.category] / budget.amount * 100) if budget.amount > 0 else 0
            if 80 <= utilization < 100:
                alerts.append(
                    f"[yellow]Approaching budget limit for '{budget.category}'. "
                    f"({utilization:.0f}% used)[/yellow]"
                )
            elif utilization >= 100:
                alerts.append(
                    f"[red]Exceeded budget for '{budget.category}'. "
                    f"({utilization:.0f}% used)[/red]"
                )

    # --- Large Transaction Alert (>20% of monthly income) ---
    current_month_transactions = filter_transactions_by_month(
        all_transactions, today.year, today.month
    )
    monthly_income = get_total_income(current_month_transactions)

    if monthly_income > 0:
        large_transaction_threshold = monthly_income * 0.20
        for t in current_month_transactions:
            if t.type == "expense" and t.amount > large_transaction_threshold:
                alerts.append(
                    f"[yellow]Large transaction detected: Rs {from_paisa(t.amount):.2f} "
                    f"for '{t.description}' ({t.category}).[/yellow]"
                )

    return alerts


def get_quick_tip() -> str:
    """
    Returns a random, simple financial tip.
    """
    import random
    tips = [
        "Review your subscriptions. Any you can cancel?",
        "Try the '50/30/20 rule': 50% needs, 30% wants, 20% savings.",
        "Automate your savings. Even a small amount adds up!",
        "Before a large purchase, wait 24 hours to avoid impulse buying.",
        "Check for discounts or coupons before you shop.",
        "Consider packing lunch for a week to see how much you save.",
    ]
    return random.choice(tips)


def smart_recommendations():
    """
    Generates personalized financial recommendations based on user's data.
    """
    console.print(Panel("[bold green]💡 Smart Financial Recommendations[/bold green]", expand=False))

    all_transactions = load_transactions()
    all_budgets = load_budgets()
    recommendations = []

    # --- Recommendation 1: Overspending Categories ---
    if all_budgets:
        current_month_str = datetime.now().strftime("%Y-%m")
        category_spending = {b.category: 0 for b in all_budgets}
        for t in all_transactions:
            if t.date.startswith(current_month_str) and t.type == "expense":
                if t.category in category_spending:
                    category_spending[t.category] += t.amount

        over_budget_categories = [
            b.category for b in all_budgets
            if category_spending[b.category] > b.amount
        ]
        if over_budget_categories:
            recommendations.append(
                f"You've gone over budget in {', '.join(over_budget_categories)}. "
                "Consider reviewing spending in these areas."
            )

    # --- Recommendation 2: Low Savings Rate ---
    today = datetime.now()
    current_month_transactions = filter_transactions_by_month(
        all_transactions, today.year, today.month
    )
    total_income = get_total_income(current_month_transactions)
    total_spending = get_total_spending(current_month_transactions)

    if total_income > 0:
        savings_rate = ((total_income - total_spending) / total_income) * 100
        if savings_rate < 10:
            recommendations.append(
                f"Your savings rate is {savings_rate:.2f}%. "
                "Aim for at least 10-20%. Look for small expenses to cut."
            )

    # --- Recommendation 3: No Budgets Set ---
    if not all_budgets:
        recommendations.append(
            "You haven't set any budgets. "
            "Create budgets for top spending categories to get better control of your finances."
        )

    # --- Recommendation 4: Good Performance ---
    if all_budgets and not recommendations:
        recommendations.append(
            "You are doing a great job staying within your budget and saving money. "
            "Keep it up!"
        )

    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            console.print(f"[cyan]{i}.[/cyan] {rec}")
    else:
        console.print("[green]No specific recommendations at this time. Keep up the good work![/green]")
