import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="AI Personal Finance Advisor", layout="wide")

# -----------------------------
# Session state initialization
# -----------------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=["Date", "Category", "Description", "Amount"]
    )

if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 10000.0

# -----------------------------
# Helper functions
# -----------------------------
def calculate_summary(df: pd.DataFrame, budget: float):
    if df.empty:
        total_expense = 0.0
    else:
        total_expense = float(df["Amount"].sum())

    savings = max(budget - total_expense, 0)
    balance = budget - total_expense
    return total_expense, savings, balance


def generate_ai_insights(df: pd.DataFrame, budget: float):
    insights = []

    if df.empty:
        return [
            "No transactions added yet. Start by adding your daily expenses.",
            "Track spending regularly to get personalized financial insights.",
        ]

    total_expense = float(df["Amount"].sum())

    category_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    if total_expense > budget:
        insights.append("⚠️ You have exceeded your monthly budget.")
    elif total_expense > 0.8 * budget:
        insights.append("⚠️ You are close to your monthly budget limit.")
    else:
        insights.append("✅ Your spending is currently under control.")

    if not category_totals.empty:
        top_category = category_totals.idxmax()
        top_amount = category_totals.max()
        percent = (top_amount / total_expense) * 100 if total_expense > 0 else 0

        insights.append(
            f"📌 Your highest spending is in **{top_category}** (₹{top_amount:.2f}, {percent:.1f}% of total expenses)."
        )

        if percent > 40:
            insights.append(
                f"💡 You are spending a large share of your money on **{top_category}**. Consider reducing it."
            )

    avg_daily = 0
    if not df.empty:
        unique_days = df["Date"].nunique()
        if unique_days > 0:
            avg_daily = total_expense / unique_days

    insights.append(f"📊 Your average daily spending is **₹{avg_daily:.2f}**.")

    remaining = budget - total_expense
    if remaining > 0:
        insights.append(f"💰 You can still save **₹{remaining:.2f}** this month if you control spending.")
    else:
        insights.append("🚨 Your balance is negative. Try cutting optional expenses immediately.")

    return insights


def reset_all_data():
    st.session_state.transactions = pd.DataFrame(
        columns=["Date", "Category", "Description", "Amount"]
    )
    st.session_state.monthly_budget = 10000.0


# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Add Expense", "AI Insights", "Budget Planner", "Transaction History"]
)

# -----------------------------
# Title
# -----------------------------
st.title("AI Personal Finance Advisor (Student Version)")
st.write("Track expenses, manage budget, and get AI-based insights on your spending.")

# -----------------------------
# Common summary data
# -----------------------------
transactions_df = st.session_state.transactions
monthly_budget = st.session_state.monthly_budget
total_expense, savings, balance = calculate_summary(transactions_df, monthly_budget)

# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    st.subheader("Financial Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expenses", f"₹{total_expense:.2f}")
    c2.metric("Savings", f"₹{savings:.2f}")
    c3.metric("Balance", f"₹{balance:.2f}")

    st.write("### Quick Summary")
    st.write(f"**Monthly Budget:** ₹{monthly_budget:.2f}")

    if transactions_df.empty:
        st.info("No expense data available yet. Add expenses to view charts.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.write("### Expense Distribution by Category")
            category_data = transactions_df.groupby("Category")["Amount"].sum()

            fig1, ax1 = plt.subplots()
            ax1.pie(category_data, labels=category_data.index, autopct="%1.1f%%")
            ax1.set_title("Category-wise Expenses")
            st.pyplot(fig1)

        with col2:
            st.write("### Spending Over Time")
            daily_data = transactions_df.groupby("Date")["Amount"].sum().reset_index()

            fig2, ax2 = plt.subplots()
            ax2.plot(daily_data["Date"], daily_data["Amount"], marker="o")
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Amount (₹)")
            ax2.set_title("Daily Spending Trend")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

        st.write("### Recent Transactions")
        st.dataframe(transactions_df.tail(5), use_container_width=True)

# -----------------------------
# Add Expense
# -----------------------------
elif page == "Add Expense":
    st.subheader("Add a New Expense")

    with st.form("expense_form"):
        expense_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Rent", "Others"])
        description = st.text_input("Description")
        amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=10.0)

        submitted = st.form_submit_button("Add Expense")

        if submitted:
            if amount <= 0:
                st.warning("Please enter an amount greater than 0.")
            else:
                new_row = pd.DataFrame([{
                    "Date": expense_date,
                    "Category": category,
                    "Description": description.strip() if description else "No description",
                    "Amount": amount
                }])

                st.session_state.transactions = pd.concat(
                    [st.session_state.transactions, new_row],
                    ignore_index=True
                )

                st.success("Expense added successfully.")

    st.write("### Current Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expenses", f"₹{total_expense:.2f}")
    c2.metric("Savings", f"₹{savings:.2f}")
    c3.metric("Balance", f"₹{balance:.2f}")

# -----------------------------
# AI Insights
# -----------------------------
elif page == "AI Insights":
    st.subheader("AI Insights & Recommendations")

    insights = generate_ai_insights(transactions_df, monthly_budget)

    for insight in insights:
        st.write(f"- {insight}")

    if not transactions_df.empty:
        st.write("### Category Spending Analysis")
        category_totals = transactions_df.groupby("Category")["Amount"].sum().reset_index()
        st.dataframe(category_totals, use_container_width=True)

# -----------------------------
# Budget Planner
# -----------------------------
elif page == "Budget Planner":
    st.subheader("Monthly Budget Planner")

    new_budget = st.number_input(
        "Set Monthly Budget (₹)",
        min_value=0.0,
        value=float(st.session_state.monthly_budget),
        step=500.0
    )

    if st.button("Update Budget"):
        st.session_state.monthly_budget = new_budget
        st.success("Monthly budget updated successfully.")

    used_percent = 0
    if st.session_state.monthly_budget > 0:
        used_percent = min(total_expense / st.session_state.monthly_budget, 1.0)

    st.write(f"**Budget Used:** {used_percent * 100:.1f}%")
    st.progress(used_percent)

    if total_expense > st.session_state.monthly_budget:
        st.error("You have exceeded your budget.")
    elif total_expense > 0.8 * st.session_state.monthly_budget:
        st.warning("You are nearing your budget limit.")
    else:
        st.success("Your spending is within budget.")

    st.write(f"**Current Budget:** ₹{st.session_state.monthly_budget:.2f}")
    st.write(f"**Total Expenses:** ₹{total_expense:.2f}")
    st.write(f"**Remaining Balance:** ₹{balance:.2f}")

# -----------------------------
# Transaction History
# -----------------------------
elif page == "Transaction History":
    st.subheader("Transaction History")

    if transactions_df.empty:
        st.info("No transactions recorded yet.")
    else:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(transactions_df["Category"].unique())
        )

        filtered_df = transactions_df.copy()

        if filter_category != "All":
            filtered_df = filtered_df[filtered_df["Category"] == filter_category]

        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Transactions CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv"
        )

# -----------------------------
# Reset section
# -----------------------------
st.write("---")
st.subheader("Reset App Data")

confirm_reset = st.checkbox("I understand this will delete all current expense data.")

if st.button("Reset All Data"):
    if confirm_reset:
        reset_all_data()
        st.success("All expenses, savings, and balance data have been reset.")
    else:
        st.warning("Please confirm before resetting.")
