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
