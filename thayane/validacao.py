"""Validação de dados (usada pelo formulário público e pelo painel)."""
import re
from datetime import date
from decimal import Decimal, InvalidOperation

EMAIL_RE = r"[^\s@]+@[^\s@]+\.[^\s@]+"
TEL_RE = r"[0-9()+\-\s]{8,20}"
URL_RE = r"https?://\S+"
IMG_RE = r"(/|https?://)\S*"


class Validador:
    def __init__(self, origem):
        self.origem = origem
        self.valores = {}
        self.erros = {}

    def txt(self, campo, obrigatorio=True, max=255, regex=None, msg_regex="Valor inválido.",
            msg_obrig="Campo obrigatório.", padrao=""):
        v = str(self.origem.get(campo) or "").strip()
        self.valores[campo] = v
        if not v:
            if obrigatorio:
                self.erros[campo] = msg_obrig
            else:
                self.valores[campo] = padrao
        elif len(v) > max:
            self.erros[campo] = f"Máximo de {max} caracteres."
        elif regex and not re.fullmatch(regex, v):
            self.erros[campo] = msg_regex
        return v

    def checkbox(self, campo):
        self.valores[campo] = str(self.origem.get(campo) or "").lower() in ("on", "true", "1")

    def preco(self, campo):
        bruto = str(self.origem.get(campo) or "").strip().replace(",", ".")
        self.valores[campo] = bruto
        try:
            d = Decimal(bruto).quantize(Decimal("0.01"))
            if d < 0 or d >= Decimal("100000000"):
                raise InvalidOperation
            self.valores[campo] = d
        except (InvalidOperation, ValueError):
            self.erros[campo] = "Informe um preço válido (ex.: 180,00)."

    def data(self, campo, futura=False, hoje=None):
        bruto = str(self.origem.get(campo) or "").strip()
        self.valores[campo] = bruto
        try:
            d = date.fromisoformat(bruto)
        except ValueError:
            self.erros[campo] = "Informe uma data válida."
            return
        if futura and d < (hoje or date.today()):
            self.erros[campo] = "A data deve ser hoje ou futura."
        else:
            self.valores[campo] = d

    @property
    def ok(self):
        return not self.erros
