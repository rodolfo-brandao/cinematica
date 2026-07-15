"""FastAPI application exposing the film-graph agent over HTTP."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI

from src.agents.agent import answer_question
from src.clients.anthropic.client import AnthropicClient
from src.clients.neo4j.client import Neo4jClient
from src.clients.ollama.client import OllamaClient
from src.logger import get_logger
from src.models.agent import QueryRequest, QueryResponse


_HOST = "0.0.0.0"
_PORT = 8000

_logger = get_logger(__name__)


@asynccontextmanager
async def _lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """
    Opens the Neo4j and Ollama clients once at startup, storing them
    on `fastapi_app.state` for reuse across requests, and closes both
    on shutdown.

    :param fastapi_app: The FastAPI application instance.
    :type fastapi_app: FastAPI
    """

    fastapi_app.state.neo4j_client = Neo4jClient()
    fastapi_app.state.anthropic_client = AnthropicClient()
    fastapi_app.state.ollama_client = OllamaClient()
    _logger.info("Cinematica API startup: clients ready.")

    yield

    await fastapi_app.state.ollama_client.close()
    await fastapi_app.state.anthropic_client.close()
    fastapi_app.state.neo4j_client.close()
    _logger.info("Cinematica API shutdown: clients closed.")


app = FastAPI(title="Cinematica", lifespan=_lifespan)


@app.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    """
    Answers a natural-language question about the film knowledge graph.

    :param request: The submitted question.
    :type request: QueryRequest

    :return: The question paired with the agent's synthesized answer.
    :rtype: QueryResponse
    """

    answer = await answer_question(
        request.question,
        neo4j=app.state.neo4j_client,
        anthropic=app.state.anthropic_client,
        ollama=app.state.ollama_client
    )
    return QueryResponse(question=request.question, answer=answer)


if __name__ == "__main__":
    uvicorn.run("src.api.app:app", host=_HOST, port=_PORT, reload=True)
