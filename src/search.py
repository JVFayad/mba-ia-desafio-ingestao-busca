import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{context}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{question}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def search_prompt(question=None):
    for k in (
        "DATABASE_URL",
        "PG_VECTOR_COLLECTION_NAME",
        "GOOGLE_API_KEY",
        "GOOGLE_EMBEDDING_MODEL",
    ):
        if k not in os.environ:
            raise RuntimeError(f"Missing required environment variable: {k}")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_API_MODEL", "gemini-embedding-2-preview")
    )

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True,
    )

    database_context = store.similarity_search_with_score(question, k=10)

    question_template = PromptTemplate(
        input_variables=["context", "question"], template=PROMPT_TEMPLATE
    )

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

    chain = question_template | llm

    return chain.invoke(
        {
            "context": "\n\n".join([doc.page_content for doc, _ in database_context]),
            "question": question,
        }
    )
