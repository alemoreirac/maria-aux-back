import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class EmailManager:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_from_name = os.getenv("SMTP_FROM_NAME")
        self.smtp_from_email = self.smtp_username  # mesmo e-mail de login
  
    def send_verification_email(self, to_email: str, link:str):


        subject = "Confirmação de E-mail"
        body = f"""
        Olá,

        Clique no link abaixo para verificar seu e-mail:

        {link}

        Caso não tenha solicitado isso, ignore este e-mail.
        """

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
        msg["To"] = to_email

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)

        print(f"E-mail de verificação enviado para {to_email}")
 
