import os


def _bootstrap():
    """
    Carrega secrets antes de qualquer import do app.
    - Se as variáveis INFISICAL_* estiverem presentes: busca do Infisical.
    - Caso contrário: carrega o .env local (desenvolvimento).
    """
    url        = os.environ.get("INFISICAL_URL")
    client_id  = os.environ.get("INFISICAL_CLIENT_ID")
    client_sec = os.environ.get("INFISICAL_CLIENT_SECRET")
    project_id = os.environ.get("INFISICAL_PROJECT_ID")
    environment = os.environ.get("INFISICAL_ENVIRONMENT", "prod")

    if all([url, client_id, client_sec, project_id]):
        try:
            from infisical_client import (
                ClientSettings, InfisicalClient,
                UniversalAuthMethod, ListSecretsOptions,
            )
            client = InfisicalClient(ClientSettings(
                site_url=url,
                auth=UniversalAuthMethod(
                    client_id=client_id,
                    client_secret=client_sec,
                ),
            ))
            secrets = client.listSecrets(
                options=ListSecretsOptions(
                    project_id=project_id,
                    environment=environment,
                    path="/",
                )
            )
            for s in secrets:
                os.environ.setdefault(s.secretKey, s.secretValue)
            print(f"✅ {len(secrets)} secrets carregados do Infisical ({environment})")
            return
        except ImportError:
            print("⚠️  infisical-python não instalado — usando .env como fallback")
        except Exception as e:
            print(f"⚠️  Infisical indisponível ({e}) — usando .env como fallback")

    from dotenv import load_dotenv
    load_dotenv(override=True)
    print("📄 Secrets carregados do .env (modo local)")


_bootstrap()

from app import create_app  # noqa: E402 — import intencional após bootstrap

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8021)
