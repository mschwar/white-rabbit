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
    assert len(plan.vendor_queries) >= 24
    assert all(len(query) <= SAFE_VENDOR_QUERY_LENGTH for query in plan.vendor_queries)
    assert all("arizona" in query.lower() for query in plan.vendor_queries)
    assert any("voip" in query.lower() for query in plan.vendor_queries)
    assert any("staff directory" in query.lower() for query in plan.vendor_queries)
    assert any("technology services" in query.lower() for query in plan.vendor_queries)
    assert any("director of technology" in query.lower() for query in plan.vendor_queries)
    for account in ARIZONA_K12_TARGET_ACCOUNTS:
        account_queries = [query for query in plan.vendor_queries if account.lower() in query.lower()]
        assert len(account_queries) >= 3


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


def test_compile_query_plan_expands_broad_query_for_high_volume_results():
    plan = compile_query_plan(
        "healthcare IT directors in Phoenix",
        max_results=50,
    )

    assert plan.broad_query is True
    assert len(plan.vendor_queries) >= 6
    assert all(len(query) <= SAFE_VENDOR_QUERY_LENGTH for query in plan.vendor_queries)
    assert any("Director of Technology" in query for query in plan.vendor_queries)
    assert any("hospitals" in query for query in plan.vendor_queries)
    assert all("Phoenix" in query or "phoenix" in query for query in plan.vendor_queries)


def test_compile_query_plan_aggressive_breadth_adds_more_bounded_queries():
    normal_plan = compile_query_plan(
        "commodity buyers at retail lumber yards in Washington",
        max_results=50,
    )
    aggressive_plan = compile_query_plan(
        "commodity buyers at retail lumber yards in Washington",
        max_results=240,
        aggressive_breadth=True,
    )

    assert normal_plan.broad_query is True
    assert aggressive_plan.broad_query is True
    assert aggressive_plan.aggressive_breadth is True
    assert len(aggressive_plan.vendor_queries) > len(normal_plan.vendor_queries)
    assert len(aggressive_plan.vendor_queries) >= 12
    assert all(len(query) <= SAFE_VENDOR_QUERY_LENGTH for query in aggressive_plan.vendor_queries)
