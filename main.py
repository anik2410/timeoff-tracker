import streamlit as st
from datetime import datetime

from vacation_manager import VacationManager
from personal_manager import PersonalManager

vac = VacationManager()
per = PersonalManager()

st.set_page_config(page_title="Time Off Tracker", layout="centered")

st.title("⏰ Time Off Tracker")

tabs = st.tabs(["🌴 Vacation Days", "🧍 Personal Days"])

# =====================================================================
# TAB: VACATION
# =====================================================================
with tabs[0]:
    st.header("🌴 Vacation Days")

    # Allowance
    vac_total = vac.get_allowance()

    if vac_total is None:
        vac_total = st.number_input("Enter your total vacation days", min_value=1.0)
        if st.button("Save Vacation Allowance"):
            vac.set_allowance(vac_total)
            st.success("Vacation allowance saved.")
            st.rerun()

    else:
        st.write(f"Total Vacation Days: **{vac_total}**")

        # Step 1 — when button clicked, enable edit mode
        if st.button("Update Vacay Allowance"):
            st.session_state.vac_allowance_edit = True
        # Step 2 — show edit field if edit mode enabled
        if st.session_state.get("vac_allowance_edit"):
            new_value = st.number_input(
                "New Vacation Allowance",
                min_value=1.0,
                value=vac_total,
                key="vac_allowance_input"
            )

            if st.button("Save New Vacation Allowance"):
                vac.set_allowance(new_value)
                st.success("Allowance updated.")
                st.session_state.vac_allowance_edit = False
                st.rerun()


    # Remaining
    remaining = vac.remaining_days()
    if remaining is not None:
        st.success(f"Remaining: **{remaining:.1f} days**")

    st.divider()

    # Add Record
    st.subheader("Add Vacation Record")

    vac_start = st.date_input("Start Date", key="vac_start")
    vac_end   = st.date_input("End Date", value=vac_start, key="vac_end")
    full  = st.radio("Full Day?", ["Yes", "No"], key="vac_full") == "Yes"
    purpose = st.text_input("Purpose", key="vac_purpose")

    if st.button("Save Vacation"):
        vac.add_record(vac_start, vac_end, full, purpose)
        st.success("Vacation saved!")
        st.rerun()

    st.divider()

    # View/Edit/Delete
    st.subheader("All Vacation Records")

    for rec in vac.get_records():
        rec_id, s, e, full_day, hours, purp = rec

        with st.expander(f"Vacation ID {rec_id}"):
            st.write(f"📅 {s} → {e}")
            st.write(f"🔘 Full Day: {full_day}")
            st.write(f"⏱ Hours: {hours}")
            st.write(f"📝 {purp}")

            col1, col2 = st.columns(2)

            # Delete
            if col1.button(f"Delete {rec_id}", key=f"vac_del_{rec_id}"):
                vac.delete_record(rec_id)
                st.warning("Record deleted.")
                st.rerun()

            # Edit
            if col2.button(f"Edit {rec_id}", key=f"vac_edit_{rec_id}"):
                st.session_state.vac_edit = rec_id

            # Edit form
            if st.session_state.get("vac_edit") == rec_id:
                new_start = st.date_input("Start", datetime.strptime(s, "%Y-%m-%d"), key=f"vac_edit_s_{rec_id}")
                new_end   = st.date_input("End", datetime.strptime(e, "%Y-%m-%d"), key=f"vac_edit_e_{rec_id}")
                new_full  = st.radio("Full Day?", ["Yes", "No"], index=0 if full_day else 1, key=f"vac_edit_full_{rec_id}") == "Yes"
                new_purp  = st.text_input("Purpose", purp, key=f"vac_edit_p_{rec_id}")

                if st.button("Save Changes", key=f"vac_saveedit_{rec_id}"):
                    vac.update_record(rec_id, new_start, new_end, new_full, new_purp)
                    st.success("Updated!")
                    st.session_state.vac_edit = None
                    st.rerun()


# =====================================================================
# TAB: PERSONAL
# =====================================================================
with tabs[1]:
    st.header("🧍 Personal Days")

    # Allowance
    per_total = per.get_allowance()

    if per_total is None:
        per_total = st.number_input("Enter total personal days", min_value=1.0)
        if st.button("Save Personal Allowance"):
            per.set_allowance(per_total)
            st.success("Personal allowance saved.")
            st.rerun()
    else:
        st.write(f"Total Personal Days: **{per_total}**")

        # Step 1 — when button clicked, enable edit mode
        if st.button("Update Personal Allowance"):
            st.session_state.per_allowance_edit = True
        # Step 2 — show edit field if edit mode enabled
        if st.session_state.get("per_allowance_edit"):
            new_value = st.number_input(
                "New Personal Allowance",
                min_value=1.0,
                value=per_total,
                key="per_allowance_input"
            )

            if st.button("Save New Personal Allowance"):
                per.set_allowance(new_value)
                st.success("Allowance updated.")
                st.session_state.per_allowance_edit = False
                st.rerun()

    # Remaining
    remaining = per.remaining_days()
    if remaining is not None:
        st.success(f"Remaining: **{remaining:.1f} days**")

    st.divider()

    # Add
    st.subheader("Add Personal Day")

    per_start = st.date_input("Start Date", key="per_start")
    per_end   = st.date_input("End Date", value=per_start, key="per_end")
    full  = st.radio("Full Day?", ["Yes", "No"], key="per_full") == "Yes"
    purpose = st.text_input("Purpose", key="per_purpose")

    if st.button("Save Personal Day"):
        per.add_record(per_start, per_end, full, purpose)
        st.success("Personal day saved!")
        st.rerun()

    st.divider()

    # View/Edit/Delete
    st.subheader("All Personal Records")

    for rec in per.get_records():
        rec_id, s, e, full_day, hours, purp = rec

        with st.expander(f"Personal ID {rec_id}"):
            st.write(f"📅 {s} → {e}")
            st.write(f"🔘 Full Day: {full_day}")
            st.write(f"⏱ Hours: {hours}")
            st.write(f"📝 {purp}")

            col1, col2 = st.columns(2)

            # Delete
            if col1.button(f"Delete {rec_id}", key=f"per_del_{rec_id}"):
                per.delete_record(rec_id)
                st.warning("Deleted.")
                st.rerun()

            # Edit
            if col2.button(f"Edit {rec_id}", key=f"per_edit_{rec_id}"):
                st.session_state.per_edit = rec_id

            # Edit form
            if st.session_state.get("per_edit") == rec_id:
                new_start = st.date_input("Start", datetime.strptime(s, "%Y-%m-%d"), key=f"per_edit_s_{rec_id}")
                new_end   = st.date_input("End", datetime.strptime(e, "%Y-%m-%d"), key=f"per_edit_e_{rec_id}")
                new_full  = st.radio("Full Day?", ["Yes", "No"], index=0 if full_day else 1, key=f"per_edit_full_{rec_id}") == "Yes"
                new_purp  = st.text_input("Purpose", purp, key=f"per_edit_p_{rec_id}")

                if st.button("Save Changes", key=f"per_saveedit_{rec_id}"):
                    per.update_record(rec_id, new_start, new_end, new_full, new_purp)
                    st.success("Updated!")
                    st.session_state.per_edit = None
                    st.rerun()

# =====================================================================
# Global Reset Section
# =====================================================================
st.divider()
st.header("🔄 Reset Options")

choice = st.selectbox("Reset What?", ["Nothing", "Vacation", "Personal", "Both"])
confirm = st.text_input("Type RESET to confirm")

if st.button("Reset"):
    if confirm.strip().upper() != "RESET":
        st.error("Reset failed — type RESET.")
    else:
        if choice in ["Vacation", "Both"]:
            vac.reset_all()

        if choice in ["Personal", "Both"]:
            per.reset_all()

        st.success("Reset complete.")
        st.rerun()
