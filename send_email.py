import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from python_files.app import logger


def send_email(subject, body, to_email):
    """Функция отправки письма."""
    from_email = "your_email@example.com"  # Ваш email
    from_password = "your_email_password"  # Ваш пароль

    try:
        # Устанавливаем соединение с SMTP сервером
        server = smtplib.SMTP("smtp.example.com", 587)
        server.starttls()  # Защищенное соединение
        server.login(from_email, from_password)

        # Создаем MIME сообщение
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Прикрепляем текстовое тело письма
        msg.attach(MIMEText(body, 'plain'))

        # Отправляем письмо
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        logger.info(f"Письмо отправлено на {to_email}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {e}")
        return False
