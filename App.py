import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

st.title("📅 Staff Reservation Sheet")

# --- CONFIGURATION ---
START_TIME = datetime.strptime("08:00", "%H:%M").time()
END_TIME = datetime.strptime("12:30", "%H:%M").time()
SLOT_MINUTES = 15
CSV_FILE = "reservations.csv"
# --- Generate time slots ---
def generate_time_slots():
    slots = []
    current = datetime.combine(date.today(), START_TIME)
    while current.time() < datetime.strptime("17:00", "%H:%M").time():
        end = current + timedelta(minutes=SLOT_MINUTES)
        # Convert both start and end times to 12-hour format with AM/PM:
        start_12h = current.strftime("%I:%M %p").lstrip('0')
        end_12h = end.strftime("%I:%M %p").lstrip('0')
        slots.append(f"{start_12h} - {end_12h}")
        current = end
    return slots

# --- Load existing reservations ---
try:
    reservations = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    reservations = pd.DataFrame(columns=["Name", "Email", "Date", "Slot", "Description"])

# --- User Input ---
st.subheader("🔒 Book a Time Slot")
name = st.text_input("Your Name")
email = st.text_input("Your Email")
selected_date = st.date_input("Select a Date", min_value=date.today())
all_slots = generate_time_slots()

# Filter out already reserved slots for selected date
booked_slots_today = reservations[reservations["Date"] == str(selected_date)]["Slot"].tolist()
available_slots = [slot for slot in all_slots if slot not in booked_slots_today]

# Show only valid slots
valid_slots = []
today = date.today()
start_limit = datetime.strptime("08:00 AM", "%I:%M %p").time()
end_limit_today = datetime.strptime("12:30 PM", "%I:%M %p").time()
end_limit_other = datetime.strptime("05:00 PM", "%I:%M %p").time()

for slot in available_slots:
    slot_start = datetime.strptime(slot.split(" - ")[0], "%I:%M %p").time()
    
    if selected_date == today:
        if start_limit <= slot_start <= end_limit_today:
            valid_slots.append(slot)
    else:
        if start_limit <= slot_start <= end_limit_other:
            valid_slots.append(slot)

slot = st.selectbox("Select a 15-minute slot", valid_slots)
description = st.text_area("Brief Description (Optional)")

# --- Reserve Slot ---
if st.button("Reserve Slot"):
    if not name or not email or not slot:
        st.error("Name, Email, and Slot are required.")
    else:
        new_entry = {
            "Name": name,
            "Email": email,
            "Date": str(selected_date),
            "Slot": slot,
            "Description": description
        }
        reservations = pd.concat([reservations, pd.DataFrame([new_entry])], ignore_index=True)
        reservations.to_csv(CSV_FILE, index=False)
        st.success(f"Reservation confirmed for {slot} on {selected_date}")
        try:
            st.experimental_rerun()
        except AttributeError:
            pass  # ignore if function does not exist

# --- Show reservations ---
st.subheader("📋 Current Reservations")
st.dataframe(reservations.sort_values(by=["Date", "Slot"]))
