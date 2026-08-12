import os
from dataclasses import dataclass
from datetime import datetime, timezone

from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.0-flash"
# simulated cost per 1M tokens; real free-tier is $0
INPUT_COST_PER_1M = 0.10
OUTPUT_COST_PER_1M = 0.40

SYSTEM_PROMPT = """\
You are a helpful support assistant for DeployHub, \
a cloud deployment platform. Answer questions using only the context \
provided below. If the context does not contain the answer, say you \
are not sure and suggest contacting support. Cite the source filename \
in square brackets like [pricing.md] at the end of relevant sentences.
"""


@dataclass
class GenerationResult:
    answer: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    sources: list[str]


@dataclass
class UsageLog:
    timestamp: str
    query: str
    answer: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    sources: list[str]


_usage_log: list[UsageLog] = []


def get_usage_log():
    return list(_usage_log)


def clear_usage_log():
    _usage_log.clear()


@dataclass
class Generator:
    model_name: str = MODEL_NAME

    def _build_context(self, search_results):
        parts = []
        sources = []
        for result in search_results:
            parts.append(
                f"[{result.chunk.source} > {result.chunk.heading}]\n{result.chunk.text}"
            )
            if result.chunk.source not in sources:
                sources.append(result.chunk.source)
        return "\n\n---\n\n".join(parts), sources

    def generate(self, query, search_results):
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        context, sources = self._build_context(search_results)
        prompt = f"Context from the knowledge base:\n{context}\n\nQuestion: {query}"

        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )

        usage = response.usage_metadata
        prompt_tokens = (usage.prompt_token_count if usage else None) or 0
        completion_tokens = (usage.candidates_token_count if usage else None) or 0

        cost = (
            prompt_tokens * INPUT_COST_PER_1M / 1_000_000
            + completion_tokens * OUTPUT_COST_PER_1M / 1_000_000
        )

        answer = response.text or ""

        _usage_log.append(
            UsageLog(
                timestamp=datetime.now(timezone.utc).isoformat(),
                query=query,
                answer=answer,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost,
                sources=sources,
            )
        )

        return GenerationResult(
            answer=answer,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            sources=sources,
        )


if __name__ == "__main__":
    from retriever import Chunk, SearchResult

    g = Generator()
    fake_results = [
        SearchResult(Chunk("Pro plan costs $29/month.", "pricing.md", "Pricing"), 0.9)
    ]
    context, sources = g._build_context(fake_results)
    assert "$29" in context, "context should contain chunk text"
    assert sources == ["pricing.md"], f"expected ['pricing.md'], got {sources}"
    print("self-check passed")
