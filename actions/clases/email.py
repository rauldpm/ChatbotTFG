from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
from decouple import Config, RepositoryEnv

# -----------------------------------------
DOTENV_FILE = 'secrets/email_secrets.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))
# -----------------------------------------

class Email():

    def __init__(self):
        self.port = int(env_config.get("EMAIL_SERVER_PORT"))
        self.server = env_config.get("EMAIL_SERVER_SMTP")
        self.sender = env_config.get("EMAIL_SENDER")
        self.password = env_config.get("EMAIL_APP_PASSWORD")

    def send_email(self, recipient, message, subject):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, "plain"))
        text = msg.as_string()
        SSLcontext = ssl.create_default_context()

        with smtplib.SMTP(self.server, self.port) as server:
            server.starttls(context=SSLcontext)
            server.login(self.sender, self.password)
            server.sendmail(self.sender, recipient, text)

    def send_email_code(self, recipient, code, name):

        message = "Hello " + name + "!\n\n"
        message += "Your reservation code is: " + code
        subject = "Restaurant reservation code"
        self.send_email(recipient, message, subject)


    def send_email_message(self, recipient, reserva_array, menu_array):

        message = "Hello " + reserva_array[4] + "!\n\n"
        message += "The details of your reservation are:\n\n"
        message += "- Day: " + reserva_array[0] + "\n"
        message += "- Hour: " + reserva_array[1] + "\n"
        message += "- Table: " + str(reserva_array[2]) + "\n"
        message += "- Name: " + reserva_array[4] + "\n"
        message += "- Diners: " + str(reserva_array[3]) + "\n\n"
        if len(menu_array) > 0:
          message += "Your menu is composed of:\n\n"
          if menu_array[0] is not None:
            message += "- Starter: " + menu_array[0] + "\n"
          if menu_array[1] is not None:
            message += "- Meat: " + menu_array[1] + "\n"
          if menu_array[2] is not None:
            message += "- Fish: " + menu_array[2] + "\n"
          if menu_array[3] is not None:
            message += "- Dessert: " + menu_array[3] + "\n"
          if menu_array[4] is not None:
            message += "- Drink: " + menu_array[4] + "\n"


        subject = "Restaurant reservation resume"
        self.send_email(recipient, message, subject)