from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import func
from werkzeug.security import check_password_hash

from .extensions import db
from .models import Contato, Post, RedeSocial, Servico, Trabalho, Usuario
from .seed import hash_senha
from .validacao import EMAIL_RE, IMG_RE, URL_RE, Validador

bp = Blueprint("admin", __name__, url_prefix="/admin")
_dummy = None


@bp.before_request
def proteger():
    """Tudo em /admin/** exige administrador autenticado (exceto o login)."""
    if request.endpoint == "admin.login":
        return None
    if not current_user.is_authenticated or current_user.role != "ADMIN":
        return redirect(url_for("admin.login"))
    return None


# ---------------- Login / logout ----------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    global _dummy
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        u = Usuario.query.filter(func.lower(Usuario.email) == email).first() if email else None
        if u is None:  # gasta o mesmo tempo para não revelar se o e-mail existe
            _dummy = _dummy or hash_senha("dummy-password")
            check_password_hash(_dummy, senha)
        if u and u.ativo and check_password_hash(u.senha, senha):
            session.clear()
            session.permanent = True
            login_user(u)
            return redirect(url_for("admin.dashboard"))
        flash("E-mail ou senha incorretos.", "erro")
        return redirect(url_for("admin.login"))
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/login.html")


@bp.post("/logout")
def logout():
    logout_user()
    session.clear()
    flash("Você saiu com segurança.", "ok")
    return redirect(url_for("admin.login"))


@bp.get("/")
def dashboard():
    return render_template("admin/dashboard.html", pagina="dashboard",
                           qt_servicos=Servico.query.count(), qt_posts=Post.query.count(), qt_trabalhos=Trabalho.query.count())


# ---------------- Parsers (validação) ----------------
def parse_servico(f):
    v = Validador(f)
    v.txt("nome", max=120, msg_obrig="Informe o nome do serviço.")
    v.txt("descricao", max=500, msg_obrig="Informe a descrição.")
    v.preco("preco")
    v.txt("beneficios", obrigatorio=False, max=1000)
    v.checkbox("ativo")
    return v


def parse_post(f):
    v = Validador(f)
    v.txt("titulo", max=160, msg_obrig="Informe o título.")
    v.txt("categoria", max=60, msg_obrig="Informe a categoria.")
    v.data("data_publicacao")
    v.txt("imagem_url", obrigatorio=False, max=500, regex=IMG_RE, msg_regex="Use um caminho (/images/...) ou um link https://",
          padrao="/images/blog-1.svg")
    v.txt("resumo", max=500, msg_obrig="Informe o resumo.")
    v.txt("conteudo", max=20000, msg_obrig="Informe o texto.")
    v.checkbox("ativo")
    return v


def parse_trabalho(f):
    v = Validador(f)
    v.txt("titulo", max=160, msg_obrig="Informe o título.")
    v.txt("categoria", max=60, msg_obrig="Informe a categoria.")
    v.txt("imagem_url", obrigatorio=False, max=500, regex=IMG_RE, msg_regex="Use um caminho (/images/...) ou um link https://",
          padrao="/images/hero.jpg")
    v.txt("descricao", obrigatorio=False, max=1000)
    v.checkbox("ativo")
    return v


def parse_rede(f):
    v = Validador(f)
    v.txt("nome", max=60, msg_obrig="Informe o nome da rede.")
    v.txt("url", max=300, regex=URL_RE, msg_regex="O link deve começar com http:// ou https://", msg_obrig="Informe o link.")
    v.checkbox("ativo")
    return v


# ---------------- CRUD genérico ----------------
def _para_form(obj):
    out = {}
    for c in obj.__table__.columns:
        val = getattr(obj, c.name)
        out[c.name] = val.isoformat() if isinstance(val, date) and not hasattr(val, "hour") else ("" if val is None else val)
    return out


def registrar_crud(slug, Modelo, template, parse, vazio, ordem, rotulo, alternar=False):
    def listar():
        valores = dict(vazio)
        editar = request.args.get("editar", type=int)
        if editar:
            valores = _para_form(db.get_or_404(Modelo, editar))
        return render_template(template, pagina=slug, valores=valores, erros={}, itens=Modelo.query.order_by(*ordem).all())

    def salvar():
        v = parse(request.form)
        v.valores["id"] = request.form.get("id", type=int)
        if not v.ok:
            return render_template(template, pagina=slug, valores=v.valores, erros=v.erros,
                                   itens=Modelo.query.order_by(*ordem).all()), 400
        obj = db.get_or_404(Modelo, v.valores["id"]) if v.valores["id"] else Modelo()
        for k, val in v.valores.items():
            if k != "id":
                setattr(obj, k, val)
        db.session.add(obj)
        db.session.commit()
        flash(f"{rotulo} salvo com sucesso.", "ok")
        return redirect(url_for(f"admin.{slug}_listar"))

    def excluir(item_id):
        db.session.delete(db.get_or_404(Modelo, item_id))
        db.session.commit()
        flash(f"{rotulo} excluído.", "ok")
        return redirect(url_for(f"admin.{slug}_listar"))

    def alternar_status(item_id):
        obj = db.get_or_404(Modelo, item_id)
        obj.ativo = not obj.ativo
        db.session.commit()
        flash("Status atualizado.", "ok")
        return redirect(url_for(f"admin.{slug}_listar"))

    bp.add_url_rule(f"/{slug}", f"{slug}_listar", listar)
    bp.add_url_rule(f"/{slug}/salvar", f"{slug}_salvar", salvar, methods=["POST"])
    bp.add_url_rule(f"/{slug}/<int:item_id>/excluir", f"{slug}_excluir", excluir, methods=["POST"])
    if alternar:
        bp.add_url_rule(f"/{slug}/<int:item_id>/alternar", f"{slug}_alternar", alternar_status, methods=["POST"])


registrar_crud("precos", Servico, "admin/precos.html", parse_servico, {"ativo": True}, (Servico.id,), "Serviço", alternar=True)
registrar_crud("posts", Post, "admin/posts.html", parse_post, {"ativo": True, "data_publicacao": date.today().isoformat()},
               (Post.data_publicacao.desc(), Post.id.desc()), "Publicação")
registrar_crud("trabalhos", Trabalho, "admin/trabalhos.html", parse_trabalho, {"ativo": True}, (Trabalho.id.desc(),), "Trabalho")


# ---------------- Configurações (contato + redes) ----------------
def _tela_config(contato_valores=None, contato_erros=None, rede_valores=None, rede_erros=None, codigo=200):
    contato = db.session.get(Contato, 1) or Contato(id=1)
    return render_template(
        "admin/configuracoes.html", pagina="config",
        c_valores=contato_valores or _para_form(contato), c_erros=contato_erros or {},
        valores=rede_valores or {"ativo": True}, erros=rede_erros or {},
        itens=RedeSocial.query.order_by(RedeSocial.id).all()), codigo


@bp.get("/configuracoes")
def config():
    editar = request.args.get("editar_rede", type=int)
    rede = _para_form(db.get_or_404(RedeSocial, editar)) if editar else None
    return _tela_config(rede_valores=rede)


@bp.post("/configuracoes/contato")
def config_contato():
    v = Validador(request.form)
    v.txt("email", max=160, regex=EMAIL_RE, msg_regex="E-mail inválido.", msg_obrig="Informe o e-mail.")
    v.txt("whatsapp", max=25, regex=r"[0-9()+\-\s]{8,25}", msg_regex="WhatsApp inválido.", msg_obrig="Informe o WhatsApp.")
    v.txt("telefone", obrigatorio=False, max=40)
    v.txt("instagram", obrigatorio=False, max=80)
    v.txt("crn", obrigatorio=False, max=20)
    if not v.ok:
        return _tela_config(contato_valores=v.valores, contato_erros=v.erros, codigo=400)
    c = db.session.get(Contato, 1) or Contato(id=1)
    for k, val in v.valores.items():
        setattr(c, k, val.lstrip("@") if k == "instagram" else val)
    db.session.add(c)
    db.session.commit()
    flash("Informações de contato atualizadas.", "ok")
    return redirect(url_for("admin.config"))


@bp.post("/configuracoes/redes/salvar")
def config_rede_salvar():
    v = parse_rede(request.form)
    v.valores["id"] = request.form.get("id", type=int)
    if not v.ok:
        return _tela_config(rede_valores=v.valores, rede_erros=v.erros, codigo=400)
    r = db.get_or_404(RedeSocial, v.valores["id"]) if v.valores["id"] else RedeSocial()
    for k, val in v.valores.items():
        if k != "id":
            setattr(r, k, val)
    db.session.add(r)
    db.session.commit()
    flash("Rede social salva.", "ok")
    return redirect(url_for("admin.config"))


@bp.post("/configuracoes/redes/<int:item_id>/excluir")
def config_rede_excluir(item_id):
    db.session.delete(db.get_or_404(RedeSocial, item_id))
    db.session.commit()
    flash("Rede removida.", "ok")
    return redirect(url_for("admin.config"))
