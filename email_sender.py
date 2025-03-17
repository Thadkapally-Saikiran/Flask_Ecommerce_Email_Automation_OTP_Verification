"""
Email Handling Module
Contains SMTP connection management and email content generation
"""

import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    """
    SMTP Email Sending Handler
    Manages connection lifecycle and email delivery
    """
    
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialize SMTP configuration
        :param smtp_server: SMTP server hostname
        :param smtp_port: SMTP server port
        :param sender_email: From address for emails
        :param sender_password: SMTP authentication password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.server = None  # Will hold SMTP connection

    def connect(self):
        """Establish secure SMTP connection with TLS"""
        self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.server.starttls()  # Enable TLS encryption
        self.server.login(self.sender_email, self.sender_password)

    def send_email(self, recipient_email, subject, body):
        """
        Construct and send email message
        :param recipient_email: Target email address
        :param subject: Email subject line
        :param body: Plain text email content
        """
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))  # Add text body
        self.server.send_message(msg)  # Send through SMTP

    def close(self):
        """Properly close SMTP connection"""
        if self.server:
            self.server.quit()

class DeliveryNotification:
    """
    Email Content Generator and OTP Manager
    Creates delivery notifications with verification OTPs
    """
    
    # Month number to name mapping
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    
    def __init__(self, email, product_id, product_name, delivery_status,
                 payment_method, delivery_day, delivery_month, delivery_year):
        """
        Initialize delivery notification
        :param email: Recipient's email address
        :param product_id: Unique product identifier
        :param product_name: Human-readable product name
        :param delivery_status: Current delivery state
        :param payment_method: Chosen payment method
        :param delivery_day: Expected delivery day
        :param delivery_month: Expected delivery month (1-12)
        :param delivery_year: Expected delivery year
        """
        self.recipient_email = email
        self.product_id = product_id
        self.product_name = product_name
        self.delivery_status = delivery_status
        self.payment_method = payment_method
        self.delivery_day = delivery_day
        self.delivery_month = delivery_month
        self.delivery_year = delivery_year
        self.otp = random.randint(11111, 99999)  # Generate 5-digit OTP

    def get_email_subject(self):
        """Generate dynamic email subject line"""
        return f"Order Update for {self.product_name} (ID: {self.product_id})"

    def get_email_body(self):
        """Construct email body with all details and OTP"""
        return (
            f"Hello,\n\n"
            f"Product: {self.product_name}\n"
            f"Status: {self.delivery_status}\n"
            f"Payment Method: {self.payment_method}\n"
            f"Expected Delivery: {self.delivery_day} "
            f"{self.months.get(self.delivery_month, '')} {self.delivery_year}\n\n"
            f"Your verification OTP: {self.otp}\n\n"
            "Thank you for your purchase!"
        )