import pandas as pd
import streamlit as st
from twilio.rest import Client
from dotenv import load_dotenv
import os

# === Load environment variables ===
load_dotenv()

# === Load property data ===
def load_properties(file_path='properties.csv'):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f'Error reading CSV: {e}')
        return None

# === Search property ===
def search_property(df, location, bhk):
    results = df[
        (df['location'].str.lower() == location.lower()) &
        (df['bhk'].str.lower() == bhk.lower())
    ]
    if results.empty:
        return None, 'No matching properties available'
    return results.iloc[0], None

# === Format message ===
def format_property_message(property):
    return f"""🏠 *{property['bhk']} Available in {property['location']}*
- Type: {property['type']}
- Rent: ₹{property['rent']}/month
- Furnishing: {property['furnishing']}
- Parking: {property['parking']}
- Contact: {property['contact']}
📸 Photos: {property['photos_link']}"""

# === Send WhatsApp message ===
def send_whatsapp_message(body_text, to_number):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=body_text,
        to=f'whatsapp:{to_number}'
    )
    return message.sid

# === Streamlit UI ===
st.set_page_config(page_title="Real Estate WhatsApp Bot")
st.title("🏠 Real Estate Assistant")

# Load data
df = load_properties()
if df is not None:
    locations = df['location'].dropna().unique().tolist()
    bhks = df['bhk'].dropna().unique().tolist()

    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("Select Location", sorted(locations))
    with col2:
        selected_bhk = st.selectbox("Select BHK", sorted(bhks))

    phone = st.text_input("Enter WhatsApp number (with +91)", max_chars=13)

    if st.button("Send Property via WhatsApp"):
        if phone.strip() == "":
            st.warning("Please enter a WhatsApp number.")
        else:
            property, error = search_property(df, selected_location, selected_bhk)
            if error:
                st.error(error)
            else:
                message = format_property_message(property)
                sid = send_whatsapp_message(message, phone)
                st.success(f"✅ Sent! Message SID: {sid}")
