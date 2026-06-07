from bootstrap import carregar_secrets

carregar_secrets()

from app import create_app  # noqa: E402 — import intencional após bootstrap

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8021)
