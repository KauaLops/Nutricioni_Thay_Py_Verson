"""Comandos de manutenção. Uso:
  python manage.py init                      -> cria tabelas, admin inicial e conteúdo de exemplo
  python manage.py criar-admin EMAIL SENHA   -> cria (ou redefine a senha de) um administrador
"""
import sys
from thayane import create_app
from thayane.extensions import db
from thayane.models import Usuario
from thayane.seed import inicializar, hash_senha

app = create_app(auto_init=False)

with app.app_context():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "init":
        inicializar()
        print("Banco inicializado.")
    elif cmd == "criar-admin" and len(sys.argv) == 4:
        email, senha = sys.argv[2].strip().lower(), sys.argv[3]
        if len(senha) < 8:
            sys.exit("A senha deve ter ao menos 8 caracteres.")
        db.create_all()
        u = Usuario.query.filter_by(email=email).first() or Usuario(nome="Administrador", email=email)
        u.senha = hash_senha(senha); u.ativo = True; u.role = "ADMIN"
        db.session.add(u); db.session.commit()
        print("Administrador salvo:", email)
    else:
        print(__doc__)
