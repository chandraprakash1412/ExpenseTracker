import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(layout="wide")
st.title("💰 Expense Tracker Dashboard")

DATA_FOLDER = "data"
OUTPUT_FILE = "output/expense_data.xlsx"
SCRIPT_PATH = "scripts/expense_tracker.py"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs("output", exist_ok=True)

# Upload PDF
uploaded_file = st.file_uploader("Upload Bank Statement PDF", type=["pdf"])

if uploaded_file:
    file_path = os.path.join(DATA_FOLDER, uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ File uploaded successfully")

    if st.button("Run Analysis"):

        # Run script
        result = subprocess.run(
            ["python", SCRIPT_PATH],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            st.error("❌ Error while processing")
            st.text(result.stderr)
        else:
            st.success("✅ Analysis Completed")

            if os.path.exists(OUTPUT_FILE):
                df = pd.read_excel(OUTPUT_FILE)

                st.subheader("📊 Expense Data")
                st.dataframe(df, width="stretch")

                st.download_button(
                    "⬇ Download Excel",
                    data=open(OUTPUT_FILE, "rb"),
                    file_name="expense_data.xlsx"
                )
            else:
                st.warning("⚠️ Output file not found")
