from email import message_from_bytes
from email.header import decode_header
import logging
from typing import Dict, Any

logger = logging.getLogger("EmailParser")


def parse_email(raw_email: bytes) -> Dict[str, Any]:
    try:
        msg = message_from_bytes(raw_email)

        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else 'utf-8')

        sender, encoding = decode_header(msg["From"])[0]
        if isinstance(sender, bytes):
            sender = sender.decode(encoding if encoding else 'utf-8')

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        return {
            "subject": subject,
            "sender": sender,
            "body": body,
            "headers": dict(msg.items())
        }
    except Exception as e:
        logger.error(f"Failed to parse email: {str(e)}")
        raise