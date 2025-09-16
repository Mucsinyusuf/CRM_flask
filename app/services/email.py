from flask import current_app, copy_current_app_context
from ..extensions import mail
from flask_mail import Message
import threading


def send_email(to, subject, body):
    if not to:
        print("⚠️ No email recipient configured")
        return False

    msg = Message(subject=subject, recipients=[to], body=body)

    def _send_sync(msg):
        try:
            mail.send(msg)
            print(f"✅ Email sent to {to}")
        except Exception as e:
            print(f"❌ Mail send error to {to}: {e}")

    @copy_current_app_context
    def _send_async(msg):
        try:
            mail.send(msg)
            print(f"✅ (async) Email sent to {to}")
        except Exception as e:
            print(f"❌ (async) Mail send error to {to}: {e}")

    # Check config flag
    use_async = current_app.config.get("MAIL_ASYNC", False)

    if use_async:
        thr = threading.Thread(target=_send_async, args=(msg,))
        thr.start()
    else:
        _send_sync(msg)

    return True
