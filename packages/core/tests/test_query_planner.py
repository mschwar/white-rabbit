from core.query_planner import ARIZONA_K12_TARGET_ACCOUNTS, SAFE_VENDOR_QUERY_LENGTH, compile_query_plan


LONG_ARIZONA_PROMPT = (
    "Find the Arizona K-12 VoIP benchmark contacts. "
    "I need technology and telecom decision makers for Mesa, Chandler, Peoria, Gilbert, "
    "Deer Valley, Paradise Valley, Dysart, and Maricopa. "
    "Keep the plan explicit, preserve the named accounts, and do not send the entire prompt "
    "to Tavily. Repeat the district list if needed: Mesa, Chandler, Peoria, Gilbert, "
    "Deer Valley, Paradise Valley, Dysart, Maricopa. "
    "The vendor query must stay under the 400 character Tavily limit even though the input "
    "is intentionally long and noisy. "
    "Do not lose the K-12, IT, VoIP, or Arizona intent while compiling the query."
)


def test_compile_query_plan_decomposes_arizona_benchmark_prompt():
    plan = compile_query_plan(LONG_ARIZONA_PROMPT)

    assert plan.named_accounts == list(ARIZONA_K12_TARGET_ACCOUNTS)
    assert len(plan.vendor_queries) == 8
    assert all(len(query) <= SAFE_VENDOR_QUERY_LENGTH for query in plan.vendor_queries)
    assert all("arizona" in query.lower() for query in plan.vendor_queries)
    assert any("voip" in query.lower() for query in plan.vendor_queries)


def test_compile_query_plan_preserves_simple_query_intent_and_filters():
    plan = compile_query_plan(
        "IT directors at school districts",
        filters={"location": "Albuquerque", "segment": "public schools"},
    )

    assert plan.named_accounts == []
    assert len(plan.vendor_queries) == 1
    assert len(plan.vendor_queries[0]) <= SAFE_VENDOR_QUERY_LENGTH
    assert plan.vendor_queries[0].startswith("IT directors at school districts")
    assert "location: Albuquerque" in plan.vendor_queries[0]
    assert "segment: public schools" in plan.vendor_queries[0]
