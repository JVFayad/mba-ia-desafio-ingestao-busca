# Desafio MBA Engenharia de Software com IA - Full Cycle

Chat com RAG (Retrieval-Augmented Generation) que permite fazer perguntas sobre o conteúdo de um PDF. O PDF é indexado em um banco PostgreSQL com extensão `pgvector`, e as perguntas são respondidas pelo modelo `gemini-2.5-flash-lite` com base exclusivamente no contexto extraído do documento.

---

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- Conta e chave de API do [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
GOOGLE_API_KEY=sua_chave_aqui
GOOGLE_EMBEDDING_MODEL=models/text-embedding-004
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag
PG_VECTOR_COLLECTION_NAME=documentos
PDF_PATH=caminho/para/seu/arquivo.pdf
```

---

## Execução passo a passo

### 1. Criar a virtualenv

```bash
make create-venv
```

Cria o ambiente virtual Python em `./venv`.

### 2. Ativar a virtualenv

```bash
source venv/bin/activate
```

> O comando `make activate-venv` abre um novo shell com a venv ativada, mas para continuar usando o mesmo terminal, prefira o `source` diretamente.

### 3. Inicializar o projeto (instalar dependências, subir banco e ingerir PDF)

```bash
make init
```

Executa em sequência:
1. `make install` — instala as dependências via `venv/bin/pip install -r requirements.txt`
2. `make db-up` — sobe o PostgreSQL com `pgvector` via Docker Compose em background
3. `make ingest` — carrega e indexa o PDF no banco de dados

### 4. Iniciar o chat

```bash
make chat
```

---

## Como usar o chat

Após iniciar com `make chat`, o terminal exibirá um prompt interativo:

```
Faça sua pergunta (ou 'sair' para encerrar):
```

- **Digite sua pergunta** e pressione Enter para receber a resposta.
- O modelo responde **somente com base no conteúdo do PDF** indexado. Se a informação não estiver no documento, a resposta será:
  > "Não tenho informações necessárias para responder sua pergunta."
- Digite **`sair`** para encerrar o chat.

**Exemplo de uso:**

```
Faça sua pergunta (ou 'sair' para encerrar): Qual é o objetivo principal do documento?

PERGUNTA: Qual é o objetivo principal do documento?
RESPOSTA: ...

Faça sua pergunta (ou 'sair' para encerrar): sair
Encerrando o chat. Até mais!
```

---

## Referência dos comandos Make

| Comando              | Descrição                                              |
|----------------------|--------------------------------------------------------|
| `make help`          | Lista todos os comandos disponíveis                    |
| `make create-venv`   | Cria a virtualenv em `./venv`                          |
| `make activate-venv` | Abre um novo shell com a venv ativada                  |
| `make install`       | Instala as dependências do projeto na venv             |
| `make db-up`         | Sobe o PostgreSQL com pgvector via Docker em background|
| `make ingest`        | Carrega e indexa o PDF no banco de dados               |
| `make chat`          | Inicia o chat interativo                               |
| `make init`          | Executa `install`, `db-up` e `ingest` em sequência    |
