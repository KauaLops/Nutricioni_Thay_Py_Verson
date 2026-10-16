# Thayane-Nutri (Python / Flask)

Portfólio profissional da nutricionista Thayane Luíze Lopes de Souza Alcântara (CRN 49735).
Mesmo visual do projeto Java, agora em **Python 3.11+ · Flask · SQLAlchemy · PostgreSQL (Supabase)**.
Site público em página única (Início, Agendamento, Contato, Preços com carrossel e Blog) + painel administrativo com login.

## Estrutura
```
app.py                 ponto de entrada (Vercel / flask run / gunicorn)
manage.py              comandos: init, criar-admin
requirements.txt
public/                arquivos estáticos (css, js, images) — a Vercel serve esta pasta pela CDN
thayane/
  __init__.py          app factory, CSRF, cabeçalhos de segurança, tratamento de erros
  config.py  models.py  validacao.py  seed.py  mailer.py
  public.py  api.py  admin.py   (rotas)
  templates/           Jinja2 (index, post, legal, error, admin/*)
```

## 1. Rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # preencha (veja abaixo)
python manage.py init            # cria tabelas, administrador e conteúdo de exemplo
flask run                        # http://127.0.0.1:5000
```
No `.env` local coloque `FLASK_DEBUG=1` (sem isso o cookie de sessão é "Secure" e não funciona em http).

### Variáveis (.env)
| Variável | Descrição |
|---|---|
| `SECRET_KEY` | **obrigatória**. Gere: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | URL do PostgreSQL (Supabase). Alternativa: `DB_HOST/DB_PORT/DB_NAME/DB_USERNAME/DB_PASSWORD` |
| `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DESTINO` | SMTP do formulário de agendamento |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | cria o primeiro administrador (mín. 8 caracteres) |

Nunca versione o `.env` (já está no `.gitignore`) nem coloque senhas no código.

## 2. Banco no Supabase
Em *Connect* no painel do Supabase copie a string de conexão do **Transaction pooler** (porta 6543, recomendada para a Vercel)
ou do **Session pooler** (porta 5432) e use em `DATABASE_URL`. Se a senha tiver caracteres especiais (`@`, `/`, `#`), codifique-os
(ex.: `@` vira `%40`). O `sslmode=require` é adicionado automaticamente.

Depois do primeiro deploy, proteja as tabelas contra a API pública do Supabase (SQL Editor):
```sql
ALTER TABLE usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE servico ENABLE ROW LEVEL SECURITY;
ALTER TABLE post ENABLE ROW LEVEL SECURITY;
ALTER TABLE trabalho ENABLE ROW LEVEL SECURITY;
ALTER TABLE contato ENABLE ROW LEVEL SECURITY;
ALTER TABLE rede_social ENABLE ROW LEVEL SECURITY;
```
O app conecta como `postgres` e não é afetado; isso só bloqueia acesso externo.

## 3. Deploy na Vercel
1. Suba o projeto no GitHub (sem o `.env`).
2. Na Vercel: *Add New → Project* → escolha o repositório. A Vercel detecta Flask sozinha (arquivo `app.py` com a variável `app`).
3. Em *Settings → Environment Variables* cadastre: `SECRET_KEY`, `DATABASE_URL`, `MAIL_USERNAME`, `MAIL_PASSWORD`,
   `MAIL_DESTINO`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`.
4. Faça o deploy. Na primeira visita o app cria as tabelas e o administrador automaticamente (`AUTO_INIT=1`).
   Se preferir, rode `python manage.py init` na sua máquina apontando para o Supabase e defina `AUTO_INIT=0` na Vercel.
5. Depois de entrar no painel, remova `ADMIN_PASSWORD` das variáveis.

Em outros hosts (Render, Railway, VPS): `gunicorn app:app`.

## 4. Painel administrativo
`/admin/login` → e-mail + senha. Menu: **Preços** (criar, editar, excluir, ativar/desativar; benefícios um por linha),
**Trabalhos**, **Blog**, **Configurações** (e-mail, WhatsApp, Instagram, CRN e redes extras).
Alterações aparecem no site público na hora.
Imagens: informe um caminho (arquivo em `public/images/`, ex.: `/images/minha-foto.jpg`) ou um link `https://...`.

Novo administrador ou redefinição de senha: `python manage.py criar-admin email@exemplo.com SenhaForte123`.

## 5. E-mail do agendamento (Gmail)
Ative a verificação em duas etapas e crie uma **senha de app** em https://myaccount.google.com/apppasswords.
Use `MAIL_HOST=smtp.gmail.com`, `MAIL_PORT=587`, `MAIL_USERNAME=seu@gmail.com`, `MAIL_PASSWORD=<senha de app>`.
Se o SMTP falhar, o visitante vê uma mensagem amigável e o erro vai para o log.

## 6. Segurança
Senhas com hash PBKDF2-SHA256 (600 mil iterações); `/admin/**` só para administrador autenticado; proteção CSRF em todos os POST
(inclusive o formulário público, via cabeçalho `X-CSRF-TOKEN`); Jinja2 escapa todo conteúdo (XSS); consultas parametrizadas
(SQLAlchemy); validação no navegador e no servidor; cookies HttpOnly/SameSite/Secure; CSP e demais cabeçalhos de segurança;
tratamento global de erros. Limitação: não há bloqueio de tentativas de login (use senha forte).
