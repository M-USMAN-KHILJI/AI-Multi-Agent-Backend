import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_otp_email(to_email: str, otp_code: str) -> bool:
    """
    Sends a beautifully designed HTML OTP verification email via Gmail SMTP.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise ValueError("SMTP credentials not configured on server.")

    subject = f"{otp_code} is your OmniAgent verification code"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>OmniAgent Verification Code</title>
    </head>
    <body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #f1f5f9;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0b0f19; padding: 40px 20px;">
        <tr>
          <td align="center">
            <table role="presentation" width="100%" style="max-width: 520px; background: #131926; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 36px 32px; box-shadow: 0 20px 40px rgba(0,0,0,0.6);">
              <!-- Logo / Title Header -->
              <tr>
                <td align="center" style="padding-bottom: 24px;">
                  <div style="display: inline-block; padding: 12px 24px; border-radius: 12px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3);">
                    <span style="font-size: 20px; font-weight: 700; color: #818cf8; letter-spacing: -0.5px;">⚡ OmniAgent AI</span>
                  </div>
                </td>
              </tr>
              <!-- Headline -->
              <tr>
                <td align="center" style="padding-bottom: 12px;">
                  <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: #ffffff;">Password Reset Request</h1>
                </td>
              </tr>
              <!-- Body -->
              <tr>
                <td align="center" style="padding-bottom: 28px;">
                  <p style="margin: 0; font-size: 14px; color: #94a3b8; line-height: 1.6;">
                    We received a request to reset your password. Use the verification code below to verify your identity. This code is valid for 10 minutes.
                  </p>
                </td>
              </tr>
              <!-- OTP Box -->
              <tr>
                <td align="center" style="padding-bottom: 28px;">
                  <div style="background: rgba(11, 15, 25, 0.85); border: 2px dashed #6366f1; border-radius: 12px; padding: 18px 32px; display: inline-block;">
                    <span style="font-size: 32px; font-weight: 800; letter-spacing: 10px; color: #a5b4fc; font-family: monospace;">{otp_code}</span>
                  </div>
                </td>
              </tr>
              <!-- Expiry Note -->
              <tr>
                <td align="center" style="padding-bottom: 32px;">
                  <p style="margin: 0; font-size: 12px; color: #64748b;">
                    If you did not request a password reset, you can safely ignore this email. Your password will remain unchanged.
                  </p>
                </td>
              </tr>
              <!-- Divider -->
              <tr>
                <td style="border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 20px;" align="center">
                  <p style="margin: 0; font-size: 11px; color: #475569;">
                    © 2026 OmniAgent AI Platform • Multimodal Multi-Agent Intelligence
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email

    # Plain text fallback
    text_content = f"Your OmniAgent password reset code is: {otp_code}. Valid for 10 minutes."
    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    password = settings.SMTP_PASSWORD.replace(" ", "")
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, password)
        server.send_message(msg)

    return True

