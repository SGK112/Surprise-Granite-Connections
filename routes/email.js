const express = require('express');
const router = express.Router();
const nodemailer = require('nodemailer');

// Create email transporter
const transporter = nodemailer.createTransport({
  host: process.env.EMAIL_HOST,
  port: process.env.EMAIL_PORT,
  secure: process.env.EMAIL_SECURE === 'true',
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// Format currency
function formatCurrency(amount) {
  if (typeof amount === 'string') {
    return amount; // Already formatted
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
}

// Email route
router.post('/send-email', async (req, res) => {
  try {
    const {
      to,
      subject,
      customerName,
      customerEmail,
      customerPhone,
      customerMessage,
      estimateDetails,
      websiteSource
    } = req.body;

    if (!customerName || !customerEmail || !estimateDetails) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Create HTML for company email
    const companyHtml = `
      <h2>New Countertop Estimate Request</h2>
      <h3>Customer Information:</h3>
      <p><strong>Name:</strong> ${customerName}</p>
      <p><strong>Email:</strong> ${customerEmail}</p>
      <p><strong>Phone:</strong> ${customerPhone || 'Not provided'}</p>
      <p><strong>Message:</strong> ${customerMessage || 'No additional message'}</p>
      <p><strong>Source:</strong> ${websiteSource || 'Website'}</p>
      
      <h3>Estimate Details:</h3>
      <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
        <tr>
          <th style="text-align: left; background-color: #f2f2f2;">Item</th>
          <th style="text-align: left; background-color: #f2f2f2;">Details</th>
        </tr>
        <tr>
          <td><strong>Material</strong></td>
          <td>${estimateDetails.material} (${estimateDetails.quality})</td>
        </tr>
        <tr>
          <td><strong>Square Feet</strong></td>
          <td>${estimateDetails.squareFeet}</td>
        </tr>
        <tr>
          <td><strong>Edge Treatment</strong></td>
          <td>${estimateDetails.edge}</td>
        </tr>
        <tr>
          <td><strong>Sink Cutouts</strong></td>
          <td>${estimateDetails.sinks}</td>
        </tr>
        <tr>
          <td><strong>Material Cost</strong></td>
          <td>${estimateDetails.materialCost}</td>
        </tr>
        <tr>
          <td><strong>Edge Cost</strong></td>
          <td>${estimateDetails.edgeCost}</td>
        </tr>
        <tr>
          <td><strong>Sink Cost</strong></td>
          <td>${estimateDetails.sinkCost}</td>
        </tr>
        <tr style="font-weight: bold; background-color: #f9f9f9;">
          <td><strong>Total Estimate</strong></td>
          <td>${estimateDetails.totalCost}</td>
        </tr>
      </table>
    `;

    // Create HTML for customer email
    const customerHtml = `
      <h2>Your Surprise Granite Countertop Estimate</h2>
      <p>Dear ${customerName},</p>
      <p>Thank you for your interest in Surprise Granite! We've received your estimate request and one of our specialists will contact you shortly to discuss your project in detail.</p>
      
      <h3>Your Estimate Details:</h3>
      <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
        <tr>
          <th style="text-align: left; background-color: #f2f2f2;">Item</th>
          <th style="text-align: left; background-color: #f2f2f2;">Details</th>
        </tr>
        <tr>
          <td><strong>Material</strong></td>
          <td>${estimateDetails.material} (${estimateDetails.quality})</td>
        </tr>
        <tr>
          <td><strong>Square Feet</strong></td>
          <td>${estimateDetails.squareFeet}</td>
        </tr>
        <tr>
          <td><strong>Edge Treatment</strong></td>
          <td>${estimateDetails.edge}</td>
        </tr>
        <tr>
          <td><strong>Sink Cutouts</strong></td>
          <td>${estimateDetails.sinks}</td>
        </tr>
        <tr style="font-weight: bold; background-color: #f9f9f9;">
          <td><strong>Total Estimate</strong></td>
          <td>${estimateDetails.totalCost}</td>
        </tr>
      </table>
      
      <p><em>Please note: This is a preliminary estimate based on the information provided. Your final quote may vary based on specific project requirements and material selection.</em></p>
      
      <p>If you have any questions or would like to schedule a consultation, please contact us at:</p>
      <p>Phone: (623) 214-3599<br>
      Email: info@surprisegranite.com</p>
      
      <p>Thank you for choosing Surprise Granite!</p>
      <p>The Surprise Granite Team</p>
    `;

    // Send email to company
    await transporter.sendMail({
      from: process.env.EMAIL_FROM || '"Surprise Granite Website" <info@surprisegranite.com>',
      to: to || 'info@surprisegranite.com',
      subject: subject || 'New Countertop Estimate Request',
      html: companyHtml
    });

    // Send confirmation email to customer
    await transporter.sendMail({
      from: process.env.EMAIL_FROM || '"Surprise Granite" <info@surprisegranite.com>',
      to: customerEmail,
      subject: 'Your Surprise Granite Countertop Estimate',
      html: customerHtml
    });

    res.status(200).json({ success: true, message: 'Emails sent successfully' });
  } catch (error) {
    console.error('Email error:', error);
    res.status(500).json({ error: 'Failed to send email', details: error.message });
  }
});

module.exports = router;
