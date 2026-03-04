# Agent tools for Azure AI Foundry
# Import agents here to make them easily accessible

from .word_document_agent import create_word_document, set_word_doc_context
from .weather_agent import get_weather

__all__ = [
    "create_word_document",
    "set_word_doc_context",
    "get_weather",
]
