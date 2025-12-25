import smtplib
import socket
import ssl
from django.core.mail.backends.smtp import EmailBackend

class RenderGmailBackend(EmailBackend):
    """
    Custom Email Backend for Render + Gmail.
    Forces IPv4 and explicit SSL connection to bypass Errno 101/110.
    """
    def open(self):
        if self.connection:
            return False

        # 1. Force IPv4 (Crucial for Render)
        # We patch getaddrinfo ONLY during this specific email connection attempt
        original_getaddrinfo = socket.getaddrinfo
        
        def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
        
        socket.getaddrinfo = ipv4_getaddrinfo

        try:
            # 2. Use SMTP_SSL directly (Port 465)
            # This is more robust than starting plain and upgrading to TLS
            self.connection = smtplib.SMTP_SSL(
                self.host, 
                self.port, 
                timeout=30  # Explicit 30s timeout
            )
            
            # 3. Login
            if self.username and self.password:
                self.connection.login(self.username, self.password)
                
            return True
            
        except OSError as e:
            if not self.fail_silently:
                # Re-raise the error so we can see it in logs
                raise e
        finally:
            # 4. Cleanup: Restore original socket behavior
            socket.getaddrinfo = original_getaddrinfo