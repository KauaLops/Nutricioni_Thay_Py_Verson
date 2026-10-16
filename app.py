"""Ponto de entrada (Vercel, `flask run` e gunicorn: `gunicorn app:app`)."""
from thayane import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
