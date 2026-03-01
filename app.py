import streamlit as st
import sqlite3
from datetime import datetime

# ---------------- DATABASE CONNECTION ----------------
conn = sqlite3.connect("bank.db", check_same_thread=False)
cursor = conn.cursor()

# Create Tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS accounts(
    account_no INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_no INTEGER,
    type TEXT,
    amount REAL,
    date TEXT
)
""")

conn.commit()

# ---------------- FUNCTIONS ----------------

def create_account(name, age, gender):
    cursor.execute("INSERT INTO accounts (name, age, gender, balance) VALUES (?, ?, ?, ?)",
                   (name, age, gender, 0))
    conn.commit()
    return cursor.lastrowid

def deposit(account_no, amount):
    cursor.execute("UPDATE accounts SET balance = balance + ? WHERE account_no = ?",
                   (amount, account_no))
    cursor.execute("INSERT INTO transactions (account_no, type, amount, date) VALUES (?, ?, ?, ?)",
                   (account_no, "Deposit", amount, datetime.now()))
    conn.commit()

def withdraw(account_no, amount):
    cursor.execute("SELECT balance FROM accounts WHERE account_no = ?", (account_no,))
    balance = cursor.fetchone()

    if balance and balance[0] >= amount:
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE account_no = ?",
                       (amount, account_no))
        cursor.execute("INSERT INTO transactions (account_no, type, amount, date) VALUES (?, ?, ?, ?)",
                       (account_no, "Withdraw", amount, datetime.now()))
        conn.commit()
        return True
    return False

def get_balance(account_no):
    cursor.execute("SELECT balance FROM accounts WHERE account_no = ?", (account_no,))
    return cursor.fetchone()

def get_transactions(account_no):
    cursor.execute("SELECT type, amount, date FROM transactions WHERE account_no = ?", (account_no,))
    return cursor.fetchall()

# ---------------- STREAMLIT UI ----------------

st.set_page_config(page_title="Banking Management System", layout="wide")

st.title("🏦 Banking Management System")
menu = st.sidebar.selectbox("Menu", [
    "Create Account",
    "Deposit",
    "Withdraw",
    "Check Balance",
    "Transaction History"
])

# ---------------- CREATE ACCOUNT ----------------
if menu == "Create Account":
    st.subheader("Create New Account")
    name = st.text_input("Enter Name")
    age = st.number_input("Enter Age", min_value=18, max_value=100)
    gender = st.selectbox("Select Gender", ["Male", "Female", "Other"])

    if st.button("Create Account"):
        if name:
            acc_no = create_account(name, age, gender)
            st.success(f"Account Created Successfully! Your Account Number is {acc_no}")
        else:
            st.error("Name cannot be empty!")

# ---------------- DEPOSIT ----------------
elif menu == "Deposit":
    st.subheader("Deposit Money")
    acc_no = st.number_input("Enter Account Number", step=1)
    amount = st.number_input("Enter Amount", min_value=1.0)

    if st.button("Deposit"):
        deposit(acc_no, amount)
        st.success("Amount Deposited Successfully!")

# ---------------- WITHDRAW ----------------
elif menu == "Withdraw":
    st.subheader("Withdraw Money")
    acc_no = st.number_input("Enter Account Number", step=1)
    amount = st.number_input("Enter Amount", min_value=1.0)

    if st.button("Withdraw"):
        if withdraw(acc_no, amount):
            st.success("Amount Withdrawn Successfully!")
        else:
            st.error("Insufficient Balance or Invalid Account!")

# ---------------- CHECK BALANCE ----------------
elif menu == "Check Balance":
    st.subheader("Check Account Balance")
    acc_no = st.number_input("Enter Account Number", step=1)

    if st.button("Check"):
        balance = get_balance(acc_no)
        if balance:
            st.info(f"Current Balance: ₹ {balance[0]}")
        else:
            st.error("Account Not Found!")

# ---------------- TRANSACTION HISTORY ----------------
elif menu == "Transaction History":
    st.subheader("Transaction History")
    acc_no = st.number_input("Enter Account Number", step=1)

    if st.button("View"):
        transactions = get_transactions(acc_no)
        if transactions:
            for t in transactions:
                st.write(f"{t[2]} | {t[0]} | ₹ {t[1]}")
        else:
            st.warning("No Transactions Found!")