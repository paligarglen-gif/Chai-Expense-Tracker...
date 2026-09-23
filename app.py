import json
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


@st.cache_resource
def init_connection():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]

  # Direktang basahin mula sa Streamlit Secrets
  creds_dict = json.loads(st.secrets["gcp_json"])
  if "private_key" in creds_dict:
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

  creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
  client = gspread.authorize(creds)
  return client


client = init_connection()

# Coquette Custom CSS Styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Quicksand:wght@400;500;600&display=swap');

    .stApp {
        background: linear-gradient(135deg, #FFF0F3 0%, #FFE4E9 50%, #FADADD 100%);
        font-family: 'Quicksand', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Dancing Script', cursive !important;
        color: #B54565 !important;
        letter-spacing: 0.5px;
    }
    
    h1 {
        font-size: 3rem !important;
    }

    div[data-testid="stSidebar"] {
        background-color: #FFE8ED !important;
        border-right: 2px solid #FADADD;
    }

    div[data-testid="stForm"] {
        background-color: #FFF5F7;
        border: 2px solid #FADADD;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(217, 136, 185, 0.15);
    }

    div.stMetric {
        background-color: #FFFFFF;
        border: 1px solid #FADADD;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(217, 136, 185, 0.1);
        text-align: center;
    }
    
    div.stMetric label {
        font-size: 0.9rem !important;
        color: #9C5570 !important;
    }

    div.stMetric [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        color: #B54565 !important;
        font-weight: 700 !important;
    }

    .stButton>button {
        background-color: #E8A4B8;
        color: #FFFFFF;
        border: 1px solid #D988B9;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #D988B9;
        color: #FFFFFF;
        border-color: #B54565;
    }

    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px;
        border: 1px solid #E8A4B8;
        background-color: #FFF0F3;
        color: #7A4960;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# Google Sheets Connection Setup
# Google Sheets Connection Setup
@st.cache_resource
def init_connection():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]
  try:
   if "gcp_service_account_json" in st.secrets:
      creds_dict = dict(st.secrets["gcp_service_account_json"])
      creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
   else:
      creds = Credentials.from_service_account_file(
          "credentials.json", scopes=scope
      )
  except Exception:
    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=scope
    )

  client = gspread.authorize(creds)
  return client

def load_data():
    try:
        client = init_connection()
        sheet = client.open("chai_transactions").sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        expected_columns = [
            "ID",
            "Date",
            "Type",
            "Platform",
            "Category",
            "Description",
            "Amount",
            "Puhunan",
            "Tubo",
            "Payout Cycle",
            "Due Date",
        ]
        if df.empty:
            return pd.DataFrame(columns=expected_columns)

        for col in expected_columns:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        return pd.DataFrame(columns=[
            "ID", "Date", "Type", "Platform", "Category", 
            "Description", "Amount", "Puhunan", "Tubo", "Payout Cycle", "Due Date"
        ])


def save_data_to_sheet(df):
    try:
        client = init_connection()
        sheet = client.open("chai_transactions").sheet1
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"Error saving to Google Sheet: {e}")


# App Header
st.title("🎀 Chai Expenses Tracker")
st.markdown(
    "<p style='color: #9C5570; font-family: Quicksand, sans-serif; font-style: italic; font-size: 1.1rem;'>Keep your boutique, affiliate income & personal finances organized safely. ✨</p>",
    unsafe_allow_html=True,
)

# Sidebar for Adding Entries
st.sidebar.header("🩰 Add New Entry")

trans_type = st.sidebar.selectbox(
    "Transaction Type",
    [
        "Sales (Income)",
        "Affiliate Income",
        "Savings Deposit",
        "Personal Expense",
        "Business Expense",
        "Business Withdrawal",
        "Loan",
    ],
    key="trans_type_selectbox",
)

with st.sidebar.form("expense_form", clear_on_submit=True):
    date = st.date_input("Date")
    platform = st.selectbox(
        "Platform / Source",
        ["TikTok Shop", "Shopee", "Manual / Direct", "Personal", "Bank / Piggy Bank"],
        key="platform_selectbox",
    )
    category = st.selectbox(
        "Category",
        [
            "Affiliate Payout",
            "Food & Baon",
            "Transport",
            "Clothing & Boutique",
            "Supplies",
            "Operations",
            "Savings",
            "Loans",
            "Other",
        ],
        key="category_selectbox",
    )
    description = st.text_input(
        "Description (e.g., Monthly piggy bank savings, Emergency fund)",
        key="desc_input",
    )

    payout_cycle = "N/A"
    due_date = "N/A"
    puhunan = 0.0
    tubo = 0.0
    final_amount = 0.0

    if trans_type == "Sales (Income)":
        sales_amount = st.number_input(
            "Daily Sales Income (₱)", min_value=0.0, format="%.2f", key="sales_val"
        )
        puhunan = st.number_input(
            "Puhunan / Capital (₱)", min_value=0.0, format="%.2f", key="puhunan_val"
        )
        tubo = sales_amount - puhunan
        final_amount = sales_amount
        st.markdown(
            f"<p style='color: #B54565; font-family: Quicksand, sans-serif; font-weight: bold;'>Calculated Tubo (Profit): ₱{tubo:,.2f} ✨</p>",
            unsafe_allow_html=True,
        )
    elif trans_type == "Affiliate Income":
        final_amount = st.number_input(
            "Expected Affiliate Earnings (₱)",
            min_value=0.0,
            format="%.2f",
            key="aff_val",
        )
        payout_cycle = st.selectbox(
            "Expected Payout Cycle Date",
            ["15th of the Month", "30th of the Month"],
            key="payout_selectbox",
        )
    elif trans_type in [
        "Savings Deposit",
        "Personal Expense",
        "Business Expense",
        "Business Withdrawal",
        "Loan",
    ]:
        if trans_type == "Savings Deposit":
            label_text = "Savings Amount (₱)"
        elif trans_type == "Business Withdrawal":
            label_text = "Withdrawal Amount (₱)"
        else:
            label_text = "Expense / Payment Amount (₱)"

        final_amount = st.number_input(
            label_text, min_value=0.0, format="%.2f", key="expense_val"
        )
        if trans_type == "Loan":
            due_date = st.selectbox(
                "Loan Due Date",
                [
                    "15th of the Month",
                    "30th of the Month",
                    "Every 15th",
                    "Every End of Month",
                    "Custom / One-time",
                ],
                key="due_date_select",
            )

    submitted = st.form_submit_button("Add Entry ✨")
    if submitted:
        df_existing = load_data()

        new_id = (
            int(df_existing["ID"].max() + 1)
            if not df_existing.empty
            and "ID" in df_existing.columns
            and not pd.isna(df_existing["ID"].max())
            else 1
        )

        new_row = pd.DataFrame([{
            "ID": new_id,
            "Date": str(date),
            "Type": trans_type,
            "Platform": platform,
            "Category": category,
            "Description": description,
            "Amount": final_amount,
            "Puhunan": puhunan,
            "Tubo": tubo,
            "Payout Cycle": payout_cycle,
            "Due Date": due_date,
        }])

        df_updated = pd.concat([df_existing, new_row], ignore_index=True)
        save_data_to_sheet(df_updated)

        st.sidebar.success("Added and saved safely to Google Sheets! 🩰")
        st.rerun()

# Load Data for Display
df = load_data()

if not df.empty and "Date" in df.columns:
    df["Datetime"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month-Year"] = df["Datetime"].dt.strftime("%B %Y")

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Tubo"] = pd.to_numeric(df["Tubo"], errors="coerce").fillna(0)

    # Calculations: Business
    biz_sales = df[df["Type"] == "Sales (Income)"]["Amount"].sum()
    biz_expenses = df[df["Type"] == "Business Expense"]["Amount"].sum()
    biz_withdrawals = df[df["Type"] == "Business Withdrawal"]["Amount"].sum()
    total_tubo = df["Tubo"].sum()

    remaining_business = biz_sales - biz_expenses - biz_withdrawals

    # Calculations: Personal, Savings & Affiliate
    aff_income = df[df["Type"] == "Affiliate Income"]["Amount"].sum()
    savings_total = df[df["Type"] == "Savings Deposit"]["Amount"].sum()
    personal_expenses = df[df["Type"].isin(["Personal Expense", "Loan"])]["Amount"].sum()

    remaining_personal = aff_income - personal_expenses - savings_total

    # Section 1: Business Overview
    st.subheader("🛍️ Business Dashboard (Chai Co. & Boutique)")
    b1, b2, b3, b4, b5 = st.columns(5)
    b1.metric("Business Sales", f"₱{biz_sales:,.2f}")
    b2.metric("Business Expenses", f"₱{biz_expenses:,.2f}")
    b3.metric("Withdrawals", f"₱{biz_withdrawals:,.2f}")
    b4.metric("Total Tubo", f"₱{total_tubo:,.2f}")
    b5.metric("Remaining Biz Fund", f"₱{remaining_business:,.2f}")

    st.write("")

    # Section 2: Personal, Savings & Affiliate Overview
    st.subheader("🌸 Personal, Savings & Affiliate Dashboard")
    p1, p2, p3, p4, p5 = st.columns(5)
    p1.metric("Affiliate Income", f"₱{aff_income:,.2f}")
    p2.metric("Total Savings", f"₱{savings_total:,.2f}")
    p3.metric("Personal Exp.", f"₱{personal_expenses:,.2f}")
    p4.metric("Net Available", f"₱{(aff_income - personal_expenses):,.2f}")
    p5.metric("Remaining Personal", f"₱{remaining_personal:,.2f}")

    # Section 3: Monthly Savings Breakdown
    st.write("---")
    st.subheader("📅 Monthly Savings & Financial Summary")

    monthly_summary = []
    for month_yr, group in df.groupby("Month-Year"):
        if pd.isna(month_yr):
            continue
        m_income = group[group["Type"].isin(["Sales (Income)", "Affiliate Income"])]["Amount"].sum()
        m_savings = group[group["Type"] == "Savings Deposit"]["Amount"].sum()
        m_expenses = group[group["Type"].isin(["Personal Expense", "Business Expense", "Loan"])]["Amount"].sum()
        monthly_summary.append({
            "Month": month_yr,
            "Total Incomes (₱)": m_income,
            "Total Savings (₱)": m_savings,
            "Total Expenses & Loans (₱)": m_expenses,
        })

    if monthly_summary:
        monthly_df = pd.DataFrame(monthly_summary)
        st.dataframe(monthly_df, use_container_width=True, hide_index=True)

# Quick Calculator Section
st.write("---")
st.subheader("🧮 Quick Calculator")
with st.expander("✨ Open Calculator for Quick Math"):
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    with calc_col1:
        num1 = st.number_input("First Value (₱)", value=0.0, format="%.2f", key="calc_num1")
    with calc_col2:
        operation = st.selectbox(
            "Operation",
            ["Addition (+)", "Subtraction (-)", "Multiplication (×)", "Division (÷)"],
            key="calc_op"
        )
    with calc_col3:
        num2 = st.number_input("Second Value (₱)", value=0.0, format="%.2f", key="calc_num2")

    if operation == "Addition (+)":
        calc_result = num1 + num2
    elif operation == "Subtraction (-)":
        calc_result = num1 - num2
    elif operation == "Multiplication (×)":
        calc_result = num1 * num2
    else:
        calc_result = num1 / num2 if num2 != 0 else 0.0

    st.markdown(
        f"<p style='color: #B54565; font-family: Quicksand, sans-serif; font-weight: bold; font-size: 1.2rem; text-align: center;'>Result: ₱{calc_result:,.2f} ✨</p>",
        unsafe_allow_html=True,
    )

# Transaction History Section
st.write("---")
st.subheader("📋 Transaction History")

try:
  client = init_connection()
  sheet = client.open("chai_transactions").sheet1
  data = sheet.get_all_records()

  if data:
    df = pd.DataFrame(data)
    edited_df = st.data_editor(
        df.drop(columns=["Datetime", "Month-Year"], errors="ignore"),
        num_rows="dynamic",
        key="transaction_editor",
        use_container_width=True,
        hide_index=True,
    )

    col_save_space, col_save_btn = st.columns([3, 1])
    with col_save_btn:
      if st.button("Save Changes / Delete 💾"):
        cleaned_df = edited_df.drop(
            columns=["Datetime", "Month-Year"], errors="ignore"
        )
        save_data_to_sheet(cleaned_df)
        st.success(
            "Changes saved permanently to Google Sheets and secured for years! 🩰"
        )
        st.rerun()
  else:
    st.info(
        "Your ledger is currently empty. Add your first record using the"
        " sidebar on the left! 🌸"
    )
except Exception as e:
  st.error(f"Error loading transaction history: {e}")
  # Coquette Motivational Quote Footer
st.write("---")
st.markdown(
    """
    <div style='text-align: center; font-family: "Dancing Script", cursive; font-size: 1.8rem; color: #b0578c; padding: 10px;'>
    "Every small step, every saved coin, and every hard-earned profit brings you closer to the thriving empire you are building. Keep shining, you've got this! ✨💖👑"
    </div>
    """,
    unsafe_allow_html=True,
)# Direct Link papunta sa iyong Google Sheet
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <a href="https://docs.google.com/spreadsheets/d/1XYqNHTLR6CUeuE-Qjgh1j1XeNzrKJAvxt_Y-hLS5YwY/edit?usp=sharing" target="_blank" style='text-decoration: none; background-color: #f8d7da; color: #721c24; padding: 10px 20px; border-radius: 20px; font-weight: bold; font-family: "Quicksand", sans-serif;'>
            📊 Open Google Sheet Ledger in New Tab
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)