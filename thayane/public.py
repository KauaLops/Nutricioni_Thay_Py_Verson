from flask import Blueprint, abort, render_template

from .extensions import db
from .models import Contato, Post, RedeSocial, Servico, Trabalho

bp = Blueprint("public", __name__)


@bp.context_processor
def dados_do_site():
    """Contato e redes (cabeçalho/rodapé) em todas as páginas públicas."""
    try:
        contato = db.session.get(Contato, 1) or Contato(id=1)
        redes = RedeSocial.query.filter_by(ativo=True).order_by(RedeSocial.id).all()
    except Exception:
        db.session.rollback()
        contato, redes = Contato(id=1), []
    return {"contato": contato, "redes": redes}


@bp.get("/")
def index():
    return render_template(
        "index.html",
        servicos=Servico.query.filter_by(ativo=True).order_by(Servico.id).all(),
        posts=Post.query.filter_by(ativo=True).order_by(Post.data_publicacao.desc(), Post.id.desc()).all(),
        trabalhos=Trabalho.query.filter_by(ativo=True).order_by(Trabalho.data_criacao.desc()).all())


@bp.get("/blog/<int:post_id>")
def post(post_id):
    p = Post.query.filter_by(id=post_id, ativo=True).first()
    if not p:
        abort(404)
    return render_template("post.html", post=p)


@bp.get("/termos")
def termos():
    return render_template("legal.html", tipo="termos")


@bp.get("/privacidade")
def privacidade():
    return render_template("legal.html", tipo="privacidade")
