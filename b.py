from watson_developer_cloud import NaturalLanguageUnderstandingV1

nlu = NaturalLanguageUnderstandingV1(
    version='2018-03-16',
    iam_api_key='bTZEhYvdGluVwFAvfl9F-WnecbLrGj-UJVvCqa7_yHh4',
    url='https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29'# 4072b4b7-86f6-4588-9ed3-ebb13dccb8b6
)

text = """
O texto discute a escolha de um framework React para construir uma aplicação ou site. Os frameworks recomendados são Next.js, Remix, Gatsby e Expo. Cada framework tem suas características e benefícios. O texto também discute a possibilidade de usar React sem um framework, mas a maioria das aplicações e sites acabam por construir soluções para problemas comuns. Os frameworks podem ajudar a evitar a construção de um framework personalizado e fornecer suporte a recursos como routing, bundling e server technologies.
"""

response = nlu.analyze(
    text=text,
    features={
        'entities': {},
        'keywords': {}
    },
    parameters={
        'return': 'json'
    }
).get_result()

print(response)

# Importar as bibliotecas necessárias
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Substitua 'YOUR_API_KEY' e 'YOUR_URL' pelas suas credenciais do Watson Assistant
api_key = 'WcVP_PMY8-RFVYbH3Ifwd8EThJfa_BIP4uZIO0773oiD'
url = 'https://api.us-south.assistant.watson.cloud.ibm.com/instances/7f015f1e-c902-46b0-99c7-a0014ee334a7'
assistant_id = 'YOUR_ASSISTANT_ID'  # Este é o ID do assistente que você criou

# Autenticar com o Watson Assistant
authenticator = IAMAuthenticator(api_key)
assistant = AssistantV2(
    version='2021-06-14',
    authenticator=authenticator
)
assistant.set_service_url(url)

# Criar uma nova sessão
session_response = assistant.create_session(
    assistant_id=assistant_id
).get_result()

session_id = session_response['session_id']

# Enviar uma mensagem para o assistente
message_response = assistant.message(
    assistant_id=assistant_id,
    session_id=session_id,
    input={
        'message_type': 'text',
        'text': 'Olá, como posso te ajudar?'
    }
).get_result()

# Imprimir a resposta do assistente
print(message_response)

# Fechar a sessão
assistant.delete_session(
    assistant_id=assistant_id,
    session_id=session_id
)