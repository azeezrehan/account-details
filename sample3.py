import streamlit as st
from pymongo import MongoClient
from PIL import Image
import base64
import io

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['atm']
users_collection = db['users']
transactions_collection = db['transactions']

# Define minimum balance
MINIMUM_BALANCE = 100.0  # Set your desired minimum balance here

# Function to encode image to base64
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Streamlit app title
st.title("ATM SYSTEM")

# Open Account
def open_account():
    with st.form(key='registration_form'):
        st.subheader("Open Account")
        account_no = st.text_input("Enter Account Number:")
        account_type = st.selectbox("Select Account Type:", ["Savings", "Current", "Fixed Deposit"])
        user_id = st.text_input("Enter User ID:")
        name = st.text_input("Enter Name:")
        email = st.text_input("Enter Email ID:")
        initial_balance = st.number_input("Enter minimum Balance:", min_value=0, max_value=1000)
        image_file = st.file_uploader("Upload Picture", type=["jpg", "jpeg", "png"])
        submit_registration = st.form_submit_button(label='Open Account')

        if submit_registration:
            if image_file is not None:
                image = Image.open(image_file)
                image_base64 = encode_image(image)
                users_collection.insert_one({
                    "account_no": account_no,
                    "account_type": account_type,
                    "user_id": user_id,
                    "name": name,
                    "email": email,
                    "picture": image_base64,
                    "balance": initial_balance
                })
                st.success(f"Account for {name} opened successfully with balance {initial_balance}!")
            else:
                st.error("Please upload a picture.")

# View Account Details
def view_account_details():
    st.subheader("View Account Details")
    user_id = st.text_input("Enter User ID to View Info:")
    if st.button("View Info"):
        user = users_collection.find_one({"user_id": user_id})
        if user:
            st.write(f"Account Number: {user['account_no']}")
            st.write(f"Account Type: {user['account_type']}")
            st.write(f"Name: {user['name']}")
            st.write(f"Email: {user['email']}")
            st.write(f"Balance: {user['balance']}")
            if user.get('picture'):
                image = Image.open(io.BytesIO(base64.b64decode(user['picture'])))
                st.image(image, caption='User Picture')
            else:
                st.write("No picture available.")
        else:
            st.error("User not found.")

# Deposit Money
def deposit_money():
    st.subheader("Deposit Money")
    user_id = st.text_input("Enter User ID for Deposit:")
    amount = st.number_input("Enter Amount:", min_value=0.0, step=0.01)
    if st.button("Deposit"):
        user = users_collection.find_one({"user_id": user_id})
        if user:
            new_balance = user["balance"] + amount
            users_collection.update_one({"user_id": user_id}, {"$set": {"balance": new_balance}})
            transactions_collection.insert_one({"user_id": user_id, "type": "Deposit", "amount": amount})
            st.success(f"Deposited {amount}. New balance is {new_balance}.")
        else:
            st.error("User not found.")

# Withdraw Money
def withdraw_money():
    st.subheader("Withdraw Money")
    user_id = st.text_input("Enter User ID for Withdrawal:")
    amount = st.number_input("Enter Amount:", min_value=0.0, step=0.01)
    if st.button("Withdraw"):
        user = users_collection.find_one({"user_id": user_id})
        if user:
            current_balance = user["balance"]
            if current_balance - amount >= MINIMUM_BALANCE:
                new_balance = current_balance - amount
                users_collection.update_one({"user_id": user_id}, {"$set": {"balance": new_balance}})
                transactions_collection.insert_one({"user_id": user_id, "type": "Withdrawal", "amount": amount})
                st.success(f"Withdrew {amount}. New balance is {new_balance}.")
            else:
                st.error(f"Insufficient balance. Minimum balance of {MINIMUM_BALANCE} must be maintained.")
        else:
            st.error("User not found.")

# Check Balance
def check_balance():
    st.subheader("Check Balance")
    user_id = st.text_input("Enter User ID to Check Balance:")
    if st.button("Check Balance"):
        user = users_collection.find_one({"user_id": user_id})
        if user:
            st.info(f"Current balance is {user['balance']}.")
        else:
            st.error("User not found.")

# Streamlit Sidebar for Navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose an option", 
                              ("Open Account", "View Account Details", "Deposit Money", "Withdraw Money", "Check Balance"))

if option == "Open Account":
    open_account()
elif option == "View Account Details":
    view_account_details()
elif option == "Deposit Money":
    deposit_money()
elif option == "Withdraw Money":
    withdraw_money()
elif option == "Check Balance":
    check_balance()
