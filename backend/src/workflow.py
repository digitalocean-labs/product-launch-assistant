from langgraph.graph import StateGraph, END

from .generation import generate_with_retries
from .search import web_search
from .quality import assess_quality
from .memory import log_step, maybe_update_memory_summary
from .diagrams import create_launch_timeline_diagram


def market_research(state: dict):
    search_query = f"{state['product_name']} {state['target_market']} market trends competitors 2024"
    query_hint = state.get("_mr_query_hint")
    if query_hint:
        search_query = f"{search_query} {query_hint}"
    web_data = web_search(search_query)
    prompt = (
        f"Conduct comprehensive market research for '{state['product_name']}' targeting '{state['target_market']}'. "
        f"Use this live market data: {web_data}\n\n"
        f"Provide analysis on:\n"
        f"1. Key competitors and market positioning\n"
        f"2. Current market trends and opportunities\n"
        f"3. Target audience insights\n"
        f"4. Market size and growth potential\n"
        f"5. SWOT analysis"
    )
    if query_hint:
        prompt += f"\n\nWhen analyzing, incorporate this hint: {query_hint}."
    state = generate_with_retries(prompt, "market_research", state, max_retries=1)
    state['market_research_quality'] = assess_quality(state.get('market_research', ''))
    log_step(state, "market_research", state.get("market_research", ""))
    maybe_update_memory_summary(state)
    return state


def product_description(state: dict):
    prompt = (
        f"Write a compelling e-commerce product description for '{state['product_name']}'. "
        f"Product details: {state['product_details']}. "
        f"Target market: {state['target_market']}."
    )
    state = generate_with_retries(prompt, "product_description", state, max_retries=1)
    log_step(state, "product_description", state.get("product_description", ""))
    maybe_update_memory_summary(state)
    return state


def pricing_strategy(state: dict):
    pricing_query = f"{state['product_name']} pricing competitor prices {state['target_market']} 2024"
    pricing_data = web_search(pricing_query)
    prompt = (
        f"Create a comprehensive pricing strategy for '{state['product_name']}' based on:\n\n"
        f"Market Research: {state['market_research']}\n\n"
        f"Product Details: {state['product_details']}\n\n"
        f"Current Pricing Data: {pricing_data}\n\n"
        f"Include:\n"
        f"1. Competitive pricing analysis\n"
        f"2. Recommended pricing tiers\n"
        f"3. Value-based pricing justification\n"
        f"4. Discount and promotion strategies\n"
        f"5. Revenue projections"
    )
    state = generate_with_retries(prompt, "pricing_strategy", state, max_retries=1)
    log_step(state, "pricing_strategy", state.get("pricing_strategy", ""))
    maybe_update_memory_summary(state)
    return state


def launch_plan(state: dict):
    prompt = (
        f"Create a comprehensive step-by-step launch plan for '{state['product_name']}' targeting '{state['target_market']}'. "
        f"Based on market research: {state['market_research'][:500]}...\n\n"
        f"Include:\n"
        f"1. Pre-launch phase (8 weeks before)\n"
        f"2. Launch phase (launch week)\n"
        f"3. Post-launch phase (8 weeks after)\n"
        f"4. Key milestones and deadlines\n"
        f"5. Success metrics and KPIs\n"
        f"6. Risk mitigation strategies\n\n"
        f"Focus ONLY on the launch timeline, activities, and execution plan. Do not include pricing information."
    )
    state = generate_with_retries(prompt, "launch_plan", state, max_retries=1)
    launch_text = state['launch_plan']
    timeline_diagram = create_launch_timeline_diagram(launch_text)
    state['launch_plan'] = f"{launch_text}\n\n--- VISUAL TIMELINE ---\n{timeline_diagram}"
    log_step(state, "launch_plan", state.get("launch_plan", ""))
    maybe_update_memory_summary(state)
    return state


def marketing_content(state: dict):
    marketing_query = f"viral marketing campaigns {state['target_market']} trending hashtags 2024"
    trending_data = web_search(marketing_query)
    prompt = (
        f"Generate comprehensive marketing content for '{state['product_name']}' using:\n\n"
        f"Product Description: {state['product_description']}\n\n"
        f"Trending Marketing Data: {trending_data}\n\n"
        f"Create:\n"
        f"1. Social media posts (Twitter/X, Instagram, LinkedIn)\n"
        f"2. Email marketing campaigns (subject lines + content)\n"
        f"3. Trending hashtags and keywords\n"
        f"4. Influencer collaboration briefs\n"
        f"5. Press release template\n"
        f"6. Content calendar suggestions\n\n"
        f"Make it engaging, trendy, and tailored to {state['target_market']}"
    )
    state = generate_with_retries(prompt, "marketing_content", state, max_retries=1)
    log_step(state, "marketing_content", state.get("marketing_content", ""))
    maybe_update_memory_summary(state)
    return state


def build_workflow():
    graph = StateGraph(dict)
    graph.add_node("market_research", market_research)
    graph.add_node("product_description", product_description)
    graph.add_node("pricing_strategy", pricing_strategy)
    graph.add_node("launch_plan", launch_plan)
    graph.add_node("marketing_content", marketing_content)

    graph.set_entry_point("market_research")

    def route_after_market_research(state: dict) -> str:
        quality = state.get("market_research_quality", "poor")
        mr_retries = state.get("_mr_retries", 0)
        max_mr_retries = 2
        if quality == "poor" and mr_retries < max_mr_retries:
            state["_mr_retries"] = mr_retries + 1
            state["_mr_query_hint"] = "broaden keywords and include competitor names"
            return "market_research"
        return "product_description"

    graph.add_conditional_edges(
        "market_research",
        route_after_market_research,
        {"market_research": "market_research", "product_description": "product_description"}
    )

    graph.add_edge("product_description", "pricing_strategy")
    graph.add_edge("pricing_strategy", "launch_plan")
    graph.add_edge("launch_plan", "marketing_content")
    graph.add_edge("marketing_content", END)

    return graph.compile()


