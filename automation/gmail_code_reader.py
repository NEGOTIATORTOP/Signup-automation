import imapclient
import pyzmail36
import time
import re

def get_latest_verification_code(email, password, subject_match="schools", timeout=45):
    try:
        server = imapclient.IMAPClient('imap.gmail.com', ssl=True, timeout=15)
        server.login(email, password)
        server.select_folder('INBOX')
        since = time.time()
        code = None
        while time.time() - since < timeout:
            messages = server.search(['UNSEEN'])
            if not messages:
                time.sleep(2)
                continue
            latest_uid = messages[-1]
            raw_message = server.fetch([latest_uid], ['BODY[]'])
            message = pyzmail36.PyzMessage.factory(raw_message[latest_uid][b'BODY[]'])
            subject = message.get_subject()
            if subject_match.lower() in (subject or "").lower():
                body = ""
                if message.text_part:
                    body = message.text_part.get_payload().decode(message.text_part.charset)
                elif message.html_part:
                    body = message.html_part.get_payload().decode(message.html_part.charset)
                code_match = re.search(r"\b\d{6}\b", body)
                if code_match:
                    return code_match.group(0)
            time.sleep(2)
        server.logout()
    except Exception as e:
        print(f"IMAP error for {email}: {e}")
    return None
