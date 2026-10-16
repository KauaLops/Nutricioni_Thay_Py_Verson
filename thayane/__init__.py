import hmac
import logging
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, render_template, request, session

ROOT = Path(__file__).resolve().parent.parent


def create_app(auto_init=None):
    load_dotenv(ROOT / ".env")
    from .config import Config
    from .extensions import db, login_manager
    from .models import Usuario

    # Arquivos estáticos em /public (na Vercel a pasta public/ é servida pela CDN, nas mesmas URLs).
    app = Flask(__name__, static_folder=str(ROOT / "public"), static_url_path="")
    app.config.from_object(Config)
    if not app.config["SECRET_KEY"]:
        if Config.DEBUG_MODE:
            app.config["SECRET_KEY"] = secrets.token_hex(32)
        else:
            raise RuntimeError("Defina SECRET_KEY (veja .env.example).")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin.login"

    @login_manager.user_loader
    def carregar_usuario(uid):
        u = db.session.get(Usuario, int(uid))
        return u if u and u.ativo else None

    # ---------- CSRF ----------
    def csrf_token():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(32)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def verificar_csrf():
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            enviado = request.headers.get("X-CSRF-TOKEN") or request.form.get("_csrf", "")
            esperado = session.get("_csrf", "")
            if not esperado or not hmac.compare_digest(esperado, enviado):
                abort(400, description="csrf")

    # ---------- Filtros ----------
    @app.template_filter("brl")
    def brl(v):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("data_br")
    def data_br(d):
        return d.strftime("%d/%m/%Y") if d else ""

    # ---------- Cabeçalhos de segurança ----------
    @app.after_request
    def cabecalhos(resp):
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com; img-src 'self' data: https:; frame-ancestors 'none'; form-action 'self'")
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if request.path.startswith("/admin"):
            resp.headers["Cache-Control"] = "no-store"
        return resp

    # ---------- Blueprints ----------
    from .admin import bp as admin_bp
    from .api import bp as api_bp
    from .public import bp as public_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    # ---------- Tratamento global de erros ----------
    def _erro(codigo, msg_api):
        if request.path.startswith("/api/"):
            return jsonify(message=msg_api), codigo
        return render_template("error.html", status=codigo), codigo

    @app.errorhandler(400)
    def e400(e):
        return _erro(400, "Sessão expirada ou requisição inválida. Recarregue a página e tente novamente.")

    @app.errorhandler(404)
    def e404(e):
        return _erro(404, "Recurso não encontrado.")

    @app.errorhandler(405)
    def e405(e):
        return _erro(405, "Método não permitido.")

    @app.errorhandler(413)
    def e413(e):
        return _erro(413, "Conteúdo muito grande.")

    @app.errorhandler(500)
    def e500(e):
        app.logger.exception("Erro interno")
        return _erro(500, "Erro interno. Tente novamente em instantes.")

    logging.basicConfig(level=logging.INFO)
    if auto_init is None:
        auto_init = os.getenv("AUTO_INIT", "1") == "1"
    if auto_init:
        from .seed import inicializar
        with app.app_context():
            try:
                inicializar()
            except Exception:
                db.session.rollback()
                app.logger.exception("Falha ao inicializar o banco (verifique DATABASE_URL).")
    return app
