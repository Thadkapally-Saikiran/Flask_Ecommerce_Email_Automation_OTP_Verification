"""
Email Automation System with OTP Verification
Flask Application Main File
"""

# Import core Flask modules and extensions
from flask import Flask, render_template, request, session, redirect, url_for, flash
# Import custom email handling classes
from email_sender import EmailSender, DeliveryNotification
import random  # For OTP generation in DeliveryNotification class

# Initialize Flask application
app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Required for session encryption

# SMTP Configuration (Should use environment variables in production)
SMTP_SERVER = "smtp.gmail.com"        # Gmail's SMTP server address
SMTP_PORT = 587                       # Standard secure port for SMTP with TLS
SENDER_EMAIL = "thadkapallysaikiran2001@gmail.com"  # Sender's email address
SENDER_PASSWORD = "ktvq inal srse itjg" # Application-specific password

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Homepage route - Collects number of recipients
    GET: Shows input form
    POST: Validates number and stores in session
    """
    if request.method == "POST":
        try:
            # Validate numeric input
            num_recipients = int(request.form.get("num_recipients"))
            # Store in session for multi-step form handling
            session["num_recipients"] = num_recipients
            return redirect(url_for("recipient_details"))
        except ValueError:
            # Handle non-numeric input errors
            flash("Please enter a valid number", "danger")
    # Render initial input form
    return render_template("index.html")

@app.route("/recipient-details", methods=["GET", "POST"])
def recipient_details():
    """
    Recipient Details Collection Route
    GET: Shows dynamic form based on recipient count
    POST: Processes form data and sends emails
    """
    # Prevent direct access without session data
    if "num_recipients" not in session:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        # Initialize email sender and storage for notifications
        notifications = []
        email_sender = EmailSender(SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD)
        
        try:
            # Establish SMTP connection
            email_sender.connect()
            
            # Process each recipient's data
            for i in range(session["num_recipients"]):
                # Collect form data for each recipient
                recipient_data = {
                    "email": request.form.get(f"email_{i}"),
                    "product_id": request.form.get(f"product_id_{i}"),
                    "product_name": request.form.get(f"product_name_{i}"),
                    "delivery_status": request.form.get(f"delivery_status_{i}"),
                    "payment_method": request.form.get(f"payment_method_{i}"),
                    "delivery_day": request.form.get(f"delivery_day_{i}"),
                    "delivery_month": int(request.form.get(f"delivery_month_{i}")),
                    "delivery_year": request.form.get(f"delivery_year_{i}")
                }
                
                # Create notification object with generated OTP
                notification = DeliveryNotification(**recipient_data)
                # Send email through SMTP
                email_sender.send_email(
                    notification.recipient_email,
                    notification.get_email_subject(),
                    notification.get_email_body()
                )
                
                # Store notification details for verification phase
                notifications.append({
                    "email": notification.recipient_email,
                    "otp": notification.otp
                })
            
            # Store in session for next step
            session["notifications"] = notifications
            flash("Emails sent successfully!", "success")
            return redirect(url_for("verify_otp"))
        
        except Exception as e:
            # Handle any errors during email sending
            flash(f"Error sending emails: {str(e)}", "danger")
        finally:
            # Ensure SMTP connection is closed
            email_sender.close()
    
    # Show dynamic form for recipient details
    return render_template("recipient_details.html", 
                         num_recipients=session["num_recipients"])

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    """
    OTP Verification Route
    GET: Shows OTP input forms
    POST: Validates OTPs against stored values
    """
    # Prevent direct access without completed previous steps
    if "notifications" not in session:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        results = []
        # Validate each recipient's OTP
        for i, notification in enumerate(session["notifications"]):
            user_otp = request.form.get(f"otp_{i}")
            is_valid = str(user_otp) == str(notification["otp"])
            results.append({
                "email": notification["email"],
                "status": "Valid" if is_valid else "Invalid"
            })
        
        # Show verification results
        return render_template("verification_results.html", results=results)
    
    # Display OTP input forms
    return render_template("verify_otp.html", 
                          notifications=session["notifications"])

if __name__ == "__main__":
    # Run in debug mode for development
    app.run(port=5003, debug=True)