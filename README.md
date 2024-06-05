# WebSage API

WebSage API é uma API desenvolvida em Python com Flask. Sua principal função é servir como backend para uma extensão do Chrome chamada WebSage Extension, mas também pode ser utilizada em outras plataformas, como aplicações móveis e desktop, graças à sua flexibilidade.

A WebSage API conecta-se a diversos serviços para realizar suas operações. Utiliza um banco de dados não-relacional MongoDB para armazenamento e se comunica com a API da OpenAI para realizar análises detalhadas e processamento de requisições. Além disso, oferece serviços de extração de texto a partir de páginas web fornecidas via URL.

A ideia central é que, ao submeter uma URL, a API extrai o texto da página, gera um resumo em duas linhas (com no máximo 240 caracteres), cria um título, uma descrição e três tags associadas ao conteúdo da página. Estas tags são então organizadas em uma estrutura hierárquica com tags raízes predefinidas e tags ramos geradas pela interação com o ChatGPT da OpenAI, formando uma árvore binária de dois níveis.

## Sumário

- [Instalação](#instalação)
- [Uso](#uso)
- [Rotas da API](#rotas-da-api)
  - [Salvar Item](#salvar-item)
  - [Listar Itens](#listar-itens)
  - [Excluir Item](#excluir-item)

## Instalação

### Pré-requisitos

- Python 3.8+
- MongoDB

### Passos para instalação

1. Clone o repositório:

```bash
     git clone https://github.com/seu-usuario/websage-api.git
     cd websage-api
```

2. Crie um ambiente virtual:

```bash
    python3 -m venv websage
    source websage/bin/activate  # Linux/Mac
    websage\Scripts\activate  # Windows
```
3. Instale as dependências:

```bash
    pip install -r requirements.txt
```

4. Configure as variáveis de ambiente no arquivo .env:

```bash
    OPENAI_API_KEY=""
    PROJECT_ID=""
    ORGANIZATION=""
    DBHOST=""
    DATABASE=""
    COLLECTION=""
    TAGLIST=""
```

5. Execute a aplicação:

```bash
    python3 run.py   
```

## Uso

Esta API é projetada para ser utilizada por uma extensão de navegador chamada WebSage Extension. Ela oferece três rotas principais para salvar, listar e excluir itens no banco de dados.

### Rotas da API

#### Salvar Item
- Rota: /api/save-item
- Método: POST
- Descrição: Recebe uma URL, extrai o texto do HTML dessa URL, envia os textos para a API da OpenAI para análise e armazena as informações no MongoDB em uma estrutura hierárquica.
- Parâmetros: url (string): URL do site a ser analisado.

Exemplo de solicitação:
```bash
    curl -X POST http://localhost:5000/api/save-item \
    -H "Content-Type: application/json" \
    -d '{"url": "https://exemplo.com"}'
```

#### Listar Itens
- Rota: /api/list-items
- Método: GET
- Descrição: Retorna uma lista com todos os itens salvos na estrutura hierárquica no MongoDB.

Exemplo de solicitação:
```bash
    curl -X GET http://localhost:5000/api/list-items
```

#### Excluir Item
- Rota: /api/delete-items/id
- Método: DELETE
- Descrição: Exclui um item específico do banco de dados pelo seu ID.
	Parâmetros: id (string): ID do objeto a ser excluído.

Exemplo de solicitação:
```bash
    curl -X DELETE http://localhost:5000/api/delete-item/id-do-objeto
```

### Deploy Heroku
```bash
    heroku buildpacks:add --app meu-app --index 1 https://github.com/heroku/heroku-buildpack-google-chrome  
    heroku buildpacks:add --app meu-app --index 2 https://github.com/heroku/heroku-buildpack-chromedriver
```

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto está licenciado sob a MIT License.

