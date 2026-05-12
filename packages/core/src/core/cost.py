from dataclasses import dataclass, field
from typing import Any

# Pricing as of 2026-05
# Source: OpenAI Pricing (gpt-4o-mini)
OPENAI_GPT4O_MINI_INPUT_PRICE = 0.15   # $0.15 per 1M input tokens
OPENAI_GPT4O_MINI_OUTPUT_PRICE = 0.60  # $0.60 per 1M output tokens

# Source: Tavily Pricing (approximate credit cost converted to USD)
TAVILY_SEARCH_PRICE = 0.01             # $0.01 per search (conservative estimate)

# Source: OpenAI Web Search Preview
OPENAI_WEB_SEARCH_PRICE = 0.01         # $10 per 1k calls = $0.01 per call

@dataclass(slots=True)
class RunMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    tavily_searches: int = 0
    openai_web_searches: int = 0
    elapsed_seconds: float = 0.0
    estimated_cost_usd: float = 0.0
    tier_distribution: dict[str, int] = field(default_factory=dict)
    funnel_counts: dict[str, int] = field(default_factory=dict)
    funnel_notes: list[str] = field(default_factory=list)


def calculate_cost(metrics: RunMetrics) -> float:
    """Calculate total API cost in USD based on metrics."""
    input_cost = (metrics.input_tokens / 1_000_000) * OPENAI_GPT4O_MINI_INPUT_PRICE
    output_cost = (metrics.output_tokens / 1_000_000) * OPENAI_GPT4O_MINI_OUTPUT_PRICE
    tavily_cost = metrics.tavily_searches * TAVILY_SEARCH_PRICE
    openai_web_cost = metrics.openai_web_searches * OPENAI_WEB_SEARCH_PRICE
    
    return round(input_cost + output_cost + tavily_cost + openai_web_cost, 6)


def estimate_search_cost(
    tavily_results_count: int,
    lead_count: int,
) -> float:
    """Rough estimate before a run."""
    # Heuristic based on proxy-lead observations
    base_input_tokens = 1000
    tokens_per_result = 250
    tokens_per_lead = 400
    
    input_tokens = base_input_tokens + (tavily_results_count * tokens_per_result)
    output_tokens = lead_count * tokens_per_lead
    
    metrics = RunMetrics(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        tavily_searches=1
    )
    return calculate_cost(metrics)
