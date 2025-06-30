import requests
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.translation import gettext as _


def send_gift_card_email(emails, card, reason):
    subject = _("Gift Card from Firehouse Movers")

    # Get the company name and amount (quantity)
    company_name = card.company.name
    amount = card.amount

    # Text content (fallback in case HTML is not supported)
    text_content = _(
        f"Thank you for being part of Firehouse Movers! We appreciate your hard work.\n"
        f"You have received a gift card of: {company_name} with quantity {amount}\n"
        f"Reason: {reason}\n"
        "Best regards,\n"
        "The Firehouse Movers Team"
    )

    # HTML content with the logo URL - keeping original text, updating only styling
    html_content = _(
        """
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap');
                
                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                }}
                
                table {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    border: none;
                    background-color: #ffffff;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
                }}
                
                td {{
                    padding: 20px;
                }}
                
                .header {{
                    background-color: #1a1a1a;
                    text-align: center;
                    padding: 25px 20px;
                    border-bottom: 3px solid #e74c3c;
                }}
                
                .header img {{
                    max-width: 120px;
                    max-height: 120px;
                    margin-bottom: 10px;
                }}
                
                .header h2 {{
                    color: #ffffff;
                    font-size: 24px;
                    margin-top: 10px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }}
                
                .content {{
                    padding: 30px 25px;
                    text-align: center;
                    background-color: #ffffff;
                }}
                
                .content p {{
                    font-size: 16px;
                    color: #333333;
                    line-height: 1.6;
                }}
                
                .content .amount {{
                    font-size: 18px;
                    color: #e74c3c;
                    font-weight: 600;
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-left: 4px solid #e74c3c;
                    text-align: left;
                    margin: 20px 0;
                }}
                
                .content strong {{
                    color: #1a1a1a;
                }}
                
                .footer {{
                    background-color: #1a1a1a;
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid #e74c3c;
                }}
                
                .footer p {{
                    color: #ffffff;
                    font-size: 14px;
                    margin: 5px 0;
                }}
                
                .footer br {{
                    display: block;
                    content: "";
                    margin-top: 8px;
                }}
            </style>
        </head>
        <body>
            <table>
                <tr class="header">
                    <td>
                        <!-- Logo Section -->
                        <h2>You've Received a Gift Card from Firehouse Movers!</h2>
                    </td>
                </tr>
                <tr class="content">
                    <td>
                        <p>Thank you for your hard work at Firehouse Movers! We are excited to offer you a gift card as a token of appreciation.</p>
                        <p class="amount">You have received a gift card of: <strong>{company_name}</strong> with quantity <strong>{amount}</strong></p>
                        <p>Reason: <strong>{reason}</strong></p>
                    </td>
                </tr>
                <tr class="footer">
                    <td>
                        <p>Thank you again for being a valued part of our team!</p>
                        <p>Best regards,<br>The Firehouse Movers Team</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    ).format(company_name=company_name, amount=amount, reason=reason)

    # Sending the email to multiple recipients at once
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)



def send_issue_uniform_email(email, employee, uniform):
    subject = _("Uniform Issue Notification")

    text_content = _(
        f"Hi {employee},\n\n"
        f"You have been assigned the uniform item:  {uniform}.\n"
        "Best regards,\n"
        "The Firehouse Movers Team"
    )

    html_content = _(
        """
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap');

                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
                    background-color: #f8f8f8;
                    padding: 0;
                    margin: 0;
                }}

                table {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-collapse: collapse;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                }}

                .header {{
                    background-color: #1a1a1a;
                    padding: 20px;
                    text-align: center;
                    color: #ffffff;
                    border-bottom: 3px solid #e74c3c;
                }}

                .content {{
                    padding: 30px;
                    color: #333333;
                    font-size: 16px;
                    line-height: 1.6;
                }}

                .content strong {{
                    color: #e74c3c;
                }}

                .footer {{
                    background-color: #1a1a1a;
                    color: #ffffff;
                    text-align: center;
                    padding: 15px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <table>
                <tr class="header">
                    <td>
                        <h2>Uniform Issue Notification</h2>
                    </td>
                </tr>
                <tr class="content">
                    <td>
                        <p>Hi <strong>{employee}</strong>,</p>
                        <p>You have been assigned the uniform item: <strong>{uniform}</strong>.</p>
                    </td>
                </tr>
                <tr class="footer">
                    <td>
                        <p>Best regards,<br>The Firehouse Movers Team</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    ).format(employee=employee, uniform=uniform)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)




def send_return_uniform_email(email, employee, uniform):
    subject = _("Uniform Return Notification")

    text_content = _(
        f"Hi {employee},\n\n"
        f"You have returned the uniform item:  {uniform}.\n"
        "Best regards,\n"
        "The Firehouse Movers Team"
    )

    html_content = _(
        """
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap');

                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
                    background-color: #f8f8f8;
                    padding: 0;
                    margin: 0;
                }}

                table {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    border-collapse: collapse;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                }}

                .header {{
                    background-color: #1a1a1a;
                    padding: 20px;
                    text-align: center;
                    color: #ffffff;
                    border-bottom: 3px solid #e74c3c;
                }}

                .content {{
                    padding: 30px;
                    color: #333333;
                    font-size: 16px;
                    line-height: 1.6;
                }}

                .content strong {{
                    color: #e74c3c;
                }}

                .footer {{
                    background-color: #1a1a1a;
                    color: #ffffff;
                    text-align: center;
                    padding: 15px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <table>
                <tr class="header">
                    <td>
                        <h2>Uniform Return Notification</h2>
                    </td>
                </tr>
                <tr class="content">
                    <td>
                        <p>Hi <strong>{employee}</strong>,</p>
                        <p>You have returned the uniform item: <strong>{uniform}</strong>.</p>
                    </td>
                </tr>
                <tr class="footer">
                    <td>
                        <p>Best regards,<br>The Firehouse Movers Team</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    ).format(employee=employee, uniform=uniform)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_order_email(email, transaction, confirm_url, reject_url):
    subject = _("New Material Order Request")

    # Text content (fallback in case HTML is not supported)
    text_content = _(
        f"New material order has been placed.\n"
        f"Job ID: {transaction.job_id}\n"
        f"Order Date: {transaction.date.strftime('%B %d, %Y')}\n"
        f"Requested By: {transaction.employee.user.username}\n\n"
        f"Please click the following links to confirm or reject the order:\n"
        f"Confirm: {confirm_url}\n"
        f"Reject: {reject_url}\n\n"
        "Best regards,\n"
        "The Firehouse Movers Team"
    )

    # HTML content
    html_content = _(
        """
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Montserrat', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                }}
                
                table {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    border: none;
                    background-color: #ffffff;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
                }}
                
                td {{
                    padding: 20px;
                }}
                
                .header {{
                    background-color: #1a1a1a;
                    text-align: center;
                    padding: 25px 20px;
                    border-bottom: 3px solid #e74c3c;
                }}
                
                .header h2 {{
                    color: #ffffff;
                    font-size: 24px;
                    margin-top: 10px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }}
                
                .content {{
                    padding: 30px 25px;
                    text-align: left;
                    background-color: #ffffff;
                }}
                
                .content p {{
                    font-size: 16px;
                    color: #333333;
                    line-height: 1.6;
                }}
                
                .details {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-left: 4px solid #e74c3c;
                    margin: 20px 0;
                }}
                
                .details h3 {{
                    color: #1a1a1a;
                    margin-top: 0;
                }}
                
                .details ul {{
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }}
                
                .details li {{
                    margin: 5px 0;
                }}
                
                .button-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                
                .button {{
                    display: inline-block;
                    padding: 12px 25px;
                    margin: 0 10px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 600;
                    color: #ffffff !important;
                }}
                
                .confirm {{
                    background-color: #28a745;
                }}
                
                .reject {{
                    background-color: #dc3545;
                }}
                
                .footer {{
                    background-color: #1a1a1a;
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid #e74c3c;
                }}
                
                .footer p {{
                    color: #ffffff;
                    font-size: 14px;
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            <table>
                <tr class="header">
                    <td>
                        <h2>New Material Order Request</h2>
                    </td>
                </tr>
                <tr class="content">
                    <td>
                        <p>Dear Supplier,</p>
                        
                        <p>A new material order has been placed. Please review the details below:</p>
                        
                        <div class="details">
                            <p><strong>Job ID:</strong> {job_id}</p>
                            <p><strong>Order Date:</strong> {order_date}</p>
                            <p><strong>Requested By:</strong> {requested_by}</p>
                            
                            <h3>Order Details:</h3>
                            <ul>
                                {material_details}
                            </ul>
                        </div>
                        
                        <p>Please click one of the buttons below to confirm or reject this order:</p>
                        
                        <div class="button-container">
                            <a href="{confirm_url}" class="button confirm">Confirm Order</a>
                            <a href="{reject_url}" class="button reject">Reject Order</a>
                        </div>
                        
                        <p style="font-size: 0.9em; color: #666;">
                            Note: Clicking these buttons will automatically update the order status in our system.
                        </p>
                    </td>
                </tr>
                <tr class="footer">
                    <td>
                        <p>Best regards,<br>The Firehouse Movers Team</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    ).format(
        job_id=transaction.job_id,
        order_date=transaction.date.strftime('%B %d, %Y'),
        requested_by=transaction.employee.user.username,
        material_details='\n'.join([
            f'<li>{field.replace("_", " ").title()}: {getattr(transaction, field)}</li>'
            for field in [
                'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
                'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
                'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
                'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
                'packing_peanuts', 'ram_board', 'mattress_bags',
                'mirror_cartons', 'bubble_wrap', 'gondola_boxes'
            ]
            if getattr(transaction, field, 0) > 0
        ]),
        confirm_url=confirm_url,
        reject_url=reject_url
    )

    # Send the email
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)


def send_order_status_update_email(email, order, status):
    subject = _("Order Status Update")

    # Text content (fallback in case HTML is not supported)
    text_content = _(
        f"Your material order has been {status}.\n"
        f"Job ID: {order.job_id}\n"
        f"Order Date: {order.date.strftime('%B %d, %Y')}\n"
        f"Status: {status.title()}\n\n"
        "Best regards,\n"
        "The Firehouse Movers Team"
    )

    # HTML content
    html_content = _(
        """
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap');
                
                body {
                    font-family: 'Montserrat', Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f0f0f0;
                }
                
                table {
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    border: none;
                    background-color: #ffffff;
                    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
                }
                
                td {
                    padding: 20px;
                }
                
                .header {
                    background-color: #1a1a1a;
                    text-align: center;
                    padding: 25px 20px;
                    border-bottom: 3px solid #e74c3c;
                }
                
                .header h2 {
                    color: #ffffff;
                    font-size: 24px;
                    margin-top: 10px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }
                
                .content {
                    padding: 30px 25px;
                    text-align: left;
                    background-color: #ffffff;
                }
                
                .content p {
                    font-size: 16px;
                    color: #333333;
                    line-height: 1.6;
                }
                
                .status {
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-left: 4px solid {status_color};
                    margin: 20px 0;
                }
                
                .status h3 {
                    color: #1a1a1a;
                    margin-top: 0;
                }
                
                .details {
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-left: 4px solid #e74c3c;
                    margin: 20px 0;
                }
                
                .details h3 {
                    color: #1a1a1a;
                    margin-top: 0;
                }
                
                .details ul {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                
                .details li {
                    margin: 5px 0;
                }
                
                .footer {
                    background-color: #1a1a1a;
                    padding: 20px;
                    text-align: center;
                    border-top: 1px solid #e74c3c;
                }
                
                .footer p {
                    color: #ffffff;
                    font-size: 14px;
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <table>
                <tr class="header">
                    <td>
                        <h2>Order Status Update</h2>
                    </td>
                </tr>
                <tr class="content">
                    <td>
                        <p>Dear {employee_name},</p>
                        
                        <div class="status">
                            <h3>Your order has been <strong>{status}</strong></h3>
                        </div>
                        
                        <p>Order Details:</p>
                        
                        <div class="details">
                            <p><strong>Job ID:</strong> {job_id}</p>
                            <p><strong>Order Date:</strong> {order_date}</p>
                            
                            <h3>Ordered Materials:</h3>
                            <ul>
                                {material_details}
                            </ul>
                        </div>
                    </td>
                </tr>
                <tr class="footer">
                    <td>
                        <p>Best regards,<br>The Firehouse Movers Team</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
    ).format(
        status_color='#28a745' if status == 'confirmed' else '#dc3545',
        employee_name=order.employee.user.username,
        status=status.title(),
        job_id=order.job_id,
        order_date=order.date.strftime('%B %d, %Y'),
        material_details='\n'.join([
            f'<li>{field.replace("_", " ").title()}: {getattr(order, field)}</li>'
            for field in [
                'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
                'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
                'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
                'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
                'packing_peanuts', 'ram_board', 'mattress_bags',
                'mirror_cartons', 'bubble_wrap', 'gondola_boxes'
            ]
            if getattr(order, field, 0) > 0
        ])
    )

    # Send the email
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
