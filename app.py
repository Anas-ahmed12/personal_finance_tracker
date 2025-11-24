
import streamlit as st

st.set_page_config(layout="wide")

st.title("Personal Finance Tracker - Project Documentation")

st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    h1 {
        text-align: center;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    .st-expander {
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
    }
    .st-expander-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #3498db;
    }
    .st-expander-content pre {
        background-color: #2c3e50;
        color: #f8f8f2;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)


gemini_files = {
    "GEMINI.md": """
# Personal Finance Tracker CLI

## Project Overview
Professional CLI application for tracking expenses, income, budgets, and generating financial insights - similar to fintech applications.

## Core Features
- Transaction management (expenses & income)
- Category-based budgeting with alerts
- Financial analytics and health scoring
- Monthly reports and insights
- Data export (CSV/JSON)
- Simple streamlit dashboard

## Tech Stack
- *Language*: Python 3.11+
- *CLI* Framework: Questionary (interactive select lists)
- *UI Library*: Rich (tables, panels, progress bars)
- *Storage*: Plain text files (no database)
- *Package Manager*: UV

## Project Structure

finance-tracker/
├── main.py                    # Entry point with menu loop
├── database/
│   ├── transactions.txt       # All transactions
│   └── budgets.txt           # Budget allocations
└── features/
    ├── transactions/
    │   ├── GEMINI.md
    │   └── transactions.py
    ├── budgets/
    │   ├── GEMINI.md
    │   └── budgets.py
    └── analytics/
        ├── GEMINI.md
        └── analytics.py
    ...


## Critical Money Handling Rule
*ALWAYS store monetary values as integers (paisa/cents) to avoid floating-point errors.*

python
# Correct approach:
amount_paisa = 1250      # Store Rs 12.50 as 1250 paisa
display = amount / 100   # Display as Rs 12.50

# Wrong approach:
amount = 12.50           # Never use float for money!


## Transaction Categories
*Expenses*: Food, Transport, Shopping, Bills, Entertainment, Health, Other
*Income*: Salary, Freelance, Business, Investment, Gift, Other

# CLI Interaction
This repository uses questionary for dropdown-style selections in the terminal. The UI visual pieces (tables, panels) use Rich.
""",
    "features/transactions/GEMINI.md": """
## Goal
Build the core feature - tracking expenses and income transactions.

## Learning Focus
- Working with money in code (avoid float errors!)
- Date handling
- File operations
- Input validation
- Transaction categories

## Fintech Concepts
- **Transaction**: Any money movement (in or out)
- **Debit**: Money going out (expense)
- **Credit**: Money coming in (income)
- **Categories**: Grouping transactions (Food, Transport, Salary, etc.)b  

## Features to Build

### 1. Add Expense
Flow:
1. Ask amount (validate: must be positive number)
2. Ask category (Food, Transport, Shopping, Bills, Entertainment, Health, Other)
3. Ask description (e.g., "Lunch at restaurant")
4. Ask date (default: today, or allow custom date)
5. Save to transactions.txt

### 2. Add Income
Flow:
1. Ask amount
2. Ask source (Salary, Freelance, Business, Investment, Gift, Other)
3. Ask description
4. Ask date
5. Save to transactions.txt

### 3. List Transactions
Display:
- Show transactions in Rich table
- Columns: Date, Type, Category, Description, Amount
- Color: Red for expenses, Green for income
- Sort by date (newest first)
- Optional filters: last 7 days, only expenses, only income

### 4. Balance Command
Display:
- Total Income (green)
- Total Expenses (red)
- Current Balance (green if positive, red if negative)
- Show for current month

## Success Criteria

✅ Can add expenses with validation
✅ Can add income with validation
✅ Can list all transactions
✅ Can filter transactions by days
✅ Can see current balance
✅ Money calculations are accurate (no float errors)
✅ Beautiful colored output
""",
    "features/budgets/GEMINI.md": """
# Budget Management System

## Goal
Set monthly budgets for categories and track spending against them.

## Learning Focus
- Budget allocation
- Percentage calculations
- Comparison logic
- Warning systems

## Fintech Concepts
- **Budget**: Planned spending limit for a category
- **Budget Utilization**: How much of budget is used (%)
- **Budget Overspending**: When expenses exceed budget
- **Budget Tracking**: Monitoring spending vs planned amount

## Features to Build

Flow:
1. Ask category (Food, Transport, Shopping, Bills, Entertainment, Health)
2. Ask monthly budget amount
3. Save to budgets.txt
4. Show confirmation

Display Rich table:
- Category
- Budget Amount
- Spent (current month)
- Remaining
- Utilization % (with progress bar)
- Status (OK / Warning / Over)

Color coding:
- Green: Under 70% used
- Yellow: 70-100% used
- Red: Over 100% (overspending)


Display:
- Total monthly budget
- Total spent
- Total remaining
- Overall utilization %
- Categories over budget (highlighted)
- Recommendations

## Success Criteria

✅ Can set monthly budgets per category
✅ Can view budget vs actual spending
✅ Shows utilization percentage
✅ Highlights over-budget categories
✅ Shows progress bars
✅ Budget resets each month automatically
""",
    "features/analytics/GEMINI.md": """
## Financial Analytics Engine

## Goal
Analyze spending patterns and provide financial insights like real fintech apps.

## Learning Focus
- Data aggregation
- Statistical calculations
- Trend analysis
- Insight generation

## Fintech Concepts
- **Spending Pattern**: How money is distributed across categories
- **Burn Rate**: Average daily spending
- **Savings Rate**: % of income saved
- **Financial Health Score**: Overall financial wellness metric
- **Category Trends**: Which categories increasing/decreasing

## Features to Build

### 1. Spending Analysis

Display:
- Breakdown by category (pie chart in ASCII)
- Top 3 spending categories
- Average daily expense
- Comparison with last month
- Spending trends (up/down)

### 2. Income Analysis

Display:
- Income by source
- Total income this month
- Comparison with last month
- Income stability (regular vs irregular)

### 3. Savings Analysis

Display:
- Monthly savings amount
- Savings rate % (savings/income * 100)
- Savings trend (last 3 months)
- Savings goal progress (if set)

### 4. Financial Health Score

Calculate score (0-100) based on:
- Savings rate (30 points)
- Budget adherence (25 points)
- Income vs expenses (25 points)
- Debt management (20 points)

Display:
- Overall score with interpretation
- Score breakdown by factor
- Recommendations to improve score

Generate comprehensive report:
- Month overview
- Income summary
- Expense summary
- Budget performance
- Savings achieved
- Top transactions
- Trends
- Next month projections

# ASCII Pie Chart Example
'''bash
Spending by Category:
Food         ████████████ 40%
Transport    ██████ 20%
Shopping     ████████ 25%
Bills        ███ 10%
Other        █ 5%
'''

## Success Criteria

✅ Shows spending breakdown by category
✅ Calculates burn rate and savings rate
✅ Generates financial health score
✅ Compares current vs last month
✅ Creates comprehensive monthly report
✅ Provides actionable recommendations
""",
    "features/smart_assistant/GEMINI.md": """
# Smart Financial Assistant

## Goal
Add intelligent recommendations and proactive alerts like modern fintech apps.

## Learning Focus
- Rule-based recommendations
- Alert triggers
- Pattern detection
- Financial advice generation

## Fintech Concepts
- **Smart Alerts**: Proactive notifications about financial events
- **Spending Alerts**: When unusual spending detected
- **Budget Alerts**: When approaching budget limits
- **Savings Opportunities**: Finding ways to save money
- **Financial Tips**: Contextual advice based on behavior

## Features to Build

### 1. Daily Financial Check

Smart analysis showing:
- Today's spending so far
- Remaining daily budget (monthly budget / days)
- Alerts if any
- Quick tip for the day

Example:
📊 Daily Financial Check (Nov 14, 2025)

Today's Spending: Rs 1,250.00
Daily Budget: Rs 2,000.00 ✅
Remaining: Rs 750.00

⚠️  Alerts:
• Transport category at 85% budget (Rs 8,500 / Rs 10,000)
• Large transaction detected: Rs 5,000 (Shopping)

💡 Tip: You're on track! Consider moving Rs 500 to savings.

### 2. Smart Recommendations

Generate recommendations based on:
- Overspending categories → "Reduce Shopping by 20%"
- Low savings → "Try 50/30/20 rule"
- Irregular income → "Build 3-month emergency fund"
- No budget set → "Set budgets for better control"
- Good performance → "Increase savings goal"

### 3. Spending Alerts System

Show active alerts:
- Budget warnings (>80% used)
- Large transaction alerts (>20% of monthly income)
- Unusual spending patterns
- Bill payment reminders
- Savings milestones reached

### 4. Savings Opportunities

Analyze and suggest:
- Categories where spending can be reduced
- Estimate monthly savings potential
- Compare with category averages
- Show "What if" scenarios

### Allow setting goals:
- Emergency fund goal
- Savings target
- Debt payoff

###🎯 Goals Progress:
Emergency Fund
[████████░░] 80% (Rs 80,000 / Rs 100,000)
Expected: Dec 2025
Vacation Savings
[████░░░░░░] 40% (Rs 20,000 / Rs 50,000)
Expected: Mar 2026

## Success Criteria

✅ Daily financial check shows relevant info
✅ Smart recommendations based on actual behavior
✅ Proactive alerts for important events
✅ Savings opportunities identified
✅ Financial goals can be set and tracked
✅ All recommendations are actionable
""",
    "features/data_management/GEMINI.md": """
# Data Management & Export

## Goal
Professional data export, import, and backup features.

## Learning Focus
- Data export formats (CSV, JSON)
- Data import and validation
- Backup and restore
- Data integrity

## Fintech Concepts
- **Data Export**: Download financial data for external use
- **Data Portability**: Moving data between systems
- **Audit Trail**: Complete transaction history
- **Data Backup**: Protecting financial information

## Features to Build

### 1. Export Transactions

Export formats:
- CSV (for Excel/Sheets)
- JSON (for developers)
- PDF (coming later)

### 3. Export Monthly Report
Comprehensive JSON export with:
- All transactions
- Budget summary
- Analytics
- Health score
- Recommendations
### 3. Export Monthly Report
Comprehensive JSON export with:
- All transactions
- Budget summary
- Analytics
- Health score
- Recommendations

### 3. Export Monthly Report
Comprehensive JSON export with:
- All transactions
- Budget summary
- Analytics
- Health score
- Recommendations

### 4. Import Transactions

Features:
- Validate CSV format
- Check for duplicates
- Confirm before importing
- Show import summary

### 5. Backup System

Features:
- Create timestamped backup
- Compress files
- Store in backups/ folder
- Auto-cleanup old backups (keep last 10)

### 6. Data Validation

Check data integrity:
- Find corrupt entries
- Check for missing data
- Verify calculations
- Fix common issues

## Success Criteria

✅ Can export transactions to CSV
✅ Can export budgets
✅ Can export complete monthly reports
✅ Can import transactions from CSV
✅ Backup creates timestamped archive
✅ Restore works correctly
✅ Data validation finds issues
""",
    "frontend/GEMINI.md": """
## Web Dashboard & Final Polish (Instructions for Gemini)
### Objective

## Build a clean, simple, and professional one-page finance dashboard using Streamlit.
Focus on clarity, short code, easy readability, and maintainability.

## Web Dashboard Requirements
### 1. Balance Section

Display total balance in a large, centered, clean style.

Show income and expenses side by side.

Use green for income and red for expenses.

Keep layout minimal and neat.

### 2. Budget Progress Section

Create a list of budgets with:

Budget limit

Amount spent

Percentage used

Color-coded progress bars:

Green: under 70%

Yellow: 70%–99%

Red: 100%+

Use card-style boxes with clean spacing.

### 3. Recent Transactions Table

Show the last 10 transactions.

Columns: Date, Type, Category, Description, Amount.

Color code amount: income (green), expense (red).

Keep table simple, readable, and properly aligned.

## UI & Design Rules

Use card-based design (white boxes + soft shadow).

Max width ~1200px, centered layout.

Use clean fonts with generous spacing.

Mobile-responsive layout (cards stack on small screens).

Avoid complex CSS — keep structure simple and clean.

## Coding Style Guidelines for Gemini

Keep code short, simple, and easy to read.

Avoid unnecessary complexity or over-engineering.

Use clear variable names and small functions.

Ensure the dashboard loads fast and stays lightweight.

## Final Polish & Stability

Validate all loaded data.

Handle missing or corrupt files gracefully.

Ensure import/export code works before integrating.

Remove duplicate or unused functions.

Improve structure but keep logic simple.
"""
}

for filename, content in gemini_files.items():
    with st.expander(filename, expanded=False):
        st.markdown(content, unsafe_allow_html=True)
