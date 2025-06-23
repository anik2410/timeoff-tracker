import streamlit as st
import sqlite3
from datetime import datetime


st.title("Vacation Tracker")

# === CONFIG ===
DB_FILE = "vacation_tracker.db"
VACATION_RECORDS = "vacation"
VACATION_ALLOWANCE_TABLE = "vacation_allowance"
RECREATE_TABLE = False

# === DB SETUP ===
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# === RECREATE TABLE ===
if RECREATE_TABLE:
    cursor.execute(f"DROP TABLE IF EXISTS {VACATION_RECORDS}")
    cursor.execute(f"DROP TABLE IF EXISTS {VACATION_ALLOWANCE_TABLE}")
cursor.execute(f"CREATE TABLE IF NOT EXISTS {VACATION_ALLOWANCE_TABLE} (key TEXT PRIMARY KEY, value FLOAT)")
cursor.execute(f"CREATE TABLE IF NOT EXISTS {VACATION_RECORDS} (id INTEGER PRIMARY KEY, start_date TEXT, end_date TEXT, is_full_day BOOLEAN, hours FLOAT,  purpose TEXT)")

# === FETCH RECORD ===
cursor.execute(f"SELECT * FROM {VACATION_RECORDS}")
records = cursor.fetchall()

# === INIT OR FETCH VACATION ALLOWANCE ===
cursor.execute(f"SELECT value FROM {VACATION_ALLOWANCE_TABLE} WHERE key = 'total_days'")
existing_total = cursor.fetchone()

total_vacation_days_reset_flag = False

if existing_total is None:
    total_vacation_days_reset_flag = True
else:
    total_vacation_days = existing_total[0]

if total_vacation_days_reset_flag:
    with st.form("vacation_allowance_form"):
        st.subheader("🔧 Set Your Total Vacation Days Allowance")
        total_vacation_days = st.number_input("Enter Your Total Vacation Days Allowance", min_value=1.0)
        submit_button = st.form_submit_button("Submit")
        cancel_button = st.form_submit_button("Cancel")
        if submit_button:
            cursor.execute(f"INSERT INTO {VACATION_ALLOWANCE_TABLE} (key, value) VALUES('total_days', ?)", (total_vacation_days,))
            conn.commit()
            print("Total vacation days set to:", total_vacation_days)
        elif cancel_button:
            print("Vacation allowance input canceled.")
    st.rerun()

# === CALCULATE REMAINING DAYS ===
def calculate_remaining_days(total_vacation_days, records):
    used_days = 0
    for r in records:
        start = datetime.strptime(r[1], "%Y-%m-%d").date()
        end = datetime.strptime(r[2], "%Y-%m-%d").date()
        full_day = r[3]
        days = (end - start).days + 1
        used_days += days if full_day else 0.5
    return total_vacation_days - used_days


remaining_days = calculate_remaining_days(total_vacation_days, records)

st.subheader(f"🌴 Remaining Vacation Days: {remaining_days:.1f}")

# === SETUP SESSION STATE FOR FORM ===
if "start_date" not in st.session_state:
    st.session_state.start_date = datetime.today()

if "purpose" not in st.session_state:
    st.session_state.purpose = ""

if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

if st.session_state.reset_form:
    st.session_state.start_date = datetime.today().date()
    st.session_state.purpose = ""
    st.session_state.reset_input = ""
    total_vacation_days_reset_flag = True
    st.session_state.reset_form = False

#  === WIDGETS ===
st.subheader("Add New Vacation Record")

def hours_calc(days_requested, is_full_day):
    if not is_full_day:
        days_taken = 0.5
    else:
        days_taken = float(days_requested)
    hours = days_taken * 8
    return hours

start_date_input = st.date_input("Start Date", key="start_date")
existing_start_dates = [datetime.strptime(r[0], '%Y-%m-%d').date() for r in cursor.execute(f"SELECT start_date FROM vacation").fetchall()]
if start_date_input in existing_start_dates:
    st.warning("Start date cannot be the same as the existing record.")
end_date_input = st.date_input("End Date", value=start_date_input)
full_day = st.radio("Full Day?", ["Yes", "No"], index=0)
purpose = st.text_input("Purpose", key="purpose")

with st.form("vacation_form"):
    submit_button = st.form_submit_button("Submit")

if submit_button:
    if start_date_input in existing_start_dates:
        st.error("Submission failed: Start date already exists in a record. Please choose a different start date.")
    else:
        days_requested = (end_date_input - start_date_input).days + 1
        is_full_day = True if full_day == "Yes" else False
        hours = hours_calc(days_requested, is_full_day)
        st.write("Vacation Request Submitted:")
        st.write(f"Start Date: {start_date_input}")
        st.write(f"End Date: {end_date_input}")

        cursor.execute("INSERT INTO vacation (start_date, end_date, is_full_day, hours, purpose) VALUES (?, ?, ?, ?, ?)",
                    (start_date_input.isoformat(), end_date_input.isoformat(), is_full_day, hours, purpose))
        conn.commit()

        st.success("Vacation Request Recorded Successfully!")
        st.session_state.reset_form = True
        st.rerun()

# === RESET TABLE BY USER ===
st.markdown("### Reset Vacation Records")
reset_input = st.text_input("Type 'RESET' to confirm", key="reset_input")
if st.button("Reset Vacation Record"):
    if reset_input.strip().upper() == "RESET":
        cursor.execute(f"DROP TABLE IF EXISTS {VACATION_RECORDS}")
        cursor.execute(f"DROP TABLE IF EXISTS {VACATION_ALLOWANCE_TABLE}")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {VACATION_RECORDS} (id INTEGER PRIMARY KEY, start_date TEXT, end_date TEXT, is_full_day BOOLEAN, hours FLOAT, purpose TEXT)")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {VACATION_ALLOWANCE_TABLE} (key TEXT PRIMARY KEY, value FLOAT)")
        conn.commit()
        st.success("Vacation Record Reset Successfully!")
        st.rerun()
    else:
        st.error("Reset confirmation failed.")

# === VIEW AND EDIT VACATION RECORDS ===
st.subheader("Current Vacation Records")

cursor.execute("SELECT * FROM vacation")
records = cursor.fetchall()
if records:
    for record in records:
        record_id, start_date, end_date, is_full_day, hours, purpose = record

        with st.expander(f"Vacation ID {record_id}"):
            st.write(f"📅 Start Date: {start_date}")
            st.write(f"📅 End Date: {end_date}")
            st.write(f"🕒 Hours: {hours}")
            st.write(f"Purpose: {purpose}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Edit {record_id}"):
                    st.session_state.edit_id = record_id
            with col2:
                if st.button(f"🗑️ Delete {record_id}"):
                    cursor.execute(f"DELETE FROM vacation WHERE id={record_id}")
                    conn.commit()
                    st.warning(f"Vacation ID {record_id} deleted. Please Refresh the Page.")
                    st.rerun()

            if st.session_state.edit_id == record_id:
                st.markdown("### Edit Vacation Record")
                with st.form(f"edit_form_{record_id}"):
                    new_start = st.date_input("Start Date", value=datetime.strptime(start_date, '%Y-%m-%d').date())
                    new_end = st.date_input("End Date", value=datetime.strptime(end_date, '%Y-%m-%d').date())
                    new_full_day = st.radio("Full Day?", ["Yes", "No"], index=0 if is_full_day else 1)
                    new_purpose = st.text_input("Purpose", value=purpose)

                    days_requested = (new_end - new_start).days + 1
                    is_full_day = True if new_full_day == "Yes" else False
                    hours = hours_calc(days_requested, is_full_day)

                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submit_edit = st.form_submit_button("Update")
                    with col_cancel:
                        submit_cancel = st.form_submit_button("Cancel")
                    if submit_edit:
                        cursor.execute("""
                            UPDATE vacation
                            SET start_date = ?, end_date = ?, is_full_day = ?, hours = ?, purpose = ?
                            WHERE id = ?
                        """, (new_start, new_end, new_full_day, hours, new_purpose, record_id))
                        conn.commit()
                        st.success("Vacation Record Updated Successfully!")
                        st.session_state.edit_id = None
                        st.rerun()
                    elif submit_cancel:
                        st.session_state.edit_id = None
                        st.rerun()
else:
    st.info("No vacation records found.")
