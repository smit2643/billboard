import streamlit as st
import requests
import pandas as pd
import io
import time

# API Base URL
API_BASE_URL = "http://127.0.0.1:8002/api"

# Helper function to fetch data with loading spinner
def fetch_data(endpoint):
    with st.spinner("Fetching data..."):
        try:
            response = requests.get(f"{API_BASE_URL}/{endpoint}/")
            if response.status_code == 200:
                data = response.json()
                return data.get("data", data)
            else:
                st.error(f"Error: {response.status_code}, {response.text}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
    return []

# Function to send data with success/error feedback
def send_data(endpoint, data):
    try:
        response = requests.post(f"{API_BASE_URL}/{endpoint}/", json=data)
        if response.status_code == 201:
            st.success("Created successfully!")
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
    return None

# Function to update data dynamically
def update_data(endpoint, data):
    try:
        response = requests.put(f"{API_BASE_URL}/{endpoint}/", json=data)
        if response.status_code in [200, 204]:
            st.success("Updated successfully!")
            return True
        else:
            st.error(f"Error: {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
    return False

# Function to delete data
def delete_data(endpoint):
    try:
        response = requests.delete(f"{API_BASE_URL}/{endpoint}/")
        if response.status_code in [200, 204]:
            st.success("Deleted successfully!")
            return True
        else:
            st.error(f"Error: {response.status_code} - {response.json()}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {str(e)}")
    return False

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Landlords", "Billboards", "Rent Agreements", "Installments"])

if page == "Landlords":
    st.title("🏡 Manage Landlords")


    if st.button("🔄 Refresh List"):
        st.session_state.landlords = fetch_data("landlords")


    landlords = fetch_data("landlords")
    
    if landlords:
        df = pd.DataFrame(landlords)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
       

        st.dataframe(df, use_container_width=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Landlords")
        output.seek(0)
        
        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name="landlords.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No landlords found.")

    with st.expander("➕ Add New Landlord"):
        with st.form("landlord_form"):
            name = st.text_input("Name", placeholder="Enter landlord name")
            email = st.text_input("Email", placeholder="Enter email")
            phone = st.text_input("Phone", placeholder="Enter phone number")
            address = st.text_area("Address", placeholder="Enter address")
            remark = st.text_area("Remark", "")
            submit = st.form_submit_button("Create Landlord")
            
            if submit and name and phone:
                send_data("landlords", {"name": name, "email": email, "phone": phone, "address": address , "remark": remark })
            elif submit:
                st.warning("Please fill all required fields!")

    with st.expander("🔄 Update or Delete Landlord"):
        landlord_options = {f"{l['name']} - {l['phone']}": l["id"] for l in landlords} if landlords else {}
        selected_landlord = st.selectbox("Select a Landlord", options=list(landlord_options.keys()), index=None, help="Search by name/phone")
        
        if selected_landlord:
            landlord_id = landlord_options[selected_landlord]
            landlord_data = next((l for l in landlords if l["id"] == landlord_id), {})
            
            update_name = st.text_input("Update Name", landlord_data.get("name", ""))
            update_email = st.text_input("Update Email", landlord_data.get("email", ""))
            update_phone = st.text_input("Update Phone", landlord_data.get("phone", ""))
            update_address = st.text_area("Update Address", landlord_data.get("address", ""))
            update_remark = st.text_area("Update Remark", landlord_data.get("remark", ""))
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Update Landlord"):
                    update_data(f"landlords/{landlord_id}", {
                        "name": update_name,
                        "email": update_email,
                        "phone": update_phone,
                        "address": update_address,
                        "remark": update_remark
                    })
            
            with col2:
                if st.button("🗑️ Delete Landlord", help="This action is irreversible!"):
                    if delete_data(f"landlords/{landlord_id}"):
                        st.warning("Landlord deleted. Refresh to see changes.")




if page == "Billboards":
    st.title("📌 Manage Billboards")
      # Refresh button
    if st.button("🔄 Refresh List"):
            st.session_state.billboards = fetch_data("billboards")

    # Fetch billboard data
    billboards = fetch_data("billboards")
    
    if billboards:
        df = pd.DataFrame(billboards)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
       
        st.dataframe(df, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Billboards")
        output.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name="billboards.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No billboards found.")



    # Add new billboard
    with st.expander("➕ Add New Billboard"):
        landlords = fetch_data("landlords")  # Fetch landlords to assign billboard
        landlord_options = {f"{l['name']} - {l['phone']}": l["id"] for l in landlords} if landlords else {}

        with st.form("billboard_form"):
            landlord = st.selectbox("Landlord", options=list(landlord_options.keys()), index=None)
            hid = st.text_input("HID (Unique Identifier)")
            district = st.text_input("District")
            city = st.text_input("City")
            area = st.text_input("Area")
            location = st.text_area("Location")
            width = st.number_input("Width (meters)", min_value=0.1, step=0.1, format="%.2f")
            height = st.number_input("Height (meters)", min_value=0.1, step=0.1, format="%.2f")

            submit = st.form_submit_button("Create Billboard")

            if submit and landlord and hid:
                send_data("billboards", {
                    "landlord": landlord_options[landlord],
                    "hid": hid,
                    "district": district,
                    "city": city,
                    "area": area,
                    "location": location,
                    "width": width,
                    "height": height
                })
            elif submit:
                st.warning("Please fill all required fields!")

    # Update or Delete Billboard
    with st.expander("🔄 Update or Delete Billboard"):
        billboard_options = {f"{b['hid']} - {b['location']}": b["id"] for b in billboards} if billboards else {}
        selected_billboard = st.selectbox("Select a Billboard", options=list(billboard_options.keys()), index=None)

        if selected_billboard:
            billboard_id = billboard_options[selected_billboard]
            billboard_data = next((b for b in billboards if b["id"] == billboard_id), {})

            update_hid = st.text_input("Update HID", billboard_data.get("hid", ""))
            update_district = st.text_input("Update District", billboard_data.get("district", ""))
            update_city = st.text_input("Update City", billboard_data.get("city", ""))
            update_area = st.text_input("Update Area", billboard_data.get("area", ""))
            update_location = st.text_area("Update Location", billboard_data.get("location", ""))
            update_width = st.number_input("Update Width (meters)", min_value=0.1, step=0.1, format="%.2f", value=float(billboard_data.get("width", 0.1)) if billboard_data.get("width") else 0.1)

            update_height = st.number_input(
    "Update Height (meters)", 
    min_value=0.1, 
    step=0.1, 
    format="%.2f", 
    value=float(billboard_data.get("height", 0.1)) if billboard_data.get("height") else 0.1
)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Update Billboard"):
                    update_data(f"billboards/{billboard_id}", {
                        "hid": update_hid,
                        "district": update_district,
                        "city": update_city,
                        "area": update_area,
                        "location": update_location,
                        "width": update_width,
                        "height": update_height
                    })

            with col2:
                if st.button("🗑️ Delete Billboard", help="This action is irreversible!"):
                    if delete_data(f"billboards/{billboard_id}"):
                        st.warning("Billboard deleted. Refresh to see changes.")
     
if page == "Rent Agreements":
    st.title("📜 Manage Rent Agreements")

    # Refresh button
    if st.button("🔄 Refresh List"):
        st.session_state.rent_agreements = fetch_data("rent-agreements")

    # Fetch rent agreement data
    rent_agreements = fetch_data("rent-agreements")

    if rent_agreements:
        df = pd.DataFrame(rent_agreements)
         # Remove 'id' column if it exists
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        st.dataframe(df, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Rent Agreements")
        output.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name="rent_agreements.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No rent agreements found.")

    # Add new Rent Agreement
    with st.expander("➕ Add New Rent Agreement"):
        landlords = fetch_data("landlords")
        billboards = fetch_data("billboards")

        landlord_options = {f"{l['name']} - {l['phone']}": l["id"] for l in landlords} if landlords else {}
        billboard_options = {f"{b['hid']} - {b['location']}": b["id"] for b in billboards} if billboards else {}

        with st.form("rent_agreement_form"):
            agreement_number = st.text_input("Agreement Number (Unique)")
            # landlord = st.selectbox("Landlord", options=list(landlord_options.keys()), index=None)
            billboard = st.selectbox("Billboard", options=list(billboard_options.keys()), index=None)
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            rent_amount = st.number_input("Yearly Rent Amount (₹)", min_value=0.0, step=1000.0, format="%.2f")
            payment_frequency = st.number_input("Payment Frequency (Months)", min_value=1, max_value=12, step=1)
            advance_amount = st.number_input("Advance Amount (₹)", min_value=0.0, step=1000.0, format="%.2f")

            submit = st.form_submit_button("Create Rent Agreement")

            if submit and landlord and billboard and agreement_number and start_date and end_date:
                payload = {
                    "agreement_number": agreement_number,
                    # "landlord": landlord_options[landlord],
                    "billboard": billboard_options[billboard],
                    "start_date": start_date.strftime("%Y-%m-%d"),  # Ensure correct format
                    "end_date": end_date.strftime("%Y-%m-%d"),  # Ensure correct format
                    "rent_amount_yearly": rent_amount,
                    "payment_frequency_months": payment_frequency,
                    "advance_amount": advance_amount,
                }
                print("paypad    ----- ",payload)
                st.write("Debug Payload:", payload)  # Debugging
                response = send_data("rent-agreements", payload)
                st.success("Rent agreement created successfully!" if response.get("status") else response.get("message"))
            elif submit:
                st.warning("Please fill all required fields!")
    # Update or Delete Rent Agreement
    with st.expander("🔄 Update or Delete Rent Agreement"):
        agreement_options = {f"{a['agreement_number']} - {a['start_date']} to {a['end_date']}": a["id"] for a in rent_agreements} if rent_agreements else {}
        selected_agreement = st.selectbox("Select a Rent Agreement", options=list(agreement_options.keys()), index=None)

        if selected_agreement:
            agreement_id = agreement_options[selected_agreement]
            agreement_data = next((a for a in rent_agreements if a["id"] == agreement_id), {})

            update_agreement_number = st.text_input("Update Agreement Number", agreement_data.get("agreement_number", ""))
            update_start_date = st.date_input("Update Start Date", pd.to_datetime(agreement_data.get("start_date")))
            update_end_date = st.date_input("Update End Date", pd.to_datetime(agreement_data.get("end_date")))
            update_rent_amount = st.number_input("Update Yearly Rent Amount (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(agreement_data.get("rent_amount_yearly", 0.0)))
            update_payment_frequency = st.number_input("Update Payment Frequency (Months)", min_value=1, max_value=12, step=1, value=int(agreement_data.get("payment_frequency_months", 1)))
            update_advance_amount = st.number_input("Update Advance Amount (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(agreement_data.get("advance_amount", 0.0)))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Update Agreement"):
                    update_data(f"rent-agreements/{agreement_id}", {
                        "agreement_number": update_agreement_number,
                        "start_date": str(update_start_date),
                        "end_date": str(update_end_date),
                        "rent_amount_yearly": update_rent_amount,
                        "payment_frequency_months": update_payment_frequency,
                        "advance_amount": update_advance_amount,
                    })

            with col2:
                if st.button("🗑️ Delete Agreement", help="This action is irreversible!"):
                    if delete_data(f"rent-agreements/{agreement_id}"):
                        st.warning("Rent Agreement deleted. Refresh to see changes.")

    # 📄 Expander for downloading Rent Agreement PDF
    with st.expander("📄 Download Rent Agreement PDF"):
        agreement_options = {f"{a['agreement_number']} - {a['start_date']} to {a['end_date']}": a["id"] for a in rent_agreements} if rent_agreements else {}
        selected_agreement = st.selectbox("Select a Rent Agreement", options=list(agreement_options.keys()), index=None, key="pdf_agreement")

        if selected_agreement:
            agreement_id = agreement_options[selected_agreement]
            pdf_url = f"http://127.0.0.1:8002/api/generate-pdf/{agreement_id}/"  # Update with your backend URL

            st.markdown(f"[📥 Download Rent Agreement PDF]( {pdf_url} )", unsafe_allow_html=True)



if page == "Installments":
    st.title("💰 Manage Installments")

    # Refresh button
    if st.button("🔄 Refresh List"):
        st.session_state.installments = fetch_data("installments")

    # Fetch installment data
    installments = fetch_data("installments")

    if installments:
        df = pd.DataFrame(installments)
        if 'id' in df.columns:
            df = df.drop(columns=['id'])
        st.dataframe(df, use_container_width=True)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Installments")
        output.seek(0)

        st.download_button(
            label="📥 Download as Excel",
            data=output,
            file_name="installments.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No installments found.")

    # Add new Installment
    with st.expander("➕ Add New Installment"):
        agreements = fetch_data("rent-agreements")
        agreement_options = {f"{a['agreement_number']} - {a['start_date']} to {a['end_date']}": a["id"] for a in agreements} if agreements else {}

        with st.form("installment_form"):
            agreement = st.selectbox("Rent Agreement", options=list(agreement_options.keys()), index=None)
            month = st.date_input("Installment Month")
            amount = st.number_input("Installment Amount (₹)", min_value=0.0, step=1000.0, format="%.2f")
            status = st.checkbox("Paid?")

            submit = st.form_submit_button("Create Installment")

            if submit and agreement:
                send_data("installments", {
                    "rent_agreement": agreement_options[agreement],
                    "month": str(month),
                    "amount": amount,
                    "status": status,
                })
            elif submit:
                st.warning("Please fill all required fields!")

    # Update or Delete Installment
    with st.expander("🔄 Update or Delete Installment"):
        installment_options = {f"{i['rent_agreement']} -  {i['agreement_number']} - {i['month']} - ₹{i['amount']}": i["id"] for i in installments} if installments else {}
        selected_installment = st.selectbox("Select an Installment", options=list(installment_options.keys()), index=None)

        if selected_installment:
            installment_id = installment_options[selected_installment]
            installment_data = next((i for i in installments if i["id"] == installment_id), {})

            update_month = st.date_input("Update Month", pd.to_datetime(installment_data.get("month")))
            update_amount = st.number_input("Update Installment Amount (₹)", min_value=0.0, step=1000.0, format="%.2f", value=float(installment_data.get("amount", 0.0)))
            update_status = st.checkbox("Paid?", installment_data.get("status", False))

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Update Installment"):
                    update_data(f"installments/{installment_id}", {
                        "month": str(update_month),
                        "amount": update_amount,
                        "status": update_status,
                    })

            with col2:
                if st.button("🗑️ Delete Installment", help="This action is irreversible!"):
                    if delete_data(f"installments/{installment_id}"):
                        st.warning("Installment deleted. Refresh to see changes.")
