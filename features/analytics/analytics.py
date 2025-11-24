from datetime import datetime, timedelta
from collections import defaultdict
from rich.console import Console

# Import necessary components from other features
from features.transactions.transactions import load_transactions, Transaction, from_paisa
from features.budgets.budgets import load_budgets, Budget

console = Console()

def filter_transactions_by_month(
    transactions: list[Transaction], 
    year: int, 
    month: int
) -> list[Transaction]:
    """Filters transactions for a specific year and month."""
    return [
        t for t in transactions 
        if datetime.strptime(t.date, "%Y-%m-%d").year == year and 
           datetime.strptime(t.date, "%Y-%m-%d").month == month
    ]

def get_monthly_spending_by_category(
    transactions: list[Transaction]
) -> dict[str, int]:
    """Aggregates spending by category for a given list of transactions."""
    spending_by_category = defaultdict(int)
    for t in transactions:
        if t.type == "expense":
            spending_by_category[t.category] += t.amount
    return spending_by_category

def get_monthly_income_by_source(
    transactions: list[Transaction]
) -> dict[str, int]:
    """Aggregates income by source for a given list of transactions."""
    income_by_source = defaultdict(int)
    for t in transactions:
        if t.type == "income":
            income_by_source[t.category] += t.amount
    return income_by_source

def get_total_spending(transactions: list[Transaction]) -> int:
    """Calculates total spending from a list of transactions."""
    return sum(t.amount for t in transactions if t.type == "expense")

def get_total_income(transactions: list[Transaction]) -> int:
    """Calculates total income from a list of transactions."""
    return sum(t.amount for t in transactions if t.type == "income")

from rich.table import Table

def generate_pie_chart_ascii(data: dict[str, int], title: str = "Distribution") -> str:
    """Generates a simple ASCII pie chart for data."""
    if not data:
        return "[yellow]No data to display for pie chart.[/yellow]"

    total = sum(data.values())
    if total == 0:
        return "[yellow]No data to display for pie chart (total is zero).[/yellow]"

    chart = f"[bold]{title}[/bold]\n"
    sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)
    
    max_label_length = max(len(label) for label, _ in sorted_data)

    for label, value in sorted_data:
        percentage = (value / total) * 100
        # Scale bar length to fit in a reasonable console width
        bar_length = int(percentage / 100 * 20)  # Max 20 characters for the bar
        bar = "█" * bar_length
        chart += f"{label.ljust(max_label_length)} {bar} {percentage:.0f}%\n"
    return chart

def spending_analysis():
    """Provides an analysis of spending patterns."""
    console.print("\n[bold blue]Spending Analysis[/bold blue]")

    all_transactions = load_transactions()
    if not all_transactions:
        console.print("[yellow]No transactions to analyze.[/yellow]")
        return

    today = datetime.now()
    current_month_year = (today.year, today.month)
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month_year = (last_month_date.year, last_month_date.month)

    current_month_transactions = filter_transactions_by_month(
        all_transactions, current_month_year[0], current_month_year[1]
    )
    last_month_transactions = filter_transactions_by_month(
        all_transactions, last_month_year[0], last_month_year[1]
    )

    # --- Current Month Spending ---
    console.print(f"\n[bold underline]Current Month ({today.strftime('%Y-%m')}) Spending:[/bold underline]")
    current_month_spending_by_category = get_monthly_spending_by_category(current_month_transactions)
    total_current_month_spending = sum(current_month_spending_by_category.values())

    console.print(generate_pie_chart_ascii(
        {k: v for k,v in current_month_spending_by_category.items()}, 
        "Spending by Category"
    ))

    if current_month_spending_by_category:
        sorted_spending = sorted(
            current_month_spending_by_category.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        console.print("\n[bold]Top 3 Spending Categories:[/bold]")
        for category, amount in sorted_spending[:3]:
            console.print(f"- {category}: {from_paisa(amount):.2f}")
    
    if current_month_transactions:
        # Calculate average daily expense for current month
        first_day_of_month = today.replace(day=1)
        days_in_month_so_far = (today - first_day_of_month).days + 1
        avg_daily_expense = total_current_month_spending / days_in_month_so_far
        console.print(f"\n[bold]Average Daily Expense (current month):[/bold] {from_paisa(avg_daily_expense):.2f}")

    # --- Comparison with Last Month ---
    console.print(f"\n[bold underline]Comparison with Last Month ({last_month_date.strftime('%Y-%m')}):[/bold underline]")
    total_last_month_spending = get_total_spending(last_month_transactions)

    console.print(f"Current Month Total Spending: {from_paisa(total_current_month_spending):.2f}")
    console.print(f"Last Month Total Spending: {from_paisa(total_last_month_spending):.2f}")

    if total_last_month_spending > 0:
        change_percent = ((total_current_month_spending - total_last_month_spending) / total_last_month_spending) * 100
        if change_percent > 0:
            console.print(f"[red]Spending increased by {change_percent:.2f}%[/red] compared to last month.")
        elif change_percent < 0:
            console.print(f"[green]Spending decreased by {abs(change_percent):.2f}%[/green] compared to last month.")
        else:
            console.print("[blue]Spending remained the same[/blue] as last month.")
    else:
        if total_current_month_spending > 0:
            console.print("[red]No spending last month, but spending in current month.[/red]")
        else:
            console.print("[blue]No spending in either month.[/blue]")

    # --- Spending Trends (Simplified) ---
    console.print("\n[bold underline]Spending Trends (last 3 months):[/bold underline]")
    trend_months = []
    trend_spending = []

    for i in range(3): # Last 3 months including current
        month_date = (today.replace(day=1) - timedelta(days=30*i)) 
        m_transactions = filter_transactions_by_month(
            all_transactions, month_date.year, month_date.month
        )
        total_m_spending = get_total_spending(m_transactions)
        trend_months.append(month_date.strftime("%Y-%m"))
        trend_spending.append(total_m_spending)
    
    # Reverse to show oldest to newest
    trend_months.reverse()
    trend_spending.reverse()

    console.print(f"Spending over last 3 months: {', '.join([f'{m}: {from_paisa(s):.2f}' for m, s in zip(trend_months, trend_spending)])}")
    
    if len(trend_spending) >= 2:
        if trend_spending[-1] > trend_spending[-2]:
            console.print("[red]Overall spending trend: UPWARD[/red]")
        elif trend_spending[-1] < trend_spending[-2]:
            console.print("[green]Overall spending trend: DOWNWARD[/green]")
        else:
            console.print("[blue]Overall spending trend: STABLE[/blue]")
        
def spending_analysis():
    """Provides an analysis of spending patterns."""
    console.print("\n[bold blue]Spending Analysis[/bold blue]")

    all_transactions = load_transactions()
    if not all_transactions:
        console.print("[yellow]No transactions to analyze.[/yellow]")
        return

    today = datetime.now()
    current_month_year = (today.year, today.month)
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month_year = (last_month_date.year, last_month_date.month)

    current_month_transactions = filter_transactions_by_month(
        all_transactions, current_month_year[0], current_month_year[1]
    )
    last_month_transactions = filter_transactions_by_month(
        all_transactions, last_month_year[0], last_month_year[1]
    )

    # --- Current Month Spending ---
    console.print(f"\n[bold underline]Current Month ({today.strftime('%Y-%m')}) Spending:[/bold underline]")
    current_month_spending_by_category = get_monthly_spending_by_category(current_month_transactions)
    total_current_month_spending = sum(current_month_spending_by_category.values())

    console.print(generate_pie_chart_ascii(
        {k: v for k,v in current_month_spending_by_category.items()}, 
        "Spending by Category"
    ))

    if current_month_spending_by_category:
        sorted_spending = sorted(
            current_month_spending_by_category.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        console.print("\n[bold]Top 3 Spending Categories:[/bold]")
        for category, amount in sorted_spending[:3]:
            console.print(f"- {category}: {from_paisa(amount):.2f}")
    
    if current_month_transactions:
        # Calculate average daily expense for current month
        first_day_of_month = today.replace(day=1)
        days_in_month_so_far = (today - first_day_of_month).days + 1
        avg_daily_expense = total_current_month_spending / days_in_month_so_far
        console.print(f"\n[bold]Average Daily Expense (current month):[/bold] {from_paisa(avg_daily_expense):.2f}")

    # --- Comparison with Last Month ---
    console.print(f"\n[bold underline]Comparison with Last Month ({last_month_date.strftime('%Y-%m')}):[/bold underline]")
    total_last_month_spending = get_total_spending(last_month_transactions)

    console.print(f"Current Month Total Spending: {from_paisa(total_current_month_spending):.2f}")
    console.print(f"Last Month Total Spending: {from_paisa(total_last_month_spending):.2f}")

    if total_last_month_spending > 0:
        change_percent = ((total_current_month_spending - total_last_month_spending) / total_last_month_spending) * 100
        if change_percent > 0:
            console.print(f"[red]Spending increased by {change_percent:.2f}%[/red] compared to last month.")
        elif change_percent < 0:
            console.print(f"[green]Spending decreased by {abs(change_percent):.2f}%[/green] compared to last month.")
        else:
            console.print("[blue]Spending remained the same[/blue] as last month.")
    else:
        if total_current_month_spending > 0:
            console.print("[red]No spending last month, but spending in current month.[/red]")
        else:
            console.print("[blue]No spending in either month.[/blue]")

    # --- Spending Trends (Simplified) ---
    console.print("\n[bold underline]Spending Trends (last 3 months):[/bold underline]")
    trend_months = []
    trend_spending = []

    for i in range(3): # Last 3 months including current
        month_date = (today.replace(day=1) - timedelta(days=30*i)) 
        m_transactions = filter_transactions_by_month(
            all_transactions, month_date.year, month_date.month
        )
        total_m_spending = get_total_spending(m_transactions)
        trend_months.append(month_date.strftime("%Y-%m"))
        trend_spending.append(total_m_spending)
    
    # Reverse to show oldest to newest
    trend_months.reverse()
    trend_spending.reverse()

    console.print(f"Spending over last 3 months: {', '.join([f'{m}: {from_paisa(s):.2f}' for m, s in zip(trend_months, trend_spending)])}")
    
    if len(trend_spending) >= 2:
        if trend_spending[-1] > trend_spending[-2]:
            console.print("[red]Overall spending trend: UPWARD[/red]")
        elif trend_spending[-1] < trend_spending[-2]:
            console.print("[green]Overall spending trend: DOWNWARD[/green]")
        else:
            console.print("[blue]Overall spending trend: STABLE[/blue]")
def income_analysis():
    """Provides an analysis of income patterns."""
    console.print("\n[bold blue]Income Analysis[/bold blue]")

    all_transactions = load_transactions()
    if not all_transactions:
        console.print("[yellow]No transactions to analyze.[/yellow]")
        return

    today = datetime.now()
    current_month_year = (today.year, today.month)
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month_year = (last_month_date.year, last_month_date.month)

    current_month_transactions = filter_transactions_by_month(
        all_transactions, current_month_year[0], current_month_year[1]
    )
    last_month_transactions = filter_transactions_by_month(
        all_transactions, last_month_year[0], last_month_year[1]
    )

    # --- Current Month Income ---
    console.print(f"\n[bold underline]Current Month ({today.strftime('%Y-%m')}) Income:[/bold underline]")
    current_month_income_by_source = get_monthly_income_by_source(current_month_transactions)
    total_current_month_income = sum(current_month_income_by_source.values())

    if current_month_income_by_source:
        for source, amount in current_month_income_by_source.items():
            console.print(f"- {source}: {from_paisa(amount):.2f}")
    else:
        console.print("[yellow]No income recorded for the current month.[/yellow]")
    
    console.print(f"\n[bold]Total Income (current month):[/bold] {from_paisa(total_current_month_income):.2f}")

    # --- Comparison with Last Month ---
    console.print(f"\n[bold underline]Comparison with Last Month ({last_month_date.strftime('%Y-%m')}):[/bold underline]")
    total_last_month_income = get_total_income(last_month_transactions)

    console.print(f"Current Month Total Income: {from_paisa(total_current_month_income):.2f}")
    console.print(f"Last Month Total Income: {from_paisa(total_last_month_income):.2f}")

    if total_last_month_income > 0:
        change_percent = ((total_current_month_income - total_last_month_income) / total_last_month_income) * 100
        if change_percent > 0:
            console.print(f"[green]Income increased by {change_percent:.2f}%[/green] compared to last month.")
        elif change_percent < 0:
            console.print(f"[red]Income decreased by {abs(change_percent):.2f}%[/red] compared to last month.")
        else:
            console.print("[blue]Income remained the same[/blue] as last month.")
    else:
        if total_current_month_income > 0:
            console.print("[green]No income last month, but income in current month.[/green]")
        else:
            console.print("[blue]No income in either month.[/blue]")

    # --- Income Stability (Simplified: Check consistency over last 3 months) ---
    console.print("\n[bold underline]Income Stability (last 3 months):[/bold underline]")
    income_over_months = []
    for i in range(3):
        month_date = (today.replace(day=1) - timedelta(days=30*i))
        m_transactions = filter_transactions_by_month(all_transactions, month_date.year, month_date.month)
        income_over_months.append(get_total_income(m_transactions))
    
    # Reverse to show oldest to newest
    income_over_months.reverse()

    if len(income_over_months) == 3:
        # Simple stability check: variation within 10%
        if all(abs(income_over_months[i] - income_over_months[0]) <= income_over_months[0] * 0.1 for i in range(1,3)):
            console.print("[green]Income appears relatively stable over the last 3 months.[/green]")
        else:
            console.print("[yellow]Income shows some fluctuation over the last 3 months.[/yellow]")
    elif income_over_months:
        console.print("[yellow]Not enough data to assess income stability over 3 months.[/yellow]")
    else:
        console.print("[yellow]No income data available.[/yellow]")
def savings_analysis():
    """Provides an analysis of savings patterns."""
    console.print("\n[bold blue]Savings Analysis[/bold blue]")

    all_transactions = load_transactions()
    if not all_transactions:
        console.print("[yellow]No transactions to analyze.[/yellow]")
        return

    today = datetime.now()
    
    # --- Current Month Savings ---
    console.print(f"\n[bold underline]Current Month ({today.strftime('%Y-%m')}) Savings:[/bold underline]")
    current_month_transactions = filter_transactions_by_month(all_transactions, today.year, today.month)
    total_current_month_income = get_total_income(current_month_transactions)
    total_current_month_spending = get_total_spending(current_month_transactions)

    monthly_savings = total_current_month_income - total_current_month_spending
    savings_rate = (monthly_savings / total_current_month_income * 100) if total_current_month_income > 0 else 0

    console.print(f"Total Income: {from_paisa(total_current_month_income):.2f}")
    console.print(f"Total Spending: {from_paisa(total_current_month_spending):.2f}")
    console.print(f"Monthly Savings: {from_paisa(monthly_savings):.2f}")
    console.print(f"Savings Rate: {savings_rate:.2f}%")

    # --- Savings Trend (last 3 months) ---
    console.print("\n[bold underline]Savings Trend (last 3 months):[/bold underline]")
    savings_over_months = []
    for i in range(3):
        month_date = (today.replace(day=1) - timedelta(days=30*i))
        m_transactions = filter_transactions_by_month(all_transactions, month_date.year, month_date.month)
        m_income = get_total_income(m_transactions)
        m_spending = get_total_spending(m_transactions)
        m_savings = m_income - m_spending
        savings_over_months.append((month_date.strftime("%Y-%m"), m_savings))
    
    # Reverse to show oldest to newest
    savings_over_months.reverse()

    for month_str, savings_amount in savings_over_months:
        console.print(f"- {month_str}: {from_paisa(savings_amount):.2f}")
    
    if len(savings_over_months) >= 2:
        latest_savings = savings_over_months[-1][1]
        previous_savings = savings_over_months[-2][1]

        if latest_savings > previous_savings:
            console.print("[green]Savings trend: UPWARD[/green]")
        elif latest_savings < previous_savings:
            console.print("[red]Savings trend: DOWNWARD[/red]")
        else:
            console.print("[blue]Savings trend: STABLE[/blue]")

def financial_health_score():
    """Calculates and displays a financial health score."""
    console.print("\n[bold blue]Financial Health Score[/bold blue]")

    all_transactions = load_transactions()
    all_budgets = load_budgets()

    if not all_transactions:
        console.print("[yellow]No transactions available to calculate health score.[/yellow]")
        return

    today = datetime.now()
    current_month_transactions = filter_transactions_by_month(all_transactions, today.year, today.month)
    
    total_income_cm = get_total_income(current_month_transactions)
    total_spending_cm = get_total_spending(current_month_transactions)

    # --- Score Calculation ---
    score = 0
    score_breakdown = {}

    # 1. Savings Rate (30 points)
    if total_income_cm > 0:
        monthly_savings = total_income_cm - total_spending_cm
        savings_rate = (monthly_savings / total_income_cm) * 100
        savings_score = 0
        if savings_rate >= 20: # Excellent savings
            savings_score = 30
        elif savings_rate >= 10: # Good savings
            savings_score = 20
        elif savings_rate > 0: # Some savings
            savings_score = 10
        score += savings_score
        score_breakdown["Savings Rate"] = f"{savings_score}/30 (Current: {savings_rate:.2f}%)"
    else:
        score_breakdown["Savings Rate"] = "N/A (No income)"


    # 2. Budget Adherence (25 points)
    budget_adherence_score = 25
    if all_budgets:
        current_month_str = today.strftime("%Y-%m")
        category_spending = {budget.category: 0 for budget in all_budgets}
        for t in all_transactions:
            if t.date.startswith(current_month_str) and t.type == "expense":
                if t.category in category_spending:
                    category_spending[t.category] += t.amount
        
        over_budget_count = 0
        for budget in all_budgets:
            spent = category_spending.get(budget.category, 0)
            if spent > budget.amount:
                over_budget_count += 1
        
        if over_budget_count == 0:
            budget_adherence_score = 25 # Perfect adherence
        elif over_budget_count <= len(all_budgets) / 2:
            budget_adherence_score = 15 # Some overspending
        else:
            budget_adherence_score = 5 # Significant overspending
    else:
        budget_adherence_score = 0 # No budgets set
    
    score += budget_adherence_score
    score_breakdown["Budget Adherence"] = f"{budget_adherence_score}/25"

    # 3. Income vs Expenses (25 points)
    income_vs_expense_score = 0
    if total_income_cm > 0:
        if total_income_cm > total_spending_cm:
            income_vs_expense_score = 25 # Income > Expenses
        elif total_income_cm == total_spending_cm:
            income_vs_expense_score = 15 # Income = Expenses
        else:
            income_vs_expense_score = 5 # Income < Expenses
    score += income_vs_expense_score
    score_breakdown["Income vs Expenses"] = f"{income_vs_expense_score}/25"

    # 4. Debt Management (20 points - Placeholder for future)
    # For now, assume good debt management if no specific debt tracking
    debt_score = 10 # Neutral score for now
    score += debt_score
    score_breakdown["Debt Management"] = f"{debt_score}/20 (Placeholder)"


    console.print(f"\n[bold underline]Your Financial Health Score: {score}/100[/bold underline]")
    
    console.print("\n[bold]Score Breakdown:[/bold]")
    for factor, detail in score_breakdown.items():
        console.print(f"- {factor}: {detail}")

    console.print("\n[bold]Interpretation and Recommendations:[/bold]")
    if score >= 80:
        console.print("[green]Excellent! Your financial habits are strong. Keep up the great work![/green]")
    elif score >= 60:
        console.print("[blue]Good! You have a solid foundation. Consider optimizing spending and increasing savings.[/blue]")
    elif score >= 40:
        console.print("[yellow]Fair. There's room for improvement. Focus on reducing unnecessary expenses and setting clear budgets.[/yellow]")
    else:
        console.print("[red]Needs Attention. It's time to review your finances thoroughly. Prioritize increasing income and cutting expenses.[/red]")
    
    # Specific recommendations
    if "Savings Rate" in score_breakdown and "Current: 0.00%" in score_breakdown["Savings Rate"]:
        console.print("[yellow]- Recommendation: Start building an emergency fund. Even small, consistent savings make a difference.[/yellow]")
    if "Budget Adherence" in score_breakdown and budget_adherence_score < 25:
        console.print("[yellow]- Recommendation: Revisit your budgets. Are they realistic? Try to stick to them to avoid overspending.[/yellow]")
    if "Income vs Expenses" in score_breakdown and total_income_cm < total_spending_cm:
        console.print("[yellow]- Recommendation: Look for ways to increase your income or significantly reduce your expenses to achieve a positive cash flow.[/yellow]")

def generate_monthly_report():
    """Generates a comprehensive monthly financial report."""
    console.print("\n[bold magenta]Comprehensive Monthly Financial Report[/bold magenta]")

    all_transactions = load_transactions()
    all_budgets = load_budgets()

    if not all_transactions and not all_budgets:
        console.print("[yellow]No data available to generate a report.[/yellow]")
        return
    
    today = datetime.now()
    current_month_str = today.strftime("%Y-%m")
    current_month_transactions = filter_transactions_by_month(all_transactions, today.year, today.month)

    # --- Month Overview ---
    console.print(f"\n[bold underline]1. Month Overview ({current_month_str})[/bold underline]")
    total_income_cm = get_total_income(current_month_transactions)
    total_spending_cm = get_total_spending(current_month_transactions)
    net_flow = total_income_cm - total_spending_cm
    
    console.print(f"  Total Income: {from_paisa(total_income_cm):.2f}")
    console.print(f"  Total Expenses: {from_paisa(total_spending_cm):.2f}")
    console.print(f"  Net Cash Flow: [{ 'green' if net_flow >= 0 else 'red' }]{from_paisa(net_flow):.2f}[/]")

    # --- Income Summary ---
    console.print(f"\n[bold underline]2. Income Summary[/bold underline]")
    income_by_source_cm = get_monthly_income_by_source(current_month_transactions)
    if income_by_source_cm:
        for source, amount in income_by_source_cm.items():
            console.print(f"  - {source}: {from_paisa(amount):.2f}")
    else:
        console.print("  No income recorded this month.")

    # --- Expense Summary ---
    console.print(f"\n[bold underline]3. Expense Summary[/bold underline]")
    spending_by_category_cm = get_monthly_spending_by_category(current_month_transactions)
    if spending_by_category_cm:
        for category, amount in spending_by_category_cm.items():
            console.print(f"  - {category}: {from_paisa(amount):.2f}")
    else:
        console.print("  No expenses recorded this month.")
    
    # ASCII Pie Chart
    console.print(f"\n{generate_pie_chart_ascii(spending_by_category_cm, 'Spending Distribution')}")


    # --- Budget Performance ---
    console.print(f"\n[bold underline]4. Budget Performance[/bold underline]")
    if all_budgets:
        category_spending = {budget.category: 0 for budget in all_budgets}
        for t in all_transactions: # Use all transactions for consistent comparison with budgets
            if t.date.startswith(current_month_str) and t.type == "expense":
                if t.category in category_spending:
                    category_spending[t.category] += t.amount
        
        budget_table = Table(title="Budget vs. Actual")
        budget_table.add_column("Category")
        budget_table.add_column("Budget")
        budget_table.add_column("Spent")
        budget_table.add_column("Status")

        over_budget_count = 0
        for budget in all_budgets:
            spent = category_spending.get(budget.category, 0)
            status_text = ""
            status_style = ""
            if spent > budget.amount:
                status_text = "OVER"
                status_style = "bold red"
                over_budget_count += 1
            elif spent > budget.amount * 0.7:
                status_text = "WARNING"
                status_style = "bold yellow"
            else:
                status_text = "OK"
                status_style = "bold green"
            
            budget_table.add_row(
                budget.category,
                f"{from_paisa(budget.amount):.2f}",
                f"{from_paisa(spent):.2f}",
                f"[{status_style}]{status_text}[/{status_style}]"
            )
        console.print(budget_table)
        if over_budget_count > 0:
            console.print(f"[red]You are over budget in {over_budget_count} categories this month.[/red]")
        else:
            console.print("[green]You are within budget for all categories this month. Good job![/green]")
    else:
        console.print("  No budgets set to analyze performance.")

    # --- Savings Achieved ---
    console.print(f"\n[bold underline]5. Savings Achieved[/bold underline]")
    monthly_savings = total_income_cm - total_spending_cm
    savings_rate = (monthly_savings / total_income_cm * 100) if total_income_cm > 0 else 0
    console.print(f"  Monthly Savings: {from_paisa(monthly_savings):.2f}")
    console.print(f"  Savings Rate: {savings_rate:.2f}%")

    # --- Top Transactions (Expenses) ---
    console.print(f"\n[bold underline]6. Top Expenses[/bold underline]")
    top_expenses = sorted(
        [t for t in current_month_transactions if t.type == "expense"],
        key=lambda t: t.amount,
        reverse=True
    )[:5] # Top 5 expenses

    if top_expenses:
        for i, t in enumerate(top_expenses):
            console.print(f"  {i+1}. {t.description} ({t.category}) - {from_paisa(t.amount):.2f}")
    else:
        console.print("  No expenses recorded this month.")
    
    # --- Trends (Brief Summary) ---
    console.print(f"\n[bold underline]7. Trends Summary[/bold underline]")
    # Re-using logic from spending and income analysis, simplifying
    last_month_date = today.replace(day=1) - timedelta(days=1)
    last_month_transactions = filter_transactions_by_month(all_transactions, last_month_date.year, last_month_date.month)
    total_last_month_spending = get_total_spending(last_month_transactions)
    total_last_month_income = get_total_income(last_month_transactions)

    if total_last_month_spending > 0:
        spending_change = ((total_spending_cm - total_last_month_spending) / total_last_month_spending) * 100
        if spending_change > 0:
            console.print(f"  Spending: [red]Up by {spending_change:.2f}%[/red] compared to last month.")
        elif spending_change < 0:
            console.print(f"  Spending: [green]Down by {abs(spending_change):.2f}%[/green] compared to last month.")
        else:
            console.print(f"  Spending: [blue]Stable[/blue] compared to last month.")
    
    if total_last_month_income > 0:
        income_change = ((total_income_cm - total_last_month_income) / total_last_month_income) * 100
        if income_change > 0:
            console.print(f"  Income: [green]Up by {income_change:.2f}%[/green] compared to last month.")
        elif income_change < 0:
            console.print(f"  Income: [red]Down by {abs(income_change):.2f}%[/red] compared to last month.")
        else:
            console.print(f"  Income: [blue]Stable[/blue] compared to last month.")
    else:
        console.print("  Insufficient data for income trend.")
    
    # --- Next Month Projections (Very basic for now) ---
    console.print(f"\n[bold underline]8. Next Month Projections[/bold underline]")
    if total_income_cm > 0 and total_spending_cm > 0:
        projected_net_flow = total_income_cm - total_spending_cm # Simple projection based on current month
        console.print(f"  Based on current trends, projected net cash flow next month: {from_paisa(projected_net_flow):.2f}")
    else:
        console.print("  Not enough data to provide a projection.")

    console.print("\n[bold green]Report Generated Successfully![/bold green]")
