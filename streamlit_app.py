import streamlit as st
import pandas as pd
from datetime import datetime
import utils

st.set_page_config(layout="wide")

# Custom CSS for a cleaner, card-based UI
st.markdown("""
<style>
    .reportview-container .main .block-container{
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background-color: #f0f2f6;
    }
    .st-emotion-cache-1r6dm7w { /* This targets the card containers */
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .st-emotion-cache-zt5ig8 { /* Targets metric boxes */
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px 0 rgba(0, 0, 0, 0.03);
        margin-bottom: 10px;
    }
    .st-emotion-cache-10wls0b {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #303030;
    }
    .css-1lcbmhc, .css-1d391kg { /* Sidebar styling */
        background-color: white;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state data
utils.init_session_state_data()

def home_page():
    st.title("💰 Personal Finance Tracker Dashboard")
    st.write("Welcome to your personal finance dashboard!")
    
    transactions_df = utils.get_transactions_df()
    total_income, total_expenses, balance = utils.get_monthly_summary(transactions_df)

    st.subheader("Current Month Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Income", value=f"Rs {total_income / 100:,.2f}")
    with col2:
        st.metric(label="Total Expenses", value=f"Rs {total_expenses / 100:,.2f}")
    with col3:
        st.metric(label="Balance", value=f"Rs {balance / 100:,.2f}")

    st.subheader("Recent Transactions")
    if not transactions_df.empty:
        # Ensure 'Amount' column exists before formatting
        if 'Amount' in transactions_df.columns:
            st.dataframe(transactions_df.tail(10).style.format({"Amount": "Rs {:,.2f}"}), use_container_width=True)
        else:
            st.dataframe(transactions_df.tail(10), use_container_width=True)
    else:
        st.info("No transactions recorded yet.")

def transactions_page():
    st.title("💸 Transactions")

    st.header("Add New Transaction")
    with st.form("new_transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.now())
            type = st.radio("Type", ["Expense", "Income"])
            amount_input = st.number_input("Amount (in Rs)", min_value=0.01, format="%.2f")
        with col2:
            if type == "Expense":
                category = st.selectbox("Category", utils.get_transaction_categories())
            else:
                category = st.selectbox("Source", utils.get_income_sources())
            description = st.text_area("Description")

        submitted = st.form_submit_button("Add Transaction")
        if submitted:
            amount_paisa = int(amount_input * 100) # Convert to paisa/cents
            utils.save_transaction(date, type, category, amount_paisa, description)
            st.success("Transaction added successfully!")
            # No st.experimental_rerun() needed as session_state update triggers rerun

    st.header("All Transactions")
    transactions_df = utils.get_transactions_df()
    if not transactions_df.empty:
        # Display amount in Rs. for user
        if 'Amount' in transactions_df.columns:
            # Create a copy to avoid SettingWithCopyWarning when modifying 'Amount' for display
            display_df = transactions_df.copy()
            display_df["Amount"] = display_df["Amount"] / 100
            st.dataframe(display_df.style.format({"Amount": "Rs {:,.2f}"}), use_container_width=True)
        else:
            st.dataframe(transactions_df, use_container_width=True)
    else:
        st.info("No transactions recorded yet.")

def budgets_page():
    st.title("🎯 Budgets")

    st.header("Set Monthly Budget")
    with st.form("set_budget_form"):
        categories = utils.get_all_categories()
        category = st.selectbox("Category", categories)
        budget_amount_input = st.number_input("Monthly Budget Amount (in Rs)", min_value=0.01, format="%.2f")
        
        submitted = st.form_submit_button("Set Budget")
        if submitted:
            budget_amount_paisa = int(budget_amount_input * 100)
            utils.save_budget(category, budget_amount_paisa)
            st.success(f"Budget for {category} set to Rs {budget_amount_input:,.2f} successfully!")
            # No st.experimental_rerun() needed as session_state update triggers rerun

    st.header("Your Budgets")
    budgets_df = utils.get_budgets_df()
    transactions_df = utils.get_transactions_df()
    spent_by_category = utils.get_spent_by_category(transactions_df)

    if not budgets_df.empty:
        budget_summary = []
        for index, row in budgets_df.iterrows():
            category = row["Category"]
            budget = row["Budget"]
            spent = spent_by_category.get(category, 0)
            remaining = budget - spent
            utilization_percent = (spent / budget * 100) if budget > 0 else 0

            # Determine color for progress bar
            if utilization_percent < 70:
                color = "green"
            elif utilization_percent < 100:
                color = "orange"
            else:
                color = "red"
            
            budget_summary.append({
                "Category": category,
                "Budget": f"Rs {budget / 100:,.2f}",
                "Spent": f"Rs {spent / 100:,.2f}",
                "Remaining": f"Rs {remaining / 100:,.2f}",
                "Utilization": f"{utilization_percent:.2f}%",
                "Progress": utilization_percent,
                "Color": color
            })
        
        summary_df = pd.DataFrame(budget_summary)

        for index, row in summary_df.iterrows():
            st.markdown(f"#### {row['Category']}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Budget", row["Budget"])
            col2.metric("Spent", row["Spent"])
            col3.metric("Remaining", row["Remaining"])
            col4.metric("Utilization", row["Utilization"])
            
            st.progress(min(100, int(row["Progress"])))
            st.markdown(
                f'<style> .stProgress > div > div > div > div {{ background-color: {row["Color"]}; }} </style>', 
                unsafe_allow_html=True
            )
            
            if row["Progress"] >= 100:
                st.warning(f"⚠️ {row['Category']} is over budget!")
            st.markdown("---")

    else:
        st.info("No budgets set yet.")

def analytics_page():
    st.title("📈 Analytics")

    transactions_df = utils.get_transactions_df()

    if transactions_df.empty:
        st.info("No transactions recorded yet to perform analytics.")
        return

    st.header("Spending Analysis (Current Month)")
    spending_breakdown = utils.get_spending_breakdown(transactions_df)
    if not spending_breakdown.empty:
        st.subheader("Breakdown by Category")
        st.bar_chart(spending_breakdown)
        
        st.subheader("Top Spending Categories")
        for category, percentage in spending_breakdown.head(3).items():
            st.write(f"- {category}: {percentage:.2f}%")
    else:
        st.info("No expenses recorded for the current month.")

    st.header("Monthly Income vs. Expenses Trend")
    monthly_data = utils.get_monthly_spending_income(transactions_df)
    if not monthly_data.empty:
        monthly_data.index = monthly_data.index.astype(str) # Convert Period to string for plotting
        st.line_chart(monthly_data[["Income", "Spending"]])
    else:
        st.info("Not enough data to show monthly trends.")

    st.header("Savings Analysis (Current Month)")
    savings_rate = utils.calculate_savings_rate(transactions_df)
    st.metric(label="Savings Rate (Current Month)", value=f"{savings_rate:.2f}%")

def data_management_page():
    st.title("🗄️ Data Management")
    st.header("Export Data")

    st.subheader("Export Transactions to CSV")
    transactions_df = utils.get_transactions_df()
    csv_data = utils.get_transactions_as_csv(transactions_df)
    st.download_button(
        label="Download Transactions as CSV",
        data=csv_data,
        file_name="transactions.csv",
        mime="text/csv",
    )

# Sidebar for navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", ["Dashboard", "Transactions", "Budgets", "Analytics", "Data Management"])

# Display selected page
if selection == "Dashboard":
    home_page()
elif selection == "Transactions":
    transactions_page()
elif selection == "Budgets":
    budgets_page()
elif selection == "Analytics":
    analytics_page()
elif selection == "Data Management":
    data_management_page()
