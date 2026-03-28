import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import os

st.set_page_config(page_title="AI Personal Finance Advisor", layout="wide")

# -----------------------------
# File storage
# -----------------------------
TRANSACTIONS_FILE = "transactions.csv"
STATE_FILE = "finance_state.csv"

# -----------------------------
# Custom dark colorful styling
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1020 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    p, label, div {
        color: #cbd5e1;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30,41,59,0.95), rgba(17,24,39,0.95));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 18px 14px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.25);
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 15px !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    .card {
        background: linear-gradient(135deg, rgba(30,41,59,0.92), rgba(15,23,42,0.92));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 22px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.30);
        margin-bottom: 18px;
    }

    .summary-chip {
        display: inline-block;
        padding: 10px 16px;
        margin: 6px 8px 6px 0;
        border-radius: 999px;
        font-weight: 600;
        font-size: 14px;
        color: white;
    }

    .chip-blue { background: linear-gradient(90deg, #2563eb, #3b82f6); }
    .chip-green { background: linear-gradient(90deg, #059669, #10b981); }
    .chip-pink { background: linear-gradient(90deg, #db2777, #f472b6); }
    .chip-purple { background: linear-gradient(90deg, #7c3aed, #a855f7); }

    .insight-box {
        background: linear-gradient(135deg, rgba(37,99,235,0.15), rgba(168,85,247,0.12));
        border: 1px solid rgba(96,165,250,0.25);
        border-radius: 18px;
        padding: 14px 16px;
        margin-bottom: 10px;
        color: #e2e8f0;
        font-weight: 500;
    }

    .stButton>button {
        border-radius: 14px;
        border: none;
        background: linear-gradient(90deg, #2563eb, #8b5cf6);
        color: white;
        font-weight: 700;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 6px 20px rgba(37,99,235,0.30);
    }

    .stButton>button:hover {
        background: linear-gradient(90deg, #1d4ed8, #7c3aed);
        color: white;
    }

    .stDownloadButton>button {
        border-radius: 14px;
        border: none;
        background: linear-gradient(90deg, #059669, #10b981);
        color: white;
        font-weight: 700;
    }

    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stDateInput input,
    .stSelectbox>div>div,
    .stTextArea textarea {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        color: #f8fafc !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    .stDataFrame, div[data-testid="stTable"] {
        background: rgba(15,23,42,0.92);
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        overflow: hidden;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    .small-muted {
        color: #94a3b8;
        font-size: 15px;
        margin-top: -8px;
        margin-bottom: 12px;
    }

    hr {
        border-color: rgba(255,255,255,0.08);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Persistence helpers
# -----------------------------
def load_transactions():
    if os.path.exists(TRANSACTIONS_FILE):
        df = pd.read_csv(TRANSACTIONS_FILE)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"]).dt.date
        return df
    return pd.DataFrame(columns=["Date", "Category", "Description", "Amount"])


def save_transactions():
    st.session_state.transactions.to_csv(TRANSACTIONS_FILE, index=False)


def load_state():
    if os.path.exists(STATE_FILE):
        df = pd.read_csv(STATE_FILE)
        if not df.empty:
            return float(df.loc[0, "total_balance"]), float(df.loc[0, "savings"])
    return 0.0, 0.0


def save_state():
    pd.DataFrame([{
        "total_balance": st.session_state.total_balance,
        "savings": st.session_state.savings
    }]).to_csv(STATE_FILE, index=False)


# -----------------------------
# Session state initialization
# -----------------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = load_transactions()

if "total_balance" not in st.session_state or "savings" not in st.session_state:
    total_balance_loaded, savings_loaded = load_state()
    st.session_state.total_balance = total_balance_loaded
    st.session_state.savings = savings_loaded

# -----------------------------
# Helper functions
# -----------------------------
def calculate_summary(df: pd.DataFrame, total_balance: float, savings: float):
    if df.empty:
        total_expense = 0.0
    else:
        total_expense = float(df["Amount"].sum())

    available_for_spending = total_balance - savings
    remaining_for_spending = available_for_spending - total_expense
    current_balance = total_balance - total_expense

    return total_expense, available_for_spending, remaining_for_spending, current_balance


def generate_ai_insights(df: pd.DataFrame, total_balance: float, savings: float):
    insights = []

    if df.empty:
        return [
            "No transactions added yet. Start by adding your daily expenses.",
            "Whenever you add money, 35% is automatically protected as savings.",
        ]

    total_expense = float(df["Amount"].sum())
    available_for_spending = total_balance - savings
    category_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    if total_expense > available_for_spending:
        insights.append("⚠️ You have spent more than your available spending amount.")
    elif total_expense > 0.8 * available_for_spending and available_for_spending > 0:
        insights.append("⚠️ You are close to your spending limit.")
    else:
        insights.append("✅ Your spending is under control.")

    if not category_totals.empty:
        top_category = category_totals.idxmax()
        top_amount = category_totals.max()
        percent = (top_amount / total_expense) * 100 if total_expense > 0 else 0

        insights.append(
            f"📌 Highest spending is in {top_category} (₹{top_amount:.2f}, {percent:.1f}% of total expenses)."
        )

        if percent > 40:
            insights.append(
                f"💡 A large portion of your money is going to {top_category}. Try reducing it."
            )

    unique_days = df["Date"].nunique()
    avg_daily = total_expense / unique_days if unique_days > 0 else 0
    insights.append(f"📊 Your average daily spending is ₹{avg_daily:.2f}.")
    remaining = available_for_spending - total_expense

    if remaining > 0:
        insights.append(f"💰 You still have ₹{remaining:.2f} left for spending.")
    else:
        insights.append("🚨 Your available spending amount is exhausted.")

    return insights


def reset_all_data():
    st.session_state.transactions = pd.DataFrame(
        columns=["Date", "Category", "Description", "Amount"]
    )
    st.session_state.total_balance = 0.0
    st.session_state.savings = 0.0

    save_transactions()
    save_state()


# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.markdown("## 💸 Finance Advisor")
st.sidebar.markdown("<div class='small-muted'>For Students</div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Money", "Add Expense", "AI Insights", "Transaction History"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class='card' style='padding:16px; background: linear-gradient(135deg, rgba(37,99,235,0.22), rgba(16,185,129,0.18));'>
    <div style='font-weight:800; color:white; font-size:18px;'>AI-Powered Insights</div>
    <div style='color:#dbeafe; margin-top:6px;'>Get smart suggestions to save more and spend better.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# App title
# -----------------------------
st.markdown("## Dashboard")
st.markdown("<div class='small-muted'>Overview of your finances</div>", unsafe_allow_html=True)

# -----------------------------
# Common summary data
# -----------------------------
transactions_df = st.session_state.transactions
total_balance = st.session_state.total_balance
savings = st.session_state.savings

total_expense, available_for_spending, remaining_for_spending, current_balance = calculate_summary(
    transactions_df, total_balance, savings
)

# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💼 Total Balance", f"₹{total_balance:.2f}")
    c2.metric("🪙 Savings (35%)", f"₹{savings:.2f}")
    c3.metric("💳 Total Expenses", f"₹{total_expense:.2f}")
    c4.metric("✨ Remaining Spending", f"₹{remaining_for_spending:.2f}")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Money Summary", unsafe_allow_html=True)
    st.markdown(
        f"""
        <span class='summary-chip chip-blue'>Available for Spending: ₹{available_for_spending:.2f}</span>
        <span class='summary-chip chip-green'>Current Balance: ₹{current_balance:.2f}</span>
        <span class='summary-chip chip-pink'>Expenses: ₹{total_expense:.2f}</span>
        <span class='summary-chip chip-purple'>Savings: ₹{savings:.2f}</span>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if transactions_df.empty:
        st.info("No expense data available yet. Add money and expenses to see charts.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Expense Breakdown")
            category_data = transactions_df.groupby("Category")["Amount"].sum()

            fig1, ax1 = plt.subplots()
            fig1.patch.set_facecolor("#0f172a")
            ax1.set_facecolor("#0f172a")
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#a855f7", "#f472b6"]
            ax1.pie(category_data, labels=category_data.index, autopct="%1.1f%%", colors=colors)
            for text in ax1.texts:
                text.set_color("white")
            ax1.set_title("Category-wise Expenses", color="white")
            st.pyplot(fig1)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Spending Trend")
            daily_data = transactions_df.groupby("Date")["Amount"].sum().reset_index()

            fig2, ax2 = plt.subplots()
            fig2.patch.set_facecolor("#0f172a")
            ax2.set_facecolor("#0f172a")
            ax2.plot(daily_data["Date"], daily_data["Amount"], marker="o", linewidth=3, color="#3b82f6")
            ax2.fill_between(daily_data["Date"], daily_data["Amount"], alpha=0.25, color="#3b82f6")
            ax2.set_xlabel("Date", color="white")
            ax2.set_ylabel("Amount (₹)", color="white")
            ax2.set_title("Daily Spending Trend", color="white")
            ax2.tick_params(colors="white")
            for spine in ax2.spines.values():
                spine.set_color("#334155")
            plt.xticks(rotation=45)
            st.pyplot(fig2)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("### Recent Transactions")
        st.dataframe(transactions_df.tail(5), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Add Money
# -----------------------------
elif page == "Add Money":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### Add Money")

    new_amount = st.number_input(
        "Enter Amount (₹)",
        min_value=0.0,
        value=0.0,
        step=100.0
    )

    if st.button("Add Money"):
        if new_amount > 0:
            savings_part = 0.35 * new_amount
            spending_part = 0.65 * new_amount

            st.session_state.total_balance += new_amount
            st.session_state.savings += savings_part
            save_state()

            st.success(
                f"₹{new_amount:.2f} added successfully. ₹{savings_part:.2f} moved to savings and ₹{spending_part:.2f} kept for spending."
            )
        else:
            st.warning("Please enter an amount greater than 0.")

    st.markdown(
        f"""
        <span class='summary-chip chip-blue'>Total Balance: ₹{st.session_state.total_balance:.2f}</span>
        <span class='summary-chip chip-green'>Savings: ₹{st.session_state.savings:.2f}</span>
        <span class='summary-chip chip-purple'>Available: ₹{st.session_state.total_balance - st.session_state.savings:.2f}</span>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Add Expense
# -----------------------------
elif page == "Add Expense":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### Add a New Expense")

    with st.form("expense_form"):
        expense_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Rent", "Others"])
        description = st.text_input("Description")
        amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=10.0)

        submitted = st.form_submit_button("Add Expense")

        if submitted:
            if amount <= 0:
                st.warning("Please enter an amount greater than 0.")
            elif amount > remaining_for_spending:
                st.error("This expense is greater than your remaining spending amount.")
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
                save_transactions()
                st.success("Expense added successfully.")

    st.markdown(
        f"""
        <span class='summary-chip chip-blue'>Total Balance: ₹{total_balance:.2f}</span>
        <span class='summary-chip chip-green'>Savings: ₹{savings:.2f}</span>
        <span class='summary-chip chip-pink'>Expenses: ₹{total_expense:.2f}</span>
        <span class='summary-chip chip-purple'>Remaining Spending: ₹{remaining_for_spending:.2f}</span>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# AI Insights
# -----------------------------
elif page == "AI Insights":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### AI Insights & Recommendations")

    insights = generate_ai_insights(transactions_df, total_balance, savings)
    for insight in insights:
        st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

    if not transactions_df.empty:
        st.write("### Category Spending Analysis")
        category_totals = transactions_df.groupby("Category")["Amount"].sum().reset_index()
        st.dataframe(category_totals, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Transaction History
# -----------------------------
elif page == "Transaction History":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### Transaction History")

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
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Reset section
# -----------------------------
st.write("---")
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.write("### Reset App Data")

confirm_reset = st.checkbox("I understand this will delete all current finance data.")

if st.button("Reset All Data"):
    if confirm_reset:
        reset_all_data()
        st.success("All balance, savings, and expense data have been reset.")
    else:
        st.warning("Please confirm before resetting.")
st.markdown("</div>", unsafe_allow_html=True)
