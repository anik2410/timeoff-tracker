import streamlit as st
import sqlite3
from datetime import datetime


st.title("Vacation Tracker")

# === CONFIG ===
DB_FILE = "vacation_tracker.db"
TABLE_NAME = "vacation"
RECREATE_TABLE = False

# === DB SETUP ===
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# === RECREATE TABLE ===
if RECREATE_TABLE:
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
cursor.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (id INTEGER PRIMARY KEY, start_date TEXT, end_date TEXT, is_full_day BOOLEAN, hours FLOAT, remaining_days FLOAT, purpose TEXT)")

# === VIEW AND EDIT VACATION RECORDS ===
st.subheader("Current Vacation Records")

cursor.execute("SELECT * FROM vacation")
records = cursor.fetchall()
if records:
    for record in records:
        record_id, start_date, end_date, is_full_day, hours, remaining_days, purpose = record

        with st.expander(f"Vacation ID {record_id}"):
            st.write(f"📅 Start Date: {start_date}")
            st.write(f"📅 End Date: {end_date}")
            st.write(f"🕒 Hours: {hours}")
            st.write(f"Full Day: {is_full_day}")
            st.write(f"Purpose: {purpose}")
            st.write(f"Remaining Days: {remaining_days}")

            if st.button(f"🗑️ Delete {record_id}"):
                cursor.execute(f"DELETE FROM vacation WHERE id={record_id}")
                conn.commit()
                st.warning(f"Vacation ID {record_id} deleted. Please Refresh the Page.")
                st.rerun()
        # col1, col2 = st.columns([4, 1])
        # with col1:
        #     st.markdown(f"""
        #                 **Vacation ID:** {record_id}
        #                 **Start Date:** {start_date}
        #                 **End Date:** {end_date}
        #                 **Full Day:** {full_day}
        #                 **Hours:** {hours}
        #                 **Remaining Days:** {remaining_days}
        #                 **Purpose:** {purpose}
        #                 """)

        # with col2:
        #     if st.button("🗑️ Delete", key=f"delete_{record_id}"):
        #         cursor.execute(f"DELETE FROM vacation WHERE id={record_id}")
        #         conn.commit()
        #         st.warning(f"Vacation ID {record_id} deleted. Please Refresh the Page.")
else:
    st.info("No vacation records found.")

# Check session_state
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False

st.subheader("Add New Vacation Record")

total_days = st.number_input("Your Total Vacation Days Allowance", min_value=1, value=1)
start_date_input = st.date_input("Start Date")
existing_start_dates = [datetime.strptime(r[0], '%Y-%m-%d').date() for r in cursor.execute(f"SELECT start_date FROM vacation").fetchall()]
if start_date_input in existing_start_dates:
    st.warning("Start date cannot be the same as the existing record.")
end_date_input = st.date_input("End Date", value=start_date_input)
full_day = st.radio("Full Day?", ["Yes", "No"], index=0)
purpose = st.text_input("Purpose")

with st.form("vacation_form"):
    submit_button = st.form_submit_button("Submit")

if submit_button:
    if start_date_input in existing_start_dates:
        st.error("Submission failed: Start date already exists in a record. Please choose a different start date.")
    else:
        days_requested = (end_date_input - start_date_input).days + 1
        is_full_day = True if full_day == "Yes" else False
        if not is_full_day:
            days_taken = 0.5
        else:
            days_taken = float(days_requested)
        hours = days_taken * 8
        remaining_days = total_days - days_taken
        st.write("Vacation Request Submitted:")
        st.write(f"Start Date: {start_date_input}")
        st.write(f"End Date: {end_date_input}")
        st.write(f"Remaining Days: {remaining_days}")

        cursor.execute("INSERT INTO vacation (start_date, end_date, is_full_day, hours, remaining_days, purpose) VALUES (?, ?, ?, ?, ?, ?)",
                    (start_date_input.isoformat(), end_date_input.isoformat(), is_full_day, hours, remaining_days, purpose))
        conn.commit()

        st.success("Vacation Request Recorded Successfully!")
        st.rerun()