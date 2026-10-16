from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, current_app, jsonify, request

from .mailer import EnvioEmailErro, enviar_agendamento
from .validacao import EMAIL_RE, TEL_RE, Validador

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.post("/agendamento")
def agendamento():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(message="Dados inválidos. Revise o formulário."), 400
    v = Validador(dados)
    v.txt("nome", max=120, msg_obrig="Informe seu nome completo.")
    v.txt("email", max=160, regex=EMAIL_RE, msg_regex="E-mail inválido.", msg_obrig="Informe seu e-mail.")
    v.txt("telefone", max=20, regex=TEL_RE, msg_regex="Telefone inválido.", msg_obrig="Informe seu telefone.")
    v.data("data", futura=True, hoje=datetime.now(ZoneInfo("America/Recife")).date())
    v.txt("horario", regex=r"([01]\d|2[0-3]):[0-5]\d", msg_regex="Horário inválido.", msg_obrig="Informe o horário.")
    v.txt("tipo", max=120, msg_obrig="Informe o tipo de atendimento.")
    v.txt("mensagem", obrigatorio=False, max=1000)
    if not v.ok:
        return jsonify(message="Revise os campos destacados.", erros=v.erros), 400
    try:
        enviar_agendamento(v.valores)
    except EnvioEmailErro:
        current_app.logger.exception("Falha ao enviar e-mail de agendamento")
        return jsonify(message="Não foi possível enviar sua solicitação agora. Tente novamente em instantes ou fale pelo WhatsApp."), 503
    return jsonify(message="Sua solicitação foi enviada com sucesso. Entraremos em contato para confirmar o atendimento.")
