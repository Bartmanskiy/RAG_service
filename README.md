# Corporate Knowledge Base — RAG Service

RAG-сервіс для роботи з корпоративною базою знань. Система дозволяє завантажувати документи, автоматично обробляти їх, створювати embeddings та відповідати на запитання користувача на основі інформації з цих документів.

Проєкт побудований на **FastAPI, MongoDB Vector Search та Ollama** і підтримує потокову генерацію відповідей через **Server-Sent Events (SSE)**.

---

## Можливості

* Завантаження документів у форматах:

  * PDF
  * TXT
  * Markdown
* Обмеження розміру файлу — 10 MB.
* Перевірка дублікатів за SHA-256 hash.
* Асинхронна обробка документів у background task.
* Розбір документів та розбиття тексту на chunks.
* Генерація embeddings за допомогою `nomic-embed-text`.
* Зберігання embeddings у MongoDB.
* Семантичний пошук через MongoDB Vector Search.
* Фільтрація пошуку за конкретними документами.
* Порогове значення релевантності результатів.
* RAG-відповіді за допомогою `llama3.2:3b`.
* LLM отримує тільки знайдений контекст і не повинна використовувати зовнішні знання.
* Потокова генерація відповіді через SSE.
* Відображення джерел відповіді: документ, сторінка, score та snippet.
* Видалення документа разом із його chunks та embeddings.
* Обробка помилок ingestion з переведенням документа у статус `failed`.
* Автоматичне створення MongoDB indexes та Vector Search index.
* Docker Compose для запуску всього сервісу.
* Автоматичне завантаження необхідних Ollama-моделей.
* Автоматичні тести для основних сервісів.

---

## Архітектура

Основний потік роботи системи:

```text
                    ┌─────────────────┐
                    │     Client      │
                    │   HTML / JS     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    │     Routers     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │ DocumentService │          │    RAGService   │
     └────────┬────────┘          └────────┬────────┘
              │                            │
              ▼                            ▼
     ┌─────────────────┐          ┌─────────────────┐
     │IngestionService │          │RetrievalService │
     └────────┬────────┘          └────────┬────────┘
              │                            │
       ┌──────┴──────┐                     │
       ▼             ▼                     ▼
   Parsers       Chunking             Embeddings
       │             │                     │
       └──────┬──────┘                     ▼
              │                      MongoDB Vector
              ▼                         Search
        Ollama Embeddings                  │
                                           ▼
                                      RAG Context
                                           │
                                           ▼
                                     Ollama LLM
```

### Основний RAG flow

```text
Document
   ↓
Parse
   ↓
Chunk
   ↓
Embedding
   ↓
MongoDB
   ↓
Vector Search
   ↓
Relevant Chunks
   ↓
Context
   ↓
LLM
   ↓
Answer + Sources
```

---

## Технології

### Backend

* Python 3.11
* FastAPI
* Pydantic
* Pydantic Settings
* Uvicorn

### Database

* MongoDB 8
* MongoDB Vector Search
* PyMongo Async API

### AI

* Ollama
* `llama3.2:3b` — генерація відповідей
* `nomic-embed-text` — створення embeddings

### Документи

* PDF — `pypdf`
* TXT
* Markdown

### Frontend

* HTML
* CSS
* JavaScript
* Server-Sent Events (SSE)

### Infrastructure

* Docker
* Docker Compose

### Testing

* pytest
* pytest-anyio

---

## Структура проєкту

```text
RAG_service/
│
├── app/
│   ├── clients/
│   │   ├── embedding_client.py
│   │   ├── llm_client.py
│   │   └── ollama_client.py
│   │
│   ├── models/
│   │   ├── document.py
│   │   └── chunk.py
│   │
│   ├── parsers/
│   │   ├── parser.py
│   │   ├── pdf_parser.py
│   │   ├── txt_parser.py
│   │   └── md_parser.py
│   │
│   ├── repositories/
│   │   ├── document_repository.py
│   │   └── chunk_repository.py
│   │
│   ├── routers/
│   │   ├── documents.py
│   │   └── ask.py
│   │
│   ├── schemas/
│   │   ├── document.py
│   │   └── ask.py
│   │
│   ├── services/
│   │   ├── chunking_service.py
│   │   ├── document_service.py
│   │   ├── ingestion_service.py
│   │   ├── rag_service.py
│   │   └── retrieval_service.py
│   │
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   │
│   ├── config.py
│   ├── database.py
│   ├── database_init.py
│   ├── database_indexes.py
│   ├── dependencies.py
│   ├── main.py
│   └── vector_index.py
│
├── tests/
│   ├── test_chunking_service.py
│   ├── test_retrieval_service.py
│   └── test_rag_service.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Як запустити

### 1. Клонувати репозиторій

```bash
git clone https://github.com/Bartmanskiy/RAG_service.git
cd RAG_service
```

### 2. Створити `.env`

Скопіювати `.env.example` у `.env`:

```bash
cp .env.example .env
```

Основні параметри:

```env
MONGO_URL=mongodb://mongodb:27017
MONGO_DB=corporate_knowledge

OLLAMA_URL=http://ollama:11434
LLM_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text

CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
SCORE_THRESHOLD=0.8

MAX_FILE_SIZE=10485760
```

### 3. Запустити Docker Compose

```bash
docker compose up -d --build
```

Docker Compose запускає:

* FastAPI;
* MongoDB;
* Ollama;
* Ollama initialization container для завантаження моделей.

Перевірити статус:

```bash
docker compose ps
```

### 4. Перевірити API

```bash
curl http://localhost:8000/health
```

Очікувана відповідь:

```json
{
  "status": "ok",
  "llm_model": "llama3.2:3b",
  "embedding_model": "nomic-embed-text",
  "mongodb": "ok"
}
```

---

## Web Client

Після запуску сервісу веб-інтерфейс доступний за адресою:

```text
http://localhost:8000/
```

Через нього можна:

* завантажувати документи;
* бачити статус ingestion;
* видаляти документи;
* ставити запитання;
* отримувати потокову відповідь;
* переглядати джерела відповіді.

---

## API

### Health Check

```http
GET /health
```

Перевіряє стан API, MongoDB та конфігурацію AI-моделей.

---

### Завантаження документа

```http
POST /api/documents
```

Multipart upload.

Підтримуються:

```text
.pdf
.txt
.md
```

При успішному завантаженні API повертає статус:

```text
202 Accepted
```

Документ спочатку отримує статус:

```text
processing
```

Після завершення ingestion:

```text
ready
```

У разі помилки:

```text
failed
```

---

### Отримання списку документів

```http
GET /api/documents
```

Повертає:

* `id`
* `filename`
* `status`
* `chunks_count`
* `created_at`

---

### Отримання документа

```http
GET /api/documents/{document_id}
```

---

### Видалення документа

```http
DELETE /api/documents/{document_id}
```

Видаляє:

1. документ;
2. всі його chunks;
3. embeddings, які зберігаються всередині chunks.

---

### RAG-запит

```http
POST /api/ask
```

Приклад:

```json
{
  "question": "What framework does our company use?",
  "top_k": 5
}
```

Відповідь містить:

```json
{
  "answer": "FastAPI.",
  "sources": [
    {
      "document_id": "...",
      "filename": "technologies.txt",
      "page": 1,
      "score": 0.9,
      "snippet": "Our company uses FastAPI."
    }
  ]
}
```

---

### Streaming RAG

```http
GET /api/ask/stream
```

Використовує **Server-Sent Events (SSE)**.

Потік містить такі типи подій:

```text
sources
token
done
```

Приклад:

```text
event: sources
data: [...]

event: token
data: {"token": "Fast"}

event: token
data: {"token": "API"}

event: done
data: {}
```

Якщо релевантної інформації немає, LLM не викликається. Система повертає:

```text
У документах не знайдено інформації за цим запитом
```

---

## RAG та релевантність

Під час пошуку система:

1. перетворює запит користувача на embedding;
2. виконує Vector Search у MongoDB;
3. отримує найбільш схожі chunks;
4. застосовує `SCORE_THRESHOLD`;
5. передає релевантний контекст у LLM;
6. формує відповідь тільки на основі цього контексту.

Якщо жоден chunk не проходить threshold, LLM не викликається.

Це допомагає уникати відповідей на основі інформації, якої немає у корпоративній базі знань.

---

## Chunking

Розмір chunk та overlap можна змінювати через `.env`:

```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

Кожен chunk зберігає:

* текст;
* `document_id`;
* номер сторінки;
* порядковий `chunk_index`;
* embedding.

Для PDF номер сторінки зберігається окремо, що дозволяє показувати джерело відповіді користувачу.

---

## MongoDB Indexes

Під час запуску автоматично створюються:

### Content hash index

Унікальний index для запобігання дублюванню документів:

```text
documents.content_hash
```

### Document ID index

Для швидкого пошуку chunks конкретного документа:

```text
chunks.document_id
```

### Vector Search index

MongoDB Vector Search index:

```text
vector_index
```

Використовує:

```text
768 dimensions
cosine similarity
document_id filter
```

---

## Ollama

Проєкт використовує дві моделі:

### LLM

```text
llama3.2:3b
```

Використовується для генерації відповідей на основі retrieved context.

### Embeddings

```text
nomic-embed-text
```

Використовується для перетворення тексту та запитів у vector embeddings.

Моделі автоматично завантажуються через `ollama-init` при запуску Docker Compose.

---

## Тести

Для запуску тестів:

```bash
python -m pytest -q
```

Поточний test suite перевіряє:

* chunking;
* overlap;
* нумерацію chunks;
* validation `document_id`;
* filtering за score;
* RAG без результатів;
* виклик LLM з retrieved context;
* sources;
* SSE streaming;
* поведінку без релевантних результатів.

Поточний результат:

```text
10 passed
```

---

## Конфігурація

Основні параметри задаються через environment variables:

| Змінна            | Значення за замовчуванням | Призначення                  |
| ----------------- | ------------------------: | ---------------------------- |
| `MONGO_URL`       | `mongodb://mongodb:27017` | MongoDB connection           |
| `MONGO_DB`        |     `corporate_knowledge` | Назва БД                     |
| `OLLAMA_URL`      |     `http://ollama:11434` | Ollama URL                   |
| `LLM_MODEL`       |             `llama3.2:3b` | LLM                          |
| `EMBEDDING_MODEL` |        `nomic-embed-text` | Embedding model              |
| `CHUNK_SIZE`      |                    `1000` | Розмір chunk                 |
| `CHUNK_OVERLAP`   |                     `200` | Перекриття chunks            |
| `TOP_K`           |                       `5` | Кількість результатів пошуку |
| `SCORE_THRESHOLD` |                     `0.8` | Мінімальний score            |
| `MAX_FILE_SIZE`   |                `10485760` | Максимальний розмір файлу    |

---

## Основні принципи проєкту

Проєкт побудований із розділенням відповідальності між шарами:

```text
Router
  ↓
Service
  ↓
Repository / Client
  ↓
Database / Ollama
```

Для AI-компонентів використовуються окремі інтерфейси:

```text
LLMClient
EmbeddingClient
```

та конкретна реалізація:

```text
OllamaClient
```

Це дозволяє в майбутньому замінити Ollama на інший AI provider без значної зміни бізнес-логіки.

---

