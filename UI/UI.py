import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import streamlit as st
st.set_page_config(
    page_title="Phishing Detection System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)
import numpy as np
import plotly.express as px
import pandas as pd
import re

from database.db_manager import (
    initialize_database,
    save_scan,
    get_history,
    get_statistics,
    get_daily_scan_trend,
    clear_user_history,
    get_global_statistics
)
from services.auth import (
    initialize_users,
    initialize_sessions,
    register_user,
    login_user,
    change_password,
    delete_user,
    get_user_role,
    get_all_users,
    admin_delete_user,
    activate_session,
    deactivate_session,
    is_session_active
)

initialize_database()
initialize_users()
initialize_sessions()

import sys
import os


from services.predictor import predict_email
from services.report_generator import generate_pdf_report
from services.batch_scanner import batch_scan_emails
from services.explainer import (
    explain_email,
    generate_highlighted_html
)
from services.gmail_service import (
    get_gmail_auth_url,
    get_credentials_from_code,
    fetch_recent_emails
)





# STREAMLIT UI

st.markdown(
    """
    <h1 style="text-align:center;">📧 Phishing Email Detection System</h1>
    <p style="text-align:center; font-size:18px;">
    AI-powered email phishing detection with explainable results
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False

# -------------------------
# AUTHENTICATION
# -------------------------
if "role" not in st.session_state:
    st.session_state.role = "user"

if not st.session_state.logged_in:

    auth_mode = st.sidebar.selectbox(

        "Authentication",

        [
            "Login",
            "Register"
        ]
    )

    username = st.sidebar.text_input(
        "Username"
    )

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if auth_mode == "Register":

        if st.sidebar.button("Register"):

            success = register_user(
                username,
                password
            )

            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = get_user_role(username)
                activate_session(username)
                st.rerun()

            else:

                st.sidebar.error("Username already exists.")

    else:

        if st.sidebar.button("Login"):

            authenticated = login_user(
                username,
                password
            )

            if authenticated:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = get_user_role(username)
                activate_session(username)
                st.rerun()

            else:

                st.sidebar.error("Invalid credentials.")

    
    st.stop()


# -------------------------
# SIDEBAR NAVIGATION
# -------------------------

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"
if st.session_state.role == "admin":
    if st.sidebar.button("🛡️ Admin Panel", use_container_width=True):
        st.session_state.menu = "Admin Panel"

st.sidebar.markdown("## 📌 Navigation")

if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.session_state.menu = "Dashboard"

if st.sidebar.button("📧 Scan Email", use_container_width=True):
    st.session_state.menu = "Scan Email"

if st.sidebar.button("📂 Batch Scan", use_container_width=True):
    st.session_state.menu = "Batch Scan"

if st.sidebar.button("📬 Gmail Scan", use_container_width=True):
    st.session_state.menu = "Gmail Scan"

if st.sidebar.button("📜 Scan History", use_container_width=True):
    st.session_state.menu = "Scan History"

st.sidebar.markdown("---")

if st.sidebar.button("👤 Account", use_container_width=True):
    st.session_state.menu = "Account"

if st.session_state.role != "admin":
    if st.sidebar.button("🛡️ Login as Admin", use_container_width=True):
        st.session_state.menu = "Admin Login"

if st.sidebar.button("ℹ️ About", use_container_width=True):
    st.session_state.menu = "About"

if st.sidebar.button("⚙️ System Info", use_container_width=True):
    st.session_state.menu = "System Info"

menu = st.session_state.menu


st.sidebar.markdown("---")
st.sidebar.info(
    "Deep Learning + LIME Explainability"
)

st.sidebar.markdown("---")
st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")

if st.sidebar.button("Logout"):
    deactivate_session(st.session_state.username)
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = "user"
    st.rerun()


st.info("Use the sidebar on the left to navigate through the application.")


# -------------------------
# DASHBOARD
# -------------------------

if menu == "Dashboard":

    st.header("📊 Dashboard")

    stats = get_statistics(st.session_state.username)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Scans",
        stats["total"]
    )

    col2.metric(
        "Phishing",
        stats["phishing"]
    )

    col3.metric(
        "Legitimate",
        stats["legitimate"]
    )

    col4.metric(
        "Phishing %",
        f"{stats['phishing_percentage']:.1f}%"
    )
    # -------------------------
    # CHART DATA
    # -------------------------

    chart_data = pd.DataFrame({

        "Category": [
            "Phishing",
            "Legitimate"
        ],

        "Count": [
            stats["phishing"],
            stats["legitimate"]
        ]
    })

    # -------------------------
    # PIE CHART
    # -------------------------

    pie_chart = px.pie(
        chart_data,
        names="Category",
        values="Count",
        title="Scan Distribution",
        color="Category",
        color_discrete_map={
            "Phishing": "red",
            "Legitimate": "green"
        }
    )

    st.plotly_chart(
        pie_chart,
        use_container_width=True
    )

    # -------------------------
    # BAR CHART
    # -------------------------

    bar_chart = px.bar(
        chart_data,
        x="Category",
        y="Count",
        title="Email Classification Counts",
        color="Category",
        color_discrete_map={
            "Phishing": "red",
            "Legitimate": "green"
        }
    )

    st.plotly_chart(
        bar_chart,
        use_container_width=True
    )

    # -------------------------
    # TREND DATA
    # -------------------------

    trend_rows = get_daily_scan_trend()

    trend_data = pd.DataFrame(

        trend_rows,

        columns=[
            "Date",
            "Scans"
        ]
    )

    # -------------------------
    # LINE CHART
    # -------------------------

    if not trend_data.empty:

        trend_chart = px.line(

            trend_data,

            x="Date",

            y="Scans",

            title="Daily Scan Activity"
        )

        st.plotly_chart(
            trend_chart,
            use_container_width=True
        )


if menu == "System Info":

    st.header("⚙️ System Information")

    st.subheader("Model Details")

    st.write("""
    - Model type: BiLSTM Deep Learning Model
    - Task: Binary email phishing classification
    - Classes: PHISHING and LEGITIMATE
    - Explainability: LIME
    - Interface: Streamlit
    - Database: SQLite
    """)

    st.subheader("Supported Inputs")

    st.write("""
    - Manual email text input
    - Single file upload: .txt, .eml
    - Batch file upload: .txt
    """)

    st.subheader("Outputs")

    st.write("""
    - Prediction label
    - Confidence score
    - LIME explanation
    - Highlighted explanation view
    - PDF report
    - CSV export
    - Scan history
    """)

    st.subheader("Current Application Version")

    st.info("Version 1.0 - Standalone MVP")



if menu == "Scan Email":
    st.header("📧 Scan Email")
    email_text = st.text_area("Paste Email Text Here")

    uploaded_file = st.file_uploader(
        "Or upload an email file",
        type=["txt", "eml"]
    )

    if uploaded_file is not None:

        if uploaded_file.size == 0:

            st.error("Uploaded file is empty.")

        elif uploaded_file.size > 2 * 1024 * 1024:

            st.error("File is too large. Please upload a file smaller than 2 MB.")

        else:

            st.success("Email file loaded successfully.")

            email_text = uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

            st.text_area(
                "Uploaded Email Content",
                email_text,
                height=250
            )

        

    if st.button("Detect"):

        if email_text.strip() == "":

            st.warning(
                "Please enter email content."
            )

        else:

            label, confidence = predict_email(email_text)

            save_scan(
                st.session_state.username,
                email_text,
                label,
                confidence
            )

            result_placeholder = st.empty()

            if label == "PHISHING":

                result_placeholder.error(
                    f"⚠️ {label} ({confidence:.4f})"
                )

            else:

                result_placeholder.success(
                    f"✅ {label} ({confidence:.4f})"
                )

        st.subheader("🔍 Explanation")

        explanation = explain_email(
            email_text
        )

        highlighted_html = generate_highlighted_html(

            email_text,
            explanation
        )

        st.markdown(
            f"""
            <div style="line-height:1.8; font-size:16px;">
                {highlighted_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        # -------------------------
        # GENERATE PDF REPORT
        # -------------------------

        pdf_path = generate_pdf_report(

            email_text,
            label,
            confidence,
            explanation

        )

        with open(pdf_path, "rb") as pdf_file:

            st.download_button(

                label="📄 Download PDF Report",

                data=pdf_file,

                file_name="phishing_report.pdf",

                mime="application/pdf"
            )


# -------------------------
# BATCH SCAN
# -------------------------

if menu == "Batch Scan":

    st.header("📂 Batch Email Scanner")

    batch_file = st.file_uploader(

        "Upload batch email file",

        type=["txt"],

        key="batch_upload"
    )

    if batch_file is not None:

        if batch_file.size == 0:

            st.error("Uploaded batch file is empty.")
            st.stop()

        elif batch_file.size > 5 * 1024 * 1024:

            st.error("Batch file is too large. Please upload a file smaller than 5 MB.")
            st.stop()

        content = batch_file.read().decode("utf-8", errors="ignore")

        # Split emails
        emails = re.split(
            r"\n\s*\n",
            content.strip()
        )

        if len(emails) == 0:

            st.warning("No valid emails were detected in the file.")
            st.stop()

        emails = [
            email.strip()
            for email in emails
            if email.strip()
        ]

        st.write(
            f"Detected {len(emails)} emails."
        )

        if st.button("Run Batch Scan"):

            results = batch_scan_emails(emails)

            for result in results:
                save_scan(
                    st.session_state.username,
                    result["email"],
                    result["prediction"],
                    result["confidence"]
                )

            

            results_df = pd.DataFrame(results)

            st.dataframe(results_df)

            # Export CSV
            csv = results_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(

                label="📥 Download Batch Results",

                data=csv,

                file_name="batch_scan_results.csv",

                mime="text/csv"
            ) 


if menu == "Gmail Scan":

    st.header("📬 Gmail Inbox Scanner")

    query_params = st.query_params

    if "gmail_credentials" not in st.session_state:

        if "code" in query_params:

            code = query_params["code"]

            credentials = get_credentials_from_code(
                code
            )

            st.session_state.gmail_credentials = credentials

            st.success("Gmail connected successfully.")

        else:

            auth_url = get_gmail_auth_url()

            st.link_button(
                "Connect Gmail Account",
                auth_url
            )

            st.stop()

    max_emails = st.slider(
        "Number of recent emails to scan",
        1,
        10,
        5
    )

    if st.button("Scan Gmail Inbox"):

        emails = fetch_recent_emails(
            st.session_state.gmail_credentials,
            max_results=max_emails
        )

        for email in emails:

            full_text = f"""
            From: {email['sender']}
            Subject: {email['subject']}

            {email['body']}
            """

            label, confidence = predict_email(
                full_text
            )

            save_scan(
                st.session_state.username,
                full_text,
                label,
                confidence
            )

            if label == "PHISHING":

                st.error(
                    f"⚠️ {label} ({confidence:.4f})"
                )

            else:

                st.success(
                    f"✅ {label} ({confidence:.4f})"
                )

            st.write(f"**From:** {email['sender']}")
            st.write(f"**Subject:** {email['subject']}")
            st.markdown("---")      


if menu == "Scan History":

    st.header("📜 Scan History")

    history = get_history(st.session_state.username)

    for row in history:

        prediction = row[2]

        confidence = row[3]

        timestamp = row[4]

        st.write(

            f"""
            Prediction: {prediction}
            | Confidence: {confidence}
            | Time: {timestamp}
            """
        )

    # -------------------------
    # EXPORT HISTORY
    # -------------------------

    history_data = pd.DataFrame(

        history,

        columns=[
            "ID",
            "Email",
            "Prediction",
            "Confidence",
            "Timestamp"
        ]
    )

    csv = history_data.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(

        label="📥 Download Scan History CSV",

        data=csv,

        file_name="scan_history.csv",

        mime="text/csv"
    )



if menu == "Admin Panel":

    if st.session_state.role != "admin":

        st.error("Access denied.")
        st.stop()

    st.header("🛡️ Admin Panel")

    global_stats = get_global_statistics()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total System Scans", global_stats["total"])
    col2.metric("Total Phishing", global_stats["phishing"])
    col3.metric("Total Legitimate", global_stats["legitimate"])
    col4.metric("Active Users", global_stats["active_users"])

    admin_chart_data = pd.DataFrame({

        "Category": [
            "PHISHING",
            "LEGITIMATE"
        ],

        "Count": [
            global_stats["phishing"],
            global_stats["legitimate"]
        ]
    })

    admin_pie_chart = px.pie(

        admin_chart_data,

        names="Category",

        values="Count",

        title="Global Scan Distribution",

        color="Category",

        color_discrete_map={
            "PHISHING": "red",
            "LEGITIMATE": "green"
        }
    )

    st.plotly_chart(
        admin_pie_chart,
        use_container_width=True
    )

    admin_bar_chart = px.bar(

        admin_chart_data,

        x="Category",

        y="Count",

        title="Global Email Classification Counts",

        color="Category",

        color_discrete_map={
            "PHISHING": "red",
            "LEGITIMATE": "green"
        }
    )

    st.plotly_chart(
        admin_bar_chart,
        use_container_width=True
    )

    st.info(
        f"Overall phishing percentage: {global_stats['phishing_percentage']:.1f}%"
    )

    st.markdown("---")
    st.subheader("👥 User Management")

    users = get_all_users()

    users_df = pd.DataFrame(
        users,
        columns=[
            "ID",
            "Username",
            "Role"
        ]
    )
    

    st.dataframe(users_df)

    usernames = [
        user[1]
        for user in users
        if user[1] != st.session_state.username
    ]

    selected_user = st.selectbox(
        "Select user to force logout or delete",
        usernames
    )

    if st.button("Force Logout Selected User"):

        deactivate_session(selected_user)

        st.success(
            f"User '{selected_user}' has been logged out."
        )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this user"
    )

    if st.button("Delete Selected User"):

        if confirm_delete:

            admin_delete_user(selected_user)

            st.success(
                f"User '{selected_user}' deleted successfully."
            )

            st.rerun()

        else:

            st.error(
                "Please confirm before deleting the user."
            )

    


if menu == "Admin Login":

    st.header("🛡️ Admin Login")

    admin_username = st.text_input("Admin Username")
    admin_password = st.text_input("Admin Password", type="password")

    if st.button("Login as Admin"):

        if login_user(admin_username, admin_password):

            role = get_user_role(admin_username)

            if role == "admin":

                st.session_state.logged_in = True
                st.session_state.username = admin_username
                st.session_state.role = "admin"

                activate_session(admin_username)

                st.success("Admin login successful.")
                st.rerun()

            else:

                st.error("This account is not an admin account.")

        else:

            st.error("Invalid admin credentials.")


if menu == "Account":

    st.header("👤 My Account")

    st.write(f"**Username:** {st.session_state.username}")

    st.subheader("Change Password")

    old_password = st.text_input(
        "Current Password",
        type="password"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm New Password",
        type="password"
    )

    if st.button("Change Password"):

        if new_password != confirm_password:

            st.error("New passwords do not match.")

        elif new_password.strip() == "":

            st.warning("New password cannot be empty.")

        else:

            success = change_password(
                st.session_state.username,
                old_password,
                new_password
            )

            if success:

                st.success("Password changed successfully.")

            else:

                st.error("Current password is incorrect.")

    st.markdown("---")

    st.subheader("Clear Scan History")

    st.warning(
        "This will permanently delete only your scan history. Your account will remain active."
    )

    confirm_clear = st.checkbox(
        "I understand and want to clear my scan history"
    )

    if st.button("Clear My Scan History"):

        if confirm_clear:

            clear_user_history(
                st.session_state.username
            )

            st.success(
                "Your scan history has been cleared."
            )

        else:

            st.error(
                "Please confirm before clearing your scan history."
            )

    st.markdown("---")

    st.subheader("Delete Account")

    st.warning(
        "Deleting your account is permanent."
    )

    delete_password = st.text_input(
        "Enter your password to confirm account deletion",
        type="password",
        key="delete_password"
    )

    if st.button("Delete My Account"):

        success = delete_user(
            st.session_state.username,
            delete_password
        )

        if success:

            st.success("Account deleted successfully.")

            st.session_state.logged_in = False
            st.session_state.username = ""

            st.rerun()

        else:

            st.error("Password incorrect. Account not deleted.")


if menu == "About":

    st.header("ℹ️ About")

    st.write("""

    This application uses a BiLSTM deep learning model
    combined with Explainable AI (LIME)
    to detect phishing emails.

    Features:
    - Email scanning
    - File upload support
    - Prediction confidence
    - Scan history
    - Dashboard analytics

    """)


st.markdown(
    """
    <hr>
    <p style="text-align:center; font-size:13px;">
    Developed for explainable email phishing detection using BiLSTM and LIME.
    </p>
    """,
    unsafe_allow_html=True
)