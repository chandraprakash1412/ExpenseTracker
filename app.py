import streamlit as st
import pandas as pd
import os

# Backend
from scripts.expense_tracker import main

# -----------------------------
# Config
# -----------------------------
st.set_page_config(layout="wide")
st.title("💰 Expense Tracker Dashboard")

DATA_FOLDER = "data"
OUTPUT_FILE = "output/expense_data.xlsx"

os.makedirs(DATA_FOLDER, exist_ok=True)

# -----------------------------
# Upload Section
# -----------------------------
st.subheader("📂 Upload Bank Statement (PDF)")

uploaded_file = st.file_uploader("Upload PDF File", type=["pdf"])

file_path = None

if uploaded_file is not None:
    file_path = os.path.join(DATA_FOLDER, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("File uploaded successfully ✅")

# -----------------------------
# Run Analysis
# -----------------------------
if st.button("🚀 Run Analysis"):

    if file_path is None:
        files = os.listdir(DATA_FOLDER)

        if len(files) > 0:
            files.sort(key=lambda x: os.path.getmtime(os.path.join(DATA_FOLDER, x)))
            file_path = os.path.join(DATA_FOLDER, files[-1])
        else:
            st.error("No file available ❌")
            st.stop()

    try:
        main(file_path)
    except TypeError:
        main()

    st.success("Analysis completed ✅")

# -----------------------------
# Dashboard
# -----------------------------
if os.path.exists(OUTPUT_FILE):

    df = pd.read_excel(OUTPUT_FILE)

    # -----------------------------
    # Preprocessing
    # -----------------------------
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Month"] = df["Date"].dt.month_name()
    df["Year"] = df["Date"].dt.year

    # -----------------------------
    # Sidebar Filters (SLICER)
    # -----------------------------
    st.sidebar.header("🔍 Filters")

    selected_years = st.sidebar.multiselect(
        "Select Year",
        options=sorted(df["Year"].dropna().unique()),
        default=sorted(df["Year"].dropna().unique())
    )

    selected_months = st.sidebar.multiselect(
        "Select Month",
        options=df["Month"].dropna().unique(),
        default=df["Month"].dropna().unique()
    )

    # Apply filter
    filtered_df = df[
        (df["Year"].isin(selected_years)) &
        (df["Month"].isin(selected_months))
    ]

    # -----------------------------
    # Charts (Side by Side)
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Monthly Expense")

        monthly = (
            filtered_df.groupby("Month")["Amount"]
            .sum()
            .reindex(df["Month"].unique())
        )

        st.bar_chart(monthly)

    with col2:
        st.subheader("📆 Yearly Expense")

        yearly = filtered_df.groupby("Year")["Amount"].sum()

        st.bar_chart(yearly)

    # -----------------------------
    # Transactions Table
    # -----------------------------
    st.subheader("📋 Transactions")

    st.dataframe(filtered_df, use_container_width=True)

    # -----------------------------
    # Mobile Recharge Monthly
    # -----------------------------
    st.subheader("📱 Mobile Recharge (Monthly)")

    recharge_df = filtered_df[
        filtered_df["Category"].str.contains("mobile|recharge", case=False, na=False)
    ]

    recharge_monthly = recharge_df.groupby("Month")["Amount"].sum()

    st.bar_chart(recharge_monthly)

else:
    st.warning("⚠️ Run analysis to see dashboard")
