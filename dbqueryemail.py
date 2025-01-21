import cx_Oracle
import smtplib
from email.mime.text import MIMEText
import os

# Database Configuration
db_config = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "dsn": os.getenv("DB_DSN"),
}

# Email Configuration
smtp_config = {
    "smtp_server": os.getenv("SMTP_SERVER"),
    "smtp_port": int(os.getenv("SMTP_PORT", 587)),
    "email_user": os.getenv("EMAIL_USER"),
    "email_password": os.getenv("EMAIL_PASSWORD"),
    "recipient_email": os.getenv("RECIPIENT_EMAIL"),
}

# Query Configuration
query = os.getenv("QUERY", "SELECT COUNT(*) FROM your_table")

def get_record_count():
    """Query the database and return the count of records."""
    try:
        with cx_Oracle.connect(**db_config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result else 0
    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")
        return None

def send_email(record_count):
    """Send an email with the record count."""
    try:
        subject = "Database Record Count"
        body = f"The count of records is: {record_count}"
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = smtp_config["email_user"]
        msg["To"] = smtp_config["recipient_email"]

        with smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"]) as server:
            server.starttls()
            server.login(smtp_config["email_user"], smtp_config["email_password"])
            server.sendmail(
                smtp_config["email_user"],
                smtp_config["recipient_email"],
                msg.as_string(),
            )
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    record_count = get_record_count()
    if record_count is not None:
        send_email(record_count)
    else:
        print("Failed to retrieve the record count.")
