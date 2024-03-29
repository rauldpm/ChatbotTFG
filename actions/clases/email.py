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

        message = "Hola " + name + "!\n\n"
        message += "Tu codigo de reserva es: " + code
        subject = "Restaurante - Codigo de reserva"
        self.send_email(recipient, message, subject)

    def send_email_message(self, recipient, reserva_array, menu_array, message):

        if message != "borrar":
            message = "Hola " + reserva_array[4] + "!\n\n"
            message += "Los detalles de tu reserva son:\n\n"
            message += "- Dia: " + reserva_array[0] + "\n"
            message += "- Hora: " + reserva_array[1] + "\n"
            message += "- Mesa: " + str(reserva_array[2]) + "\n"
            message += "- Nombre: " + reserva_array[4] + "\n"
            message += "- Comensales: " + str(reserva_array[3]) + "\n\n"
            if len(menu_array) > 0:
                message += "Tu menu esta compuesto por:\n\n"
                if menu_array[0] is not None:
                    message += "- " + menu_array[0] + "\n"
                if menu_array[1] is not None:
                    message += "- " + menu_array[1] + "\n"
                if menu_array[2] is not None:
                    message += "- " + menu_array[2] + "\n"
                if menu_array[3] is not None:
                    message += "- " + menu_array[3] + "\n"

            subject = "Restaurante - Resumen de reserva"
            self.send_email(recipient, message, subject)
        else:
            subject = "Restaurante - Eliminacion de reserva"
            message = "Tu reserva ha sido eliminada."
            self.send_email(recipient, message, subject)
