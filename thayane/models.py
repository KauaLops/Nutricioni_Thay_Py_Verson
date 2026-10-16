import re
from datetime import date, datetime

from flask_login import UserMixin

from .extensions import db


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)  # hash, nunca texto puro
    role = db.Column(db.String(30), nullable=False, default="ADMIN")
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def is_active(self):
        return self.ativo


class Trabalho(db.Model):
    __tablename__ = "trabalho"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    descricao = db.Column(db.String(1000))
    categoria = db.Column(db.String(60))
    imagem_url = db.Column(db.String(500))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, nullable=False, default=True)


class Servico(db.Model):
    __tablename__ = "servico"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(500))
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    beneficios = db.Column(db.String(1000))  # um por linha
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def lista_beneficios(self):
        return [b.strip() for b in (self.beneficios or "").splitlines() if b.strip()]


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(160), nullable=False)
    resumo = db.Column(db.String(500))
    conteudo = db.Column(db.Text)
    imagem_url = db.Column(db.String(500))
    categoria = db.Column(db.String(60))
    data_publicacao = db.Column(db.Date, default=date.today)
    ativo = db.Column(db.Boolean, nullable=False, default=True)


class Contato(db.Model):
    """Registro único (id = 1)."""
    __tablename__ = "contato"
    id = db.Column(db.Integer, primary_key=True, default=1)
    email = db.Column(db.String(160))
    telefone = db.Column(db.String(40))
    instagram = db.Column(db.String(80))
    whatsapp = db.Column(db.String(40))
    crn = db.Column(db.String(20))

    @property
    def whatsapp_digitos(self):
        return re.sub(r"\D", "", self.whatsapp or "")

    @property
    def whatsapp_link(self):
        return f"https://wa.me/{self.whatsapp_digitos}?text=Ol%C3%A1%2C%20gostaria%20de%20agendar%20uma%20consulta."

    @property
    def instagram_usuario(self):
        return (self.instagram or "").strip().lstrip("@")

    @property
    def instagram_link(self):
        return f"https://instagram.com/{self.instagram_usuario}"


class RedeSocial(db.Model):
    __tablename__ = "rede_social"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), nullable=False)
    url = db.Column(db.String(300), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
