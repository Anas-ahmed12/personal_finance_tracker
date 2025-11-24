import pandas as pd
from datetime import datetime
import os
import streamlit as st

TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"

def ensure_database_files_exist():
    """Ensures that the transactions.txt and budgets.txt files exist and have headers."""
    os.makedirs(os.path.dirname(TRANSACTIONS_FILE), exist_ok=True)
    
    # Ensure transactions.txt exists and has a header
    if not os.path.exists(TRANSACTIONS_FILE) or os.path.getsize(TRANSACTIONS_FILE) == 0:
        with open(TRANSACTIONS_FILE, "w") as f:
            f.write("Date,Type,Category,Amount,Description\n") # Header for transactions
    
    # Ensure budgets.txt exists and has a header
    if not os.path.exists(BUDGETS_FILE) or os.path.getsize(BUDGETS_FILE) == 0:
        with open(BUDGETS_FILE, "w") as f:
            f.write("Category,Budget\n") # Header for budgets

def _load_transactions_from_file():
    """
    Loads transactions from the CSV file into a pandas DataFrame with robust error handling.

    This function ensures that:
    - The file and its headers are created if they don't exist.
    - All expected columns ('Date', 'Type', 'Category', 'Amount', 'Description') are present.
    - 'Date' column is parsed as datetime, and rows with invalid dates are dropped.
    - 'Amount' column is parsed as numeric, with invalid values converted to 0.
    - Other columns are filled with empty strings if they have missing values.
    - Warnings are logged for problematic rows without crashing the application.
    """
    ensure_database_files_exist()
    
    expected_columns = ["Date", "Type", "Category", "Amount", "Description"]
    
    try:
        df = pd.read_csv(TRANSACTIONS_FILE, on_bad_lines='skip', engine='python')
    except pd.errors.EmptyDataError:
        # If the file is completely empty, return a correctly structured empty DataFrame
        return pd.DataFrame(columns=expected_columns)
    except FileNotFoundError:
        # This is a fallback, as ensure_database_files_exist should prevent this
        st.error(f"File not found: {TRANSACTIONS_FILE}")
        return pd.DataFrame(columns=expected_columns)

    # --- Data Cleaning and Validation ---

    # 1. Ensure all expected columns exist, filling missing ones with appropriate nulls
    df = df.reindex(columns=expected_columns)

    # 2. Clean up 'Date' column
    original_rows = len(df)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Identify and log rows with invalid dates before dropping them
    invalid_date_rows = df[df['Date'].isna()]
    if not invalid_date_rows.empty:
        st.warning("Warning: Found and removed rows with invalid or missing dates.")
        # To avoid cluttering the UI, you might only show a few examples
        st.dataframe(invalid_date_rows.head())
        
    df.dropna(subset=['Date'], inplace=True)
    
    if len(df) < original_rows:
        print(f"Log: Removed {original_rows - len(df)} rows due to invalid dates.")


    # 3. Clean up 'Amount' column
    # Identify rows where 'Amount' is not a valid number before coercion
    invalid_amount_mask = pd.to_numeric(df['Amount'], errors='coerce').isna()
    problematic_rows = df[invalid_amount_mask]
    
    if not problematic_rows.empty:
        st.warning("Warning: Found rows with invalid 'Amount'. These have been set to 0.")
        st.dataframe(problematic_rows.head())

    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0).astype(int)

    # 4. Clean up 'Type', 'Category', and 'Description'
    for col in ['Type', 'Category', 'Description']:
        # Ensure column is of string type to handle potential float inputs gracefully
        df[col] = df[col].astype(str).fillna('')
        if col == 'Type':
            # Standardize the 'Type' column to title case (e.g., 'income' -> 'Income')
            df[col] = df[col].str.title()

    # Reset index after dropping rows
    df.reset_index(drop=True, inplace=True)
    
    return df

def _load_budgets_from_file():
    """Loads budgets from budgets.txt into a pandas DataFrame."""
    ensure_database_files_exist()
    try:
        df = pd.read_csv(BUDGETS_FILE)
        # Ensure 'Budget' column is numeric
        df["Budget"] = pd.to_numeric(df["Budget"], errors='coerce').fillna(0).astype(int)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["Category", "Budget"])
    except Exception as e:
        st.error(f"Error loading budgets from file: {e}. Returning empty DataFrame with expected columns.")
        return pd.DataFrame(columns=["Category", "Budget"])

def init_session_state_data():
    """Initializes transactions and budgets DataFrames in Streamlit's session state."""
    if "transactions_df" not in st.session_state:
        st.session_state.transactions_df = _load_transactions_from_file()
    if "budgets_df" not in st.session_state:
        st.session_state.budgets_df = _load_budgets_from_file()

def get_transactions_df():
    """Returns the transactions DataFrame from session state."""
    init_session_state_data()
    return st.session_state.transactions_df

def get_budgets_df():
    """Returns the budgets DataFrame from session state."""
    init_session_state_data()
    return st.session_state.budgets_df

def save_transaction(date, type, category, amount, description):
    """Adds a new transaction to the session state DataFrame and saves it to file."""
    # Convert date to pandas Timestamp to ensure consistent datetime type
    date = pd.to_datetime(date)
    new_transaction = pd.DataFrame([{
        "Date": date,
        "Type": type,
        "Category": category,
        "Amount": amount,
        "Description": description
    }])
    st.session_state.transactions_df = pd.concat([st.session_state.transactions_df, new_transaction], ignore_index=True)
    st.session_state.transactions_df.to_csv(TRANSACTIONS_FILE, index=False)

def save_budget(category, budget_amount):
    """Saves or updates a budget to the session state DataFrame and saves it to file."""
    budgets_df = st.session_state.budgets_df
    if category in budgets_df["Category"].values:
        budgets_df.loc[budgets_df["Category"] == category, "Budget"] = budget_amount
    else:
        new_budget = pd.DataFrame([{"Category": category, "Budget": budget_amount}])
        budgets_df = pd.concat([budgets_df, new_budget], ignore_index=True)
    st.session_state.budgets_df = budgets_df
    st.session_state.budgets_df.to_csv(BUDGETS_FILE, index=False)

def get_transaction_categories():
    """Returns a list of predefined transaction categories."""
    return ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]

def get_income_sources():
    """Returns a list of predefined income sources."""
    return ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

def get_all_categories():
    """Returns all possible categories for budgets (union of transaction categories and income sources)."""
    return sorted(list(set(get_transaction_categories() + get_income_sources())))

def get_monthly_summary(df):
    """Calculates monthly income, expenses, and balance for the current month."""
    if df.empty or 'Date' not in df.columns or 'Amount' not in df.columns:
        return 0, 0, 0
    current_month_transactions = df[df["Date"].dt.to_period("M") == pd.Timestamp.now().to_period("M")]
    
    total_income = current_month_transactions[current_month_transactions["Type"] == "Income"]["Amount"].sum()
    total_expenses = current_month_transactions[current_month_transactions["Type"] == "Expense"]["Amount"].sum()
    
    balance = total_income - total_expenses
    return total_income, total_expenses, balance

def get_spending_by_category(df):
    """Calculates spending by category for the current month."""
    if df.empty or 'Date' not in df.columns or 'Amount' not in df.columns:
        return pd.Series(dtype=float)
    current_month_transactions = df[(df["Date"].dt.to_period("M") == pd.Timestamp.now().to_period("M")) & (df["Type"] == "Expense")]
    return current_month_transactions.groupby("Category")["Amount"].sum().sort_values(ascending=False)

def get_spent_by_category(transactions_df):
    """Calculates the total amount spent for each category in the current month."""
    if transactions_df.empty or 'Date' not in transactions_df.columns or 'Amount' not in transactions_df.columns:
        return {}
    current_month = pd.Timestamp.now().to_period("M")
    spent_df = transactions_df[(transactions_df["Type"] == "Expense") & 
                               (transactions_df["Date"].dt.to_period("M") == current_month)]
    return spent_df.groupby("Category")["Amount"].sum().to_dict()

def get_monthly_spending_income(df):
    """Calculates total spending and income for each month."""
    if df.empty or 'Date' not in df.columns or 'Amount' not in df.columns:
        return pd.DataFrame(columns=["Spending", "Income"])
    # Ensure 'Month' column is created before grouping
    temp_df = df.copy()
    temp_df["Month"] = temp_df["Date"].dt.to_period("M")
    monthly_data = temp_df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)
    monthly_data["Spending"] = monthly_data.get("Expense", 0)
    monthly_data["Income"] = monthly_data.get("Income", 0)
    return monthly_data[["Spending", "Income"]]

def calculate_savings_rate(df):
    """Calculates the savings rate for the current month."""
    total_income, total_expenses, _ = get_monthly_summary(df)
    if total_income > 0:
        savings = total_income - total_expenses
        return (savings / total_income) * 100
    return 0

def get_spending_breakdown(df):
    """Returns a breakdown of spending by category for the current month."""
    if df.empty or 'Date' not in df.columns or 'Amount' not in df.columns:
        return pd.Series(dtype=float)
    current_month_transactions = df[(df["Date"].dt.to_period("M") == pd.Timestamp.now().to_period("M")) & (df["Type"] == "Expense")]
    total_spending = current_month_transactions["Amount"].sum()
    if total_spending == 0:
        return pd.Series(dtype=float)
    
    breakdown = current_month_transactions.groupby("Category")["Amount"].sum()
    return (breakdown / total_spending * 100).sort_values(ascending=False)

def get_transactions_as_csv(transactions_df):
    """Returns all transactions as a CSV string."""
    df_copy = transactions_df.copy()
    df_copy["Amount"] = df_copy["Amount"] / 100 # Convert back to Rs for export
    return df_copy.to_csv(index=False)