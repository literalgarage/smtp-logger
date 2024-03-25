import smtplib
import subprocess
import threading
import time
from email.message import EmailMessage


def _send_email(host: str = "localhost", port: int = 8025) -> bool:
    """Send a test email using the localhost SMTP server on port 8025."""
    msg = EmailMessage()
    msg["Subject"] = "Test Email"
    msg["From"] = "sender@example.com"
    msg["To"] = "receiver@example.com"
    msg.set_content("""\
This is a test email. It has some text in it.
                    
Some of the text lines are actually quite long, and we expect that \
the email will be formatted correctly when it is received. Namely \
that continuation lines will be correctly buffered and displayed.

Sincerely,
Test Code
""")

    # Send the email via localhost SMTP server on port 8025
    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.send_message(msg)
    except Exception as e:
        print("Failed to send email:", {e})
        return False
    return True


def test_can_send_email():
    """Test that we can send an email using the SMTP logger."""
    # Run the smtp logger in a subprocess and capture its output
    host = "localhost"
    port = 8025

    try:
        # Start the SMTP logger in a subprocess
        proc = subprocess.Popen(
            [
                "python",
                "-m",
                "smtp_logger",
                "--verbose",
                "--host",
                host,
                "--port",
                str(port),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for the server to start
        time.sleep(1)

        # Send an email, making sure to timeout after 5 seconds (aka run in thread)
        thread = threading.Thread(target=_send_email, args=(host, port))
        thread.start()
        thread.join(timeout=1)

        # Look for the text 'This is a test email' in the stdout
        try:
            stdout, _ = proc.communicate(timeout=1)
        except subprocess.TimeoutExpired as te:
            stdout = te.stdout
            assert stdout is not None

        assert (
            b"This is a test email" in stdout
        ), "Email not received by the SMTP logger."
        assert (
            b"disconnected from" in stdout
        ), "SMTP logger did not disconnect from client."
    finally:
        proc.kill()
        proc.wait()
