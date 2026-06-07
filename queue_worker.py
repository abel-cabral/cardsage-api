from bootstrap import carregar_secrets

carregar_secrets()

from app.shared.fila import processar_fila  # noqa: E402 — import intencional após bootstrap

if __name__ == '__main__':
    processar_fila()
