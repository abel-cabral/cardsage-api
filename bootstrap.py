import os


def carregar_secrets():
    """
    Carrega secrets antes de qualquer import do app.
    - Se as variáveis INFISICAL_* estiverem presentes: busca do Infisical.
    - Caso contrário: carrega o .env local (desenvolvimento).
    Carrega .env sem override primeiro para que vars de processo (Docker/prod)
    sempre tenham prioridade, mas vars locais estejam disponíveis em dev.
    """
    from dotenv import load_dotenv
    load_dotenv(override=False)

    url          = os.environ.get("INFISICAL_URL")
    client_id    = os.environ.get("INFISICAL_CLIENT_ID")
    client_sec   = os.environ.get("INFISICAL_CLIENT_SECRET")
    project_id   = os.environ.get("INFISICAL_PROJECT_ID")
    environment  = os.environ.get("INFISICAL_ENVIRONMENT", "prod")
    access_token = os.environ.get("INFISICAL_ACCESS_TOKEN")

    if (access_token or all([client_id, client_sec])) and url and project_id:
        try:
            from infisical_client import ClientSettings, InfisicalClient, ListSecretsOptions

            settings = ClientSettings(site_url=url, access_token=access_token) if access_token else \
                       ClientSettings(site_url=url, client_id=client_id, client_secret=client_sec)

            client = InfisicalClient(settings)
            secrets = client.listSecrets(
                options=ListSecretsOptions(
                    project_id=project_id,
                    environment=environment,
                    path="/",
                )
            )
            for s in secrets:
                os.environ.setdefault(s.secret_key, s.secret_value)
            print(f"✅ {len(secrets)} secrets carregados do Infisical ({environment})")
            return
        except ImportError:
            print("⚠️  infisical-python não instalado — usando .env como fallback")
        except Exception as e:
            print(f"⚠️  Infisical indisponível ({e}) — usando .env como fallback")

    from dotenv import load_dotenv
    load_dotenv(override=True)
    print("📄 Secrets carregados do .env (modo local)")
