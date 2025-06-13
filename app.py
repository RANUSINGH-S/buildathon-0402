# SmartCare Streamlit App with Enhanced Features
import streamlit as st
import pandas as pd
from gtts import gTTS
import os
import smtplib
from email.message import EmailMessage
from fpdf import FPDF
import qrcode
from datetime import date

# Set page config
st.set_page_config(page_title="SmartCare", layout="centered")

# Custom CSS Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8fbff;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #004080;
    }
    .stButton button {
        background-color: #0077cc;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        border: 1px solid #ccc;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] {
        background-color: #e7f1ff;
    }
    </style>
""", unsafe_allow_html=True)

# Email sending function
def send_email(to, subject, body):
    email = EmailMessage()
    email['From'] = "your_email@gmail.com"  # Replace
    email['To'] = to
    email['Subject'] = subject
    email.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("your_email@gmail.com", "your_app_password")  # Replace
        smtp.send_message(email)

# PDF and QR code receipt
def generate_receipt(name, doctor, date, time):
    receipt = FPDF()
    receipt.add_page()
    receipt.set_font("Arial", size=12)
    receipt.cell(200, 10, txt="SmartCare Appointment Receipt", ln=True, align="C")
    receipt.ln(10)
    receipt.cell(200, 10, txt=f"Name: {name}", ln=True)
    receipt.cell(200, 10, txt=f"Doctor: {doctor}", ln=True)
    receipt.cell(200, 10, txt=f"Date & Time: {date} at {time}", ln=True)
    receipt.output("receipt.pdf")
    qr = qrcode.make(f"{name}-{doctor}-{date}-{time}")
    qr.save("qr.png")

# Sidebar Navigation
st.sidebar.title("SmartCare Navigation")
menu = st.sidebar.radio("Go to", ["🏠 Home", "📅 Book Appointment", "🧾 View Appointments", "📞 Contact Us"])

# Doctor availability
doctor_availability = {
    "Dr. Sharma": ["10:00 AM", "11:00 AM"],
    "Dr. Verma": ["12:00 PM", "3:00 PM"],
    "Dr. Aisha": ["10:00 AM", "3:00 PM"]
}

# Home Page
if menu == "🏠 Home":
    st.title("🏥 Welcome to SmartCare")
    st.image("images.hc.png", use_container_width=True)
    st.markdown("""
        ## Your Digital Health Assistant
        **SmartCare** helps hospitals reduce wait times by allowing patients to book appointments online.

        🔹 Book appointments in seconds  
        🔹 Instant voice and email confirmation  
        🔹 Admin dashboard with analytics  

        ---
        👇 Use the sidebar to navigate
    """)

# Book Appointment Page
elif menu == "📅 Book Appointment":
    st.title("📅 Book Your Appointment")
    name = st.text_input("Patient Name")
    email = st.text_input("Email")
    doctor = st.selectbox("Select Doctor", list(doctor_availability.keys()))
    date = st.date_input("Appointment Date")
    time = st.selectbox("Time Slot", doctor_availability[doctor])

    if st.button("Book Appointment"):
        with st.spinner("Booking your appointment..."):
            new_data = pd.DataFrame([[name, email, doctor, date, time]],
                                    columns=["name", "email", "doctor", "date", "time"])
            if os.path.exists("appointments.csv"):
                df = pd.read_csv("appointments.csv")
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                df = new_data
            df.to_csv("appointments.csv", index=False)

            tts = gTTS(f"Appointment booked with {doctor} at {time} on {date}")
            tts.save("confirm.mp3")
            st.audio("confirm.mp3", format="audio/mp3")

            try:
                send_email(email, "Appointment Confirmation",
                           f"Hi {name},\nYour appointment with {doctor} is confirmed for {date} at {time}.")
            except:
                st.warning("Could not send email. Check credentials.")

            generate_receipt(name, doctor, date, time)
            st.image("qr.png", caption="Scan to verify")
            with open("receipt.pdf", "rb") as f:
                st.download_button("📄 Download Receipt", f, file_name="appointment_receipt.pdf")

            # Queue Info
            waiting_df = df[(df["doctor"] == doctor) & (df["date"] == str(date))]
            st.info(f"🕒 You are number {len(waiting_df)} in the queue for {doctor}.")

            st.success(f"✅ Appointment booked with {doctor} at {time} on {date}")

# View Appointments (Admin)
elif menu == "🧾 View Appointments":
    st.title("🔐 Admin Login")
    pwd = st.text_input("Enter admin password", type="password")
    if pwd == "smartcare123":
        st.success("Access granted ✅")
        if os.path.exists("appointments.csv"):
            df = pd.read_csv("appointments.csv")
            df["date"] = pd.to_datetime(df["date"])
            selected_date = st.date_input("📅 Filter by date")
            filtered_df = df[df["date"].dt.date == selected_date]

            st.subheader("📋 Appointments")
            for i, row in filtered_df.iterrows():
                st.write(f"👤 {row['name']} - {row['doctor']} - {row['date'].strftime('%Y-%m-%d')} at {row['time']}")
                if st.button(f"Cancel #{i}", key=f"cancel_{i}"):
                    df.drop(i, inplace=True)
                    df.to_csv("appointments.csv", index=False)
                    st.success("❌ Appointment cancelled.")
                    st.experimental_rerun()

            # Analytics
            st.subheader("📊 Analytics")
            chart_df = df.groupby("doctor").size().reset_index(name="Appointments")
            st.bar_chart(chart_df.set_index("doctor"))

            ts_df = df.groupby("date").size().reset_index(name="Total")
            st.line_chart(ts_df.set_index("date"))
        else:
            st.info("No appointments found.")
    else:
        st.warning("Access denied ❌")

# Contact Us Page
elif menu == "📞 Contact Us":
    st.title("📞 Contact Us")
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")
    if st.button("Send Message"):
        contact = pd.DataFrame([[name, email, message]], columns=["name", "email", "message"])
        if os.path.exists("contact_messages.csv"):
            df = pd.read_csv("contact_messages.csv")
            df = pd.concat([df, contact], ignore_index=True)
        else:
            df = contact
        df.to_csv("contact_messages.csv", index=False)
        st.success("✅ Thank you! Your message has been received.")



