import asyncio
from datetime import datetime

from app.db.mongodb import get_database
from app.db.redis import get_redis

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def send_real_email(to_email: str, subject: str, html_content: str):
    from app.core.config import settings
    sender_email = settings.smtp_user
    sender_password = settings.smtp_password
    smtp_host = settings.smtp_host
    smtp_port = settings.smtp_port
    
    if not sender_email or not sender_password:
        print(f"⚠️ [Email Warning] SMTP missing in .env (SMTP_USER/SMTP_PASSWORD). Skipping real email to {to_email}.")
        return False
        
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"ShopApp <{sender_email}>"
        msg["To"] = to_email
        
        part = MIMEText(html_content, "html")
        msg.attach(part)
        
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ [Email Error] Failed to send email to {to_email}: {e}")
        return False


async def audit_log_handler(channel: str, message: str):
    """Handle generic events for Audit Logging"""
    entity, action = channel.split(".")
    print(f"📝 [Audit] {action.capitalize()} {entity}: {message}")
    
    db = get_database()
    audit_doc = {
        "entity": entity,
        "action": action,
        "entity_id": message,
        "timestamp": datetime.utcnow()
    }
    
    try:
        await db["audit_logs"].insert_one(audit_doc)
    except Exception as e:
        print(f"Error saving audit log: {e}")


async def send_email_job(event_type: str, message: str):
    """Simulate background job for sending email"""
    if event_type == "order.created":
        print(f"📧 [Background Job] Sending Order Confirmation Email for Order ID: {message}...")
        await asyncio.sleep(1) # Simulate network delay
        print(f"✓ [Background Job] Order Confirmation Email Sent!")
    elif event_type == "user.otp_requested":
        import json
        try:
            data = json.loads(message)
            email = data.get("email")
            otp = data.get("otp")
            print(f"📧 [Background Job] Sending OTP '{otp}' to Email '{email}'...")
            
            # Use real email integration via smtplib
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px;">
                    <h2 style="color: #4CAF50;">Your Verification Code</h2>
                    <p>Use the following 6-digit code to verify your ShopApp account:</p>
                    <div style="font-size: 32px; font-weight: bold; letter-spacing: 5px; padding: 15px; margin: 20px 0; background: #f4f4f4; border-radius: 8px;">
                        {otp}
                    </div>
                    <p style="color: #888; font-size: 12px;">This code will expire in 5 minutes.</p>
                </body>
            </html>
            """
            # Skip real email for dummy test accounts to avoid SMTP bounce spam
            if "@example.com" in email:
                print(f"✓ [Background Job] Simulated OTP Email (Test Account) Processed (View Console for OTP: {otp})")
            else:
                # Run blocking SMTP in a thread
                success = await asyncio.to_thread(
                    send_real_email, email, "ShopApp - Account Verification OTP", html_content
                )
                if success:
                    print(f"✓ [Background Job] Real OTP Email Successfully Sent to {email}!")
                else:
                    print(f"✓ [Background Job] Real Email Failed, Check Logs.")
                
        except Exception as e:
            print(f"Error parsing OTP event: {e}")
    elif event_type == "user.created":
        print(f"📧 [Background Job] Sending Welcome Email to new User ID: {message}...")
        await asyncio.sleep(1)
        print(f"✓ [Background Job] Welcome Email Sent!")


async def handle_event(channel: str, data: str):
    """Route events to appropriate handlers"""
    # 1. Always write Audit Log for tracked actions
    if channel.endswith((".created", ".updated", ".deleted")):
        await audit_log_handler(channel, data)
        
    # 2. Trigger background jobs (e.g., Email)
    if channel in ["order.created", "user.created", "user.otp_requested"]:
        # Run asynchronously without blocking the event loop
        asyncio.create_task(send_email_job(channel, data))


async def subscribe_to_events():
    """Subscribe to Redis Pub/Sub events"""
    redis = get_redis()
    pubsub = redis.pubsub()

    # Subscribe using pattern to capture all create/update/delete events
    await pubsub.psubscribe("*.created", "*.updated", "*.deleted", "*.otp_requested")

    print("✓ Worker listening for events...")

    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            channel = message["channel"].decode()
            data = message["data"].decode()
            await handle_event(channel, data)
        elif message["type"] == "message":
            channel = message["channel"].decode()
            data = message["data"].decode()
            await handle_event(channel, data)


async def main():
    from app.db.mongodb import connect_to_mongo
    from app.db.redis import connect_to_redis

    await connect_to_mongo()
    await connect_to_redis()

    try:
        await subscribe_to_events()
    except KeyboardInterrupt:
        print("\n✗ Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
