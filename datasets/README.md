# Datasets

Published, versioned datasets from the Vietnam Knowledge Commons.

## Available datasets

| Dataset                      | Description                          | Latest |
| ---------------------------- | ------------------------------------ | ------ |
| `legal-corpus/`              | Vietnamese legal documents           | v0.1.0 |
| `administrative-procedures/` | Government administrative procedures | —      |
| `official-forms/`            | Official forms and templates         | —      |
| `retrieval-corpus/`          | Optimized for RAG/retrieval          | —      |
| `instruction-dataset/`       | Fine-tuning dataset                  | —      |
| `evaluation-benchmarks/`     | Evaluation benchmarks                | —      |

## Usage

```python
from vnknowledge import load_dataset

corpus = load_dataset("legal-corpus", version="0.1.0")
```

## Adding a new dataset

See `docs/guides/contributing-data.md`.
