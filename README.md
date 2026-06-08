# Nigerian News Semantic Search

Semantic search for Nigerian news articles using ChromaDB and multilingual
sentence embeddings.

This is Project 2 of the Nigerian news classification work. The fine-tuned
AfroXLM-R model predicts sentiment; this project stores article embeddings and
retrieves semantically similar stories.

## Features

- Persistent local ChromaDB collection
- Multilingual sentence embeddings
- CSV ingestion with duplicate-safe article IDs
- Semantic search by natural-language query
- Optional filtering by sentiment, source, and section
- Article text and generated embeddings stay out of Git

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Data

Use a private CSV containing these columns:

```text
title,text,url,label,source,section,published_at
```

The `text` field can contain only the opening paragraphs. Do not commit
third-party article text to this repository.

## Ingest

```powershell
python -m src.ingest --csv C:\path\to\punch_articles.csv
```

This creates a persistent database in `chroma_data/`. Re-running ingestion
updates existing records instead of duplicating them.

## Search

```powershell
python -m src.search "school kidnappings in Nigeria"
python -m src.search "football victories" --sentiment positive --limit 5
python -m src.search "economic policy" --section Business
```

Each result includes its similarity score, sentiment, headline, and URL.

## How embeddings are used

During ingestion, the headline and excerpt are converted into a numerical
vector by `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
ChromaDB stores that vector with article metadata.

During search, the same model embeds the query. ChromaDB returns article
vectors nearest to the query vector using cosine distance.

## Tests

```powershell
python -m unittest discover -s tests -v
```

