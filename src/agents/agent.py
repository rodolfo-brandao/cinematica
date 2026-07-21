"""Entry point invoking the agent's LangGraph pipeline."""

from src.agents.graph import build_graph
from src.agents.state import AgentState
from src.clients.anthropic.client import AnthropicClient
from src.clients.neo4j.client import Neo4jClient
from src.clients.ollama.client import OllamaClient
from src.clients.tmdb.client import TmdbClient


_GRAPH = build_graph()


async def answer_question(
    question: str,
    neo4j: Neo4jClient,
    anthropic: AnthropicClient,
    ollama: OllamaClient,
    tmdb: TmdbClient
) -> str:
    """
    Answers a natural-language question about the film graph by running
    the plan/resolve/query/verify/compose pipeline defined in
    `src.agents.graph`.

    :param question: The user's natural-language question.
    :type question: str
    :param neo4j: The Neo4j client the pipeline queries.
    :type neo4j: Neo4jClient
    :param anthropic: The Anthropic client driving each reasoning stage.
    :type anthropic: AnthropicClient
    :param ollama: The Ollama client backing semantic (vector) search.
    :type ollama: OllamaClient
    :param tmdb: The TMDb client backing external movie search/ingestion
        and review-sentiment persistence.
    :type tmdb: TmdbClient

    :return: The pipeline's synthesized answer.
    :rtype: str
    """

    initial_state: AgentState = {
        "question": question,
        "plan": "",
        "resolved": "",
        "rows": [],
        "query_notes": "",
        "verified": False,
        "verification_notes": "",
        "query_attempts": 0,
        "answer": ""
    }
    result = await _GRAPH.ainvoke(
        initial_state,
        config={"configurable": {
            "neo4j": neo4j,
            "anthropic": anthropic,
            "ollama": ollama,
            "tmdb": tmdb
        }}
    )
    return result["answer"]
