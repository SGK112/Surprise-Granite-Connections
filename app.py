from flask import Flask, request, jsonify
import os
import openai
from flask_cors import CORS
import requests, csv, math
from io import StringIO
# Add these imports to your app.py
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request, jsonify

# Add this route to your Flask app
@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        # Get request data
        data = request.json
        
        # Extract data
        to_email = data.get('to', 'info@surprisegranite.com')
        subject = data.get('subject', 'New Countertop Estimate Request')
        customer_name = data.get('customerName')
        customer_email = data.get('customerEmail')
        customer_phone = data.get('customerPhone', 'Not provided')
        customer_message = data.get('customerMessage', 'No additional message')
        estimate_details = data.get('estimateDetails', {})
        website_source = data.get('websiteSource', 'Website')
        
        # Validate required fields
        if not customer_name or not customer_email or not estimate_details:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create HTML for company email
        company_html = f"""
        <h2>New Countertop Estimate Request</h2>
        <h3>Customer Information:</h3>
        <p><strong>Name:</strong> {customer_name}</p>
        <p><strong>Email:</strong> {customer_email}</p>
        <p><strong>Phone:</strong> {customer_phone}</p>
        <p><strong>Message:</strong> {customer_message}</p>
        <p><strong>Source:</strong> {website_source}</p>
        
        <h3>Estimate Details:</h3>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th style="text-align: left; background-color: #f2f2f2;">Item</th>
                <th style="text-align: left; background-color: #f2f2f2;">Details</th>
            </tr>
            <tr>
                <td><strong>Material</strong></td>
                <td>{estimate_details.get('material', 'N/A')} ({estimate_details.get('quality', 'N/A')})</td>
            </tr>
            <tr>
                <td><strong>Square Feet</strong></td>
                <td>{estimate_details.get('squareFeet', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Edge Treatment</strong></td>
                <td>{estimate_details.get('edge', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Sink Cutouts</strong></td>
                <td>{estimate_details.get('sinks', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Material Cost</strong></td>
                <td>{estimate_details.get('materialCost', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Edge Cost</strong></td>
                <td>{estimate_details.get('edgeCost', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Sink Cost</strong></td>
                <td>{estimate_details.get('sinkCost', 'N/A')}</td>
            </tr>
            <tr style="font-weight: bold; background-color: #f9f9f9;">
                <td><strong>Total Estimate</strong></td>
                <td>{estimate_details.get('totalCost', 'N/A')}</td>
            </tr>
        </table>
        """
        
        # Create HTML for customer email
        customer_html = f"""
        <h2>Your Surprise Granite Countertop Estimate</h2>
        <p>Dear {customer_name},</p>
        <p>Thank you for your interest in Surprise Granite! We've received your estimate request and one of our specialists will contact you shortly to discuss your project in detail.</p>
        
        <h3>Your Estimate Details:</h3>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th style="text-align: left; background-color: #f2f2f2;">Item</th>
                <th style="text-align: left; background-color: #f2f2f2;">Details</th>
            </tr>
            <tr>
                <td><strong>Material</strong></td>
                <td>{estimate_details.get('material', 'N/A')} ({estimate_details.get('quality', 'N/A')})</td>
            </tr>
            <tr>
                <td><strong>Square Feet</strong></td>
                <td>{estimate_details.get('squareFeet', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Edge Treatment</strong></td>
                <td>{estimate_details.get('edge', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Sink Cutouts</strong></td>
                <td>{estimate_details.get('sinks', 'N/A')}</td>
            </tr>
            <tr style="font-weight: bold; background-color: #f9f9f9;">
                <td><strong>Total Estimate</strong></td>
                <td>{estimate_details.get('totalCost', 'N/A')}</td>
            </tr>
        </table>
        
        <p><em>Please note: This is a preliminary estimate based on the information provided. Your final quote may vary based on specific project requirements and material selection.</em></p>
        
        <p>If you have any questions or would like to schedule a consultation, please contact us at:</p>
        <p>Phone: (623) 214-3599<br>
        Email: info@surprisegranite.com</p>
        
        <p>Thank you for choosing Surprise Granite!</p>
        <p>The Surprise Granite Team</p>
        """
        
        # Email configuration
        email_host = os.environ.get('EMAIL_HOST')
        email_port = int(os.environ.get('EMAIL_PORT', 587))
        email_user = os.environ.get('EMAIL_USER')
        email_pass = os.environ.get('EMAIL_PASS')
        email_from = os.environ.get('EMAIL_FROM', 'Surprise Granite <info@surprisegranite.com>')
        
        # Send email to company
        send_html_email(
            sender=email_from,
            recipient=to_email,
            subject=subject,
            html_content=company_html,
            smtp_server=email_host,
            smtp_port=email_port,
            smtp_user=email_user,
            smtp_pass=email_pass
        )
        
        # Send confirmation email to customer
        send_html_email(
            sender=email_from,
            recipient=customer_email,
            subject='Your Surprise Granite Countertop Estimate',
            html_content=customer_html,
            smtp_server=email_host,
            smtp_port=email_port,
            smtp_user=email_user,
            smtp_pass=email_pass
        )
        
        return jsonify({'success': True, 'message': 'Emails sent successfully'}), 200
        
    except Exception as e:
        print(f"Email error: {str(e)}")
        return jsonify({'error': 'Failed to send email', 'details': str(e)}), 500

# Helper function to send HTML emails
def send_html_email(sender, recipient, subject, html_content, smtp_server, smtp_port, smtp_user, smtp_pass):
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

app = Flask(__name__)

# Approved domains exactly as they appear in the browser
approved_origins = [
    "https://www.surprisegranite.com",
    "https://www.remodely.ai"
]

# Enable CORS for all routes for the approved origins
CORS(app, resources={r"/*": {"origins": approved_origins}})

# Load OpenAI API Key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key. Please set it in environment variables.")
openai.api_key = OPENAI_API_KEY

def get_pricing_data():
    """
    Fetch pricing data from the published Google Sheets CSV.
    Only pull the necessary columns:
      - "Color Name"
      - "Cost/SqFt"
      - "Total/SqFt"
    The rest of the data is ignored.
    """
    url = ("https://docs.google.com/spreadsheets/d/e/"
           "2PACX-1vRWyYuTQxC8_fKNBg9_aJiB7NMFztw6mgdhN35lo8sRL45MvncRg4D217lopZxuw39j5aJTN6TP4Elh"
           "/pub?output=csv")
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception("Could not fetch pricing data")
    csv_text = response.text
    csv_file = StringIO(csv_text)
    reader = csv.DictReader(csv_file)
    pricing = {}
    for row in reader:
        color = row["Color Name"].strip().lower()
        try:
            cost_sqft = float(row["Cost/SqFt"])
        except Exception:
            cost_sqft = 50.0
        try:
            color_total_sqft = float(row["Total/SqFt"])
        except Exception:
            color_total_sqft = 100.0
        pricing[color] = {"cost": cost_sqft, "total_sqft": color_total_sqft}
    return pricing

@app.route("/")
def home():
    return "<h1>Surprise Granite AI Chatbot</h1><p>Your AI assistant is ready.</p>"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "Missing user input"}), 400
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful remodeling assistant for Surprise Granite."},
                {"role": "user", "content": user_input}
            ]
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/estimate", methods=["POST", "OPTIONS"])
def estimate():
    # Handle preflight OPTIONS requests for CORS
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    if not data or not data.get("totalSqFt"):
        return jsonify({"error": "Missing project data"}), 400

    try:
        # Extract and clean input data
        total_sq_ft = float(data.get("totalSqFt"))
        vendor = data.get("vendor", "default vendor").strip()
        color = data.get("color", "").strip().lower()
        demo = data.get("demo", "no").strip()
        sink_qty = float(data.get("sinkQty", 0))
        cooktop_qty = float(data.get("cooktopQty", 0))
        sink_type = data.get("sinkType", "standard").strip().lower()
        cooktop_type = data.get("cooktopType", "standard").strip().lower()
        backsplash = data.get("backsplash", "no").strip().lower()
        # Tile option: expected as a float ($35, $65, or $85)
        tile_option = float(data.get("tileOption", 0))
        edge_detail = data.get("edgeDetail", "standard").strip().lower()
        job_name = data.get("jobName", "N/A").strip()
        job_type = data.get("jobType", "fabricate and install").strip().lower()
        customer_name = data.get("customerName", "Valued Customer").strip()

        # Get live pricing data from CSV
        pricing_data = get_pricing_data()
        pricing_info = pricing_data.get(color, {"cost": 50, "total_sqft": 100})
        price_per_sqft = pricing_info["cost"]
        color_total_sqft = pricing_info["total_sqft"]

        # Calculate material cost and adjustments
        material_cost = total_sq_ft * price_per_sqft
        if demo.lower() == "yes":
            material_cost *= 1.10  # add 10% for demo
        sink_cost = sink_qty * (150 if sink_type == "premium" else 100)
        cooktop_cost = cooktop_qty * (160 if cooktop_type == "premium" else 120)
        # If backsplash is yes, use tile_option if > 0; otherwise default to $20/sqft
        backsplash_cost = total_sq_ft * (tile_option if tile_option > 0 else 20) if backsplash == "yes" else 0

        if edge_detail == "premium":
            multiplier = 1.05
        elif edge_detail == "custom":
            multiplier = 1.10
        else:
            multiplier = 1.0
        material_cost *= multiplier

        preliminary_total = material_cost + sink_cost + cooktop_cost + backsplash_cost

        # Calculate slab count assuming 20% waste
        effective_sq_ft = total_sq_ft * 1.20
        slab_count = math.ceil(effective_sq_ft / color_total_sqft)

        # Determine labor rate: use base labor rate $45 with a markup factor.
        markup = 1.35 if job_type == "slab only" else 1.30
        base_labor_rate = 45  # default for Granite/Quartz
        labor_cost = total_sq_ft * base_labor_rate * markup

        total_project_cost = preliminary_total + labor_cost
        final_cost_per_sqft = f"{(total_project_cost / total_sq_ft):.2f}" if total_sq_ft else "0.00"

        # Build a detailed prompt for GPT‑4 to generate a professional estimate
        prompt = (
            f"Surprise Granite Detailed Estimate\n\n"
            f"Customer: Mr./Ms. {customer_name}\n"
            f"Job Name: {job_name}\n"
            f"Job Type: {job_type}\n"
            f"Project Area: {total_sq_ft} sq ft (with 20% waste: {effective_sq_ft:.2f} sq ft)\n"
            f"Vendor: {vendor}\n"
            f"Material (Color): {color.title()}\n"
            f"Price per Sq Ft for {color.title()}: ${price_per_sqft:.2f}\n"
            f"Material Cost: ${material_cost:.2f}\n"
            f"Sink Count: {sink_qty} ({sink_type}), Cost: ${sink_cost:.2f}\n"
            f"Cooktop Count: {cooktop_qty} ({cooktop_type}), Cost: ${cooktop_cost:.2f}\n"
            f"Backsplash Cost: ${backsplash_cost:.2f}\n"
            f"Number of Slabs Needed: {slab_count} (Each slab: {color_total_sqft} sq ft)\n"
            f"Preliminary Total (Materials): ${preliminary_total:.2f}\n"
            f"Labor Cost (at base rate ${base_labor_rate} per sq ft with markup {int((markup-1)*100)}%): ${labor_cost:.2f}\n"
            f"Total Project Cost: ${total_project_cost:.2f}\n"
            f"Final Cost Per Sq Ft: ${final_cost_per_sqft}\n\n"
            "Using the above pricing details from Surprise Granite, generate a comprehensive, professional, "
            "and detailed written estimate that includes a breakdown of material and labor costs, installation notes, "
            "and a personalized closing message addressing the customer by name. "
            "Ensure that the estimate is specific to Surprise Granite pricing and does not include generic information."
        )

        ai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert estimator at Surprise Granite. Provide a highly detailed and professional estimate strictly based on Surprise Granite pricing details."},
                {"role": "user", "content": prompt}
            ]
        )
        narrative = ai_response.choices[0].message.content

        return jsonify({
            "preliminary": {
                "material_cost": material_cost,
                "sink_cost": sink_cost,
                "cooktop_cost": cooktop_cost,
                "backsplash_cost": backsplash_cost,
                "labor_cost": labor_cost,
                "preliminary_total": preliminary_total,
                "slab_count": slab_count
            },
            "estimate": narrative
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/millwork-estimate", methods=["POST", "OPTIONS"])
def millwork_estimate():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    required_fields = ["roomLength", "roomWidth", "cabinetStyle", "woodType"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing {field}"}), 400

    try:
        room_length = float(data.get("roomLength"))
        room_width = float(data.get("roomWidth"))
        cabinet_style = data.get("cabinetStyle").strip().lower()
        wood_type = data.get("woodType").strip().lower()

        area = room_length * room_width
        base_cost = 50.0

        style_multiplier = 1.0
        if cabinet_style == "modern":
            style_multiplier = 1.2
        elif cabinet_style == "traditional":
            style_multiplier = 1.1

        wood_multiplier = 1.0
        if wood_type == "oak":
            wood_multiplier = 1.3
        elif wood_type == "maple":
            wood_multiplier = 1.2

        estimated_cost = area * base_cost * style_multiplier * wood_multiplier

        prompt = (
            f"Millwork Estimate Details:\n"
            f"Room dimensions: {room_length} ft x {room_width} ft (Area: {area} sq ft)\n"
            f"Cabinet Style: {cabinet_style.title()}\n"
            f"Wood Type: {wood_type.title()}\n"
            f"Base cost per sq ft: ${base_cost:.2f}\n"
            f"Style Multiplier: {style_multiplier}\n"
            f"Wood Multiplier: {wood_multiplier}\n"
            f"Calculated Estimated Cost: ${estimated_cost:.2f}\n\n"
            "Please provide a comprehensive, professional, and friendly written estimate for millwork services based on the above details."
        )

        ai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional millwork estimator."},
                {"role": "user", "content": prompt}
            ]
        )
        narrative = ai_response.choices[0].message.content

        return jsonify({
            "area": area,
            "estimatedCost": estimated_cost,
            "narrative": narrative
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
