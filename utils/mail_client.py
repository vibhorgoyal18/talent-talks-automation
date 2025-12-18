from __future__ import annotations

import email
import imaplib
from dataclasses import dataclass
from email.header import decode_header
from typing import List, Optional


class MailClientError(RuntimeError):
    """Raised for errors when accessing email."""


@dataclass
class EmailMessage:
    """Represents an email message."""
    id: str
    subject: str
    sender: str
    date: str
    snippet: str
    body: Optional[str] = None


class GmailIMAPClient:
    """Gmail client using IMAP for reading emails.
    
    Requires an App Password (not regular password) for Gmail accounts with 2FA.
    Generate at: https://myaccount.google.com/apppasswords
    """

    IMAP_SERVER = "imap.gmail.com"
    IMAP_PORT = 993

    def __init__(self, email_address: str, app_password: str, timeout: int = 30) -> None:
        """Initialize Gmail IMAP client.
        
        Args:
            email_address: Gmail address (e.g., user@gmail.com)
            app_password: Gmail App Password (16 characters, no spaces)
            timeout: Connection timeout in seconds
        """
        if not email_address or not app_password:
            raise ValueError("Email address and app password must be provided")
        self.email_address = email_address
        self.app_password = app_password
        self.timeout = timeout
        self._connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """Connect and authenticate to Gmail IMAP server."""
        try:
            self._connection = imaplib.IMAP4_SSL(
                self.IMAP_SERVER, self.IMAP_PORT
            )
            self._connection.login(self.email_address, self.app_password)
        except imaplib.IMAP4.error as e:
            raise MailClientError(f"Failed to connect to Gmail: {e}")

    def disconnect(self) -> None:
        """Close the IMAP connection."""
        if self._connection:
            try:
                self._connection.logout()
            except Exception:
                pass
            self._connection = None

    def _decode_header_value(self, value: str) -> str:
        """Decode email header value."""
        if not value:
            return ""
        decoded_parts = decode_header(value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(charset or "utf-8", errors="replace"))
            else:
                result.append(part)
        return "".join(result)

    def _get_email_body(self, msg: email.message.Message) -> str:
        """Extract plain text or HTML body from email message."""
        body_text = ""
        body_html = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    decoded_payload = payload.decode(charset, errors="replace")
                    
                    if content_type == "text/plain":
                        body_text = decoded_payload
                    elif content_type == "text/html":
                        body_html = decoded_payload
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                decoded_payload = payload.decode(charset, errors="replace")
                content_type = msg.get_content_type()
                
                if content_type == "text/plain":
                    body_text = decoded_payload
                elif content_type == "text/html":
                    body_html = decoded_payload
        
        # Prefer plain text, but fall back to HTML if plain text is empty
        return body_text if body_text else body_html

    def list_messages(
        self, 
        folder: str = "INBOX", 
        max_results: int = 10,
        search_criteria: str = "ALL"
    ) -> List[EmailMessage]:
        """List messages from a folder.
        
        Args:
            folder: Mailbox folder (INBOX, SENT, etc.)
            max_results: Maximum number of messages to return
            search_criteria: IMAP search criteria (ALL, UNSEEN, FROM "email", SUBJECT "text", etc.)
        
        Returns:
            List of EmailMessage objects
        """
        if not self._connection:
            self.connect()
        
        try:
            self._connection.select(folder, readonly=True)
            _, message_numbers = self._connection.search(None, search_criteria)
            
            email_ids = message_numbers[0].split()
            # Get the latest emails (reverse order)
            email_ids = email_ids[-max_results:][::-1]
            
            messages = []
            for email_id in email_ids:
                _, msg_data = self._connection.fetch(email_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject = self._decode_header_value(msg.get("Subject", ""))
                        sender = self._decode_header_value(msg.get("From", ""))
                        date = msg.get("Date", "")
                        body = self._get_email_body(msg)
                        snippet = body[:200] + "..." if len(body) > 200 else body
                        
                        messages.append(EmailMessage(
                            id=email_id.decode(),
                            subject=subject,
                            sender=sender,
                            date=date,
                            snippet=snippet.strip(),
                            body=body
                        ))
            
            return messages
            
        except imaplib.IMAP4.error as e:
            raise MailClientError(f"Failed to fetch messages: {e}")

    def get_message(self, message_id: str, folder: str = "INBOX") -> Optional[EmailMessage]:
        """Get a specific message by ID."""
        if not self._connection:
            self.connect()
        
        try:
            self._connection.select(folder, readonly=True)
            _, msg_data = self._connection.fetch(message_id.encode(), "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject = self._decode_header_value(msg.get("Subject", ""))
                    sender = self._decode_header_value(msg.get("From", ""))
                    date = msg.get("Date", "")
                    body = self._get_email_body(msg)
                    snippet = body[:200] + "..." if len(body) > 200 else body
                    
                    return EmailMessage(
                        id=message_id,
                        subject=subject,
                        sender=sender,
                        date=date,
                        snippet=snippet.strip(),
                        body=body
                    )
            return None
            
        except imaplib.IMAP4.error as e:
            raise MailClientError(f"Failed to get message: {e}")

    def search_messages(
        self, 
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        unseen_only: bool = False,
        max_results: int = 10
    ) -> List[EmailMessage]:
        """Search for messages with specific criteria.
        
        Args:
            subject: Search for emails with this subject
            sender: Search for emails from this sender
            unseen_only: Only return unread emails
            max_results: Maximum number of results
        
        Returns:
            List of matching EmailMessage objects
        """
        criteria_parts = []
        
        if unseen_only:
            criteria_parts.append("UNSEEN")
        if subject:
            criteria_parts.append(f'SUBJECT "{subject}"')
        if sender:
            criteria_parts.append(f'FROM "{sender}"')
        
        search_criteria = " ".join(criteria_parts) if criteria_parts else "ALL"
        
        return self.list_messages(
            folder="INBOX",
            max_results=max_results,
            search_criteria=search_criteria
        )

    def wait_for_email(
        self,
        subject_contains: str,
        timeout_seconds: int = 60,
        poll_interval: int = 5
    ) -> Optional[EmailMessage]:
        """Wait for an email with a specific subject to arrive.
        
        Args:
            subject_contains: Text that should be in the subject
            timeout_seconds: Maximum time to wait
            poll_interval: Seconds between checks
        
        Returns:
            EmailMessage if found, None if timeout
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            messages = self.search_messages(subject=subject_contains, max_results=5)
            for msg in messages:
                if subject_contains.lower() in msg.subject.lower():
                    return msg
            time.sleep(poll_interval)
        
        return None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
