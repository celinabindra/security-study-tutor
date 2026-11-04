# Security+ Study Tutor

A command-line AI tutor for CompTIA Security+ that saves conversations in PostgreSQL, so you can pick up where you left off. It runs locally with Ollama, so no API key is needed.

**Built with:** Python, PostgreSQL, Psycopg, and Ollama (Llama 3.2)

## Setup

Requires Python 3.13, PostgreSQL, and Ollama.

```bash
git clone https://github.com/YOUR-USERNAME/security-study-tutor.git
cd security-study-tutor
python3.13 -m venv .venv
source .venv/bin/activate
pip install "psycopg[binary]" ollama
createdb chatbot
psql chatbot -f schema.sql
ollama pull llama3.2
```

## Usage

```bash
python tutor.py        # continue the latest conversation
python tutor.py --new  # start a new conversation
```

Type `quit` to exit.
