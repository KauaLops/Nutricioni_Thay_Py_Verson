import re
import smtplib
from email.message import EmailMessage

from flask import current_app


class EnvioEmailErro(Exception):
    pass


def _limpa(s):
    return re.sub(r"[\r\n]+", " ", str(s or "")).strip()


def enviar_agendamento(d):
    cfg = current_app.config
    if not cfg["MAIL_USERNAME"] or not cfg["MAIL_PASSWORD"]:
        raise EnvioEmailErro("SMTP não configurado (defina MAIL_USERNAME e MAIL_PASSWORD).")
    msg = EmailMessage()
    msg["From"] = cfg["MAIL_USERNAME"]
    msg["To"] = cfg["MAIL_DESTINO"]
    msg["Reply-To"] = _limpa(d["email"])
    msg["Subject"] = "Nova solicitação de agendamento - " + _limpa(d["nome"])
    obs = d["mensagem"] or "(sem observações)"
    msg.set_content(
        "Nova solicitação de agendamento pelo site\n\n"
        f"Nome: {_limpa(d['nome'])}\nE-mail: {_limpa(d['email'])}\nTelefone: {_limpa(d['telefone'])}\n"
        f"Tipo de atendimento: {_limpa(d['tipo'])}\nData desejada: {d['data'].strftime('%d/%m/%Y')}\n"
        f"Horário desejado: {d['horario']}\n\nMensagem:\n{obs}\n")
    try:
        if cfg["MAIL_PORT"] == 465:
            with smtplib.SMTP_SSL(cfg["MAIL_HOST"], 465, timeout=10) as s:
                s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"]); s.send_message(msg)
        else:
            with smtplib.SMTP(cfg["MAIL_HOST"], cfg["MAIL_PORT"], timeout=10) as s:
                s.starttls(); s.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"]); s.send_message(msg)
    except (smtplib.SMTPException, OSError) as e:
        raise EnvioEmailErro(str(e)) from e
