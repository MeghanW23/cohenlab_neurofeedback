import os
import glob
import pandas as pd
from datetime import datetime
import smtplib
from email.message import EmailMessage
from getpass import getpass

# === USER INPUT ===
user_name = input("Enter your name (for email sign-off): ")
sender_email = input("Enter your Outlook email address: ")
password = getpass("Enter your email password (or app-specific password): ")
dropbox_user_folder = input("Enter your Dropbox subfolder (e.g., 'Sofia Heras' or 'Meghan Walsh'): ").strip()

# === BUILD DROPBOX PATH ===
dropbox_user_folder = input("Enter your Dropbox subfolder (e.g., 'Sofia Heras' or 'Meghan Walsh'): ").strip()
dropbox_base = os.path.expanduser(f"~/BCH Dropbox/{dropbox_user_folder}/#154 fMRI Neurofeedback and Task Performance in ADHD")
excel_pattern = os.path.join(dropbox_base, "#154*.xls*")  # matches .xls and .xlsx

# === FIND MOST RECENT FILE ===
excel_files = glob.glob(excel_pattern)
if not excel_files:
    raise FileNotFoundError(f"No Excel files found matching {excel_pattern}")

latest_file = max(excel_files, key=os.path.getmtime)
print(f"Using latest RPR list: {latest_file}")

# === LOAD EXCEL ===
df = pd.read_excel(latest_file, header=14)
today = datetime.today()

# === SET UP SMTP ===
smtp_server = "smtp.office365.com"
smtp_port = 587

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(sender_email, password)

    for idx, row in df.iterrows():
        email = row.get("E-mail")
        if pd.notna(email):
            parent_name = row.get("First Name (Parent1)", "").strip()
            child_name = row.get("Child's First Name", "").strip()
            dob = row.get("Date of Birth")

            if pd.isna(dob):
                continue

            age = (today - pd.to_datetime(dob)).days // 365

            body = f"""Hi {parent_name},

We hope this email finds you well. We are contacting you because {child_name} is enrolled in the TNC Participant Registry at Boston Children's Hospital. We would like to know if ​{child_name} is interested in participating in our research study on attention training. If you no longer wish to be enrolled in the TNC Participant Registry at Boston Children’s Hospital, please let us know so we can contact the administrator.

This study involves:
• Performing computer-based attention activities
• Completing questionnaires
• Undergoing task-based MRIs

Participants will be asked to do 4 sessions in the MRI Scanner, but this can vary for up to 8 sessions depending on how well we feel the experiment fits {child_name}. Participants receive $100 and a parking voucher upon completion of each visit.

We are located at 2 Brookline Place, Brookline MA 02445, and we can provide either a voucher to cover the cost of parking at the parking garage or payment for the cost of a round-trip MBTA ride.

For this study, we are looking for participants who:
• Have an ADHD diagnosis
• Are currently taking stimulant medication for ADHD and are willing to abstain from taking the medication on the day of some MRI scans until after the scan is over
• Are 12 years or older
• Are able to follow one-step directions
• Are able to complete an MRI scan: Research MRI participants can't have braces, non-removable jewelry, ferromagnetic material in the body, etc. If you aren't sure if {child_name} is able to meet the requirements to do a research MRI scan, please just let us know and we can contact radiology to figure out if {child_name} is eligible!

Please let me know if you are interested and meet the eligibility criteria above! Let me know if you have any questions!"""

            if age < 18:
                body += f"""\n\n*Please note that since {child_name} is under 18, a parent or guardian will need to be present for all sessions.*"""

            body += f"""\n\nBest,\n\n{user_name}\nNeurofeedback Study Coordinator"""

            # === SEND EMAIL ===
            msg = EmailMessage()
            msg["Subject"] = "Potential Neurofeedback ADHD Cohen Lab Study Participation"
            msg["From"] = sender_email
            msg["To"] = email
            msg.set_content(body)

            #server.send_message(msg)
            #print(f"Email sent to: {email} ({child_name}, age {age})")

            print(f"\n[TEST MODE] Would send email to: {email} (Child: {child_name}, Age: {age})")
            print(f"--- Email preview below ---\n{body}\n---\n")
