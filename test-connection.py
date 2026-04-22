# /// script
# dependencies = ["openai", "python-dotenv"]
# ///
"""Schneller Verbindungstest — prueft Azure OpenAI Erreichbarkeit."""
import os, sys
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

from openai import AzureOpenAI

try:
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
    )
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")
    resp = client.chat.completions.create(
        model=deployment,
        messages=[{"role": "user", "content": "Antworte mit: OK"}],
    )
    print(f"OK — {deployment} antwortet: {resp.choices[0].message.content}")
    sys.exit(0)
except Exception as e:
    print(f"FEHLER: {e}", file=sys.stderr)
    sys.exit(1)
