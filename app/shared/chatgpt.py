import os
import json
from openai import AsyncOpenAI

taglist = os.getenv('TAGLIST', '').split(',')

RKLLAMA_URL = os.getenv('RKLLAMA_URL', 'http://localhost:8080')
MODEL = os.getenv('RKLLAMA_MODEL', 'qwen2.5:3b')

client = AsyncOpenAI(
    base_url=f"{RKLLAMA_URL}/v1",
    api_key='rkllama'
)

promptIntroducao = f"""
Você receberá um texto. Sua tarefa é:

1. Resumir o conteúdo de forma clara e objetiva, SEMPRE em terceira pessoa
   (ex: "O autor descreve...", "O texto apresenta...").
2. Criar um título curto e representativo, com no máximo 31 caracteres.
3. Gerar três tags que NÃO estejam nesta lista: {taglist}.
4. Listar palavras-chave relevantes.

Responda APENAS em JSON válido, sem markdown, sem explicações, no formato:
{{
  "titulo": "Título curto (até 31 caracteres)",
  "descricao": "Resumo em terceira pessoa",
  "tag1": "Primeira tag",
  "tag2": "Segunda tag",
  "tag3": "Terceira tag",
  "palavras_chaves": ["x", "y", "z"]
}}
"""

promptClassificarTag = f"""
Classifique a descrição em UMA das categorias abaixo. Retorne APENAS o nome exato da categoria.

Categorias e quando usar cada uma:
- Desenvolvimento: programação, código, APIs, frameworks, bibliotecas, linguagens de programação, DevOps
- Ciência: pesquisa científica, física, química, biologia, matemática, engenharia
- Educação: tutoriais didáticos, ensino, aprendizado geral, explicações técnicas
- Cursos: cursos pagos, formações, certificações, treinamentos, plataformas de ensino
- Inovação: startups, tendências tecnológicas, transformação digital, novas tecnologias empresariais
- Notícias: jornalismo, atualidades, eventos recentes, política
- Games: jogos, videogames, consoles, esports, reviews de games
- Filmes: cinema, filmes, críticas, trailers
- Séries: séries de TV, streaming, episódios
- Animes: anime, mangá, cultura japonesa
- Festas: eventos sociais, festas, shows, entretenimento ao vivo
- Saúde: medicina, bem-estar, fitness, nutrição, psicologia
- RedesSociais: redes sociais, influenciadores, marketing digital, engajamento
- Música: músicas, bandas, artistas, álbuns, playlists
- Livros: literatura, livros, autores, resenhas literárias
- Moda: roupas, estilo, tendências de moda, beleza
- Culinária: receitas, gastronomia, restaurantes, culinária
- Viagens: turismo, destinos, dicas de viagem
- Arte: artes visuais, design gráfico, criatividade, ilustração
- Promoções: ofertas, descontos, cupons, compras

Lista exata de categorias válidas: {taglist}

REGRAS:
- Retorne SOMENTE o nome exato de uma categoria da lista acima.
- Priorize a categoria MAIS ESPECÍFICA.
- "Desenvolvimento" tem prioridade sobre "Inovação" para conteúdo de programação.
- Se nada se encaixar, retorne "Indefinido".

Descrição a classificar:
"""


def _extrair_json(text: str) -> str:
    """Remove markdown fences que modelos menores costumam gerar."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        start = 1 if lines[0].startswith("```") else 0
        end = -1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[start:end]).strip()
    return text


async def _chat(messages: list) -> str:
    response = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content


async def _get_json(messages: list, tentativas: int = 3) -> dict:
    for i in range(tentativas):
        content = await _chat(messages)
        try:
            result = json.loads(_extrair_json(content))
            # Trunca título se o modelo ignorar o limite
            if len(result.get("titulo", "")) > 31:
                result["titulo"] = result["titulo"][:31]
            return result
        except (json.JSONDecodeError, ValueError):
            print(f"⚠️ JSON inválido na tentativa {i + 1}, tentando novamente...")
            messages = messages + [
                {"role": "assistant", "content": content},
                {"role": "user", "content": "Resposta inválida. Retorne APENAS JSON válido, sem markdown."}
            ]

    return {
        "titulo": "Indefinido", "descricao": "Indefinido",
        "tag1": "Indefinido", "tag2": "Indefinido", "tag3": "Indefinido",
        "palavras_chaves": ["Indefinido"]
    }


async def iniciarConversa(html_texto: str) -> dict:
    messages = [
        {"role": "system", "content": promptIntroducao},
        {"role": "user", "content": html_texto}
    ]
    return await _get_json(messages)


async def classificarTagsGerais(descricao: str) -> str:
    messages = [
        {"role": "system", "content": promptClassificarTag + descricao}
    ]
    for _ in range(3):
        content = (await _chat(messages)).strip()
        if content in taglist:
            return content
        messages = messages + [
            {"role": "assistant", "content": content},
            {"role": "user", "content": f"'{content}' não está na lista. Retorne somente uma das: {taglist}"}
        ]
        print(f"⚠️ Tag '{content}' fora da lista, tentando novamente...")

    return "Indefinido"


__all__ = ['iniciarConversa', 'classificarTagsGerais']
