from langgraph.graph import StateGraph, END
import asyncio
from typing import Dict, Any

from .generation import generate_with_retries, generate_with_retries_async
from .search import web_search, web_search_async
from .quality import assess_quality
from .memory import log_step, maybe_update_memory_summary
from .diagrams import create_launch_timeline_diagram


async def market_research(state: dict):
    search_query = f"{state['product_name']} {state['target_market']} market trends competitors 2024"
    query_hint = state.get("_mr_query_hint")
    if query_hint:
        search_query = f"{search_query} {query_hint}"
    web_data = await web_search_async(search_query)
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
    state = await generate_with_retries_async(prompt, "market_research", state, max_retries=1)
    state['market_research_quality'] = assess_quality(state.get('market_research', ''))
    log_step(state, "market_research", state.get("market_research", ""))
    maybe_update_memory_summary(state)
    return state


async def product_description(state: dict):
    prompt = (
        f"Write a compelling e-commerce product description for '{state['product_name']}'. "
        f"Product details: {state['product_details']}. "
        f"Target market: {state['target_market']}."
    )
    state = await generate_with_retries_async(prompt, "product_description", state, max_retries=1)
    log_step(state, "product_description", state.get("product_description", ""))
    maybe_update_memory_summary(state)
    return state


async def pricing_strategy(state: dict):
    pricing_query = f"{state['product_name']} pricing competitor prices {state['target_market']} 2024"
    pricing_data = await web_search_async(pricing_query)
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
    state = await generate_with_retries_async(prompt, "pricing_strategy", state, max_retries=1)
    log_step(state, "pricing_strategy", state.get("pricing_strategy", ""))
    maybe_update_memory_summary(state)
    return state


async def launch_plan(state: dict):
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
    state = await generate_with_retries_async(prompt, "launch_plan", state, max_retries=1)
    launch_text = state['launch_plan']
    timeline_diagram = create_launch_timeline_diagram(launch_text)
    state['launch_plan'] = f"{launch_text}\n\n--- VISUAL TIMELINE ---\n{timeline_diagram}"
    log_step(state, "launch_plan", state.get("launch_plan", ""))
    maybe_update_memory_summary(state)
    return state


async def marketing_content(state: dict):
    marketing_query = f"viral marketing campaigns {state['target_market']} trending hashtags 2024"
    trending_data = await web_search_async(marketing_query)
    # Enforce strict JSON output for marketing content
    prompt = (
        f"Generate comprehensive marketing content for '{state['product_name']}' using the inputs below.\n\n"
        f"Inputs:\n"
        f"- Product Description: {state['product_description']}\n"
        f"- Trending Marketing Data: {trending_data}\n"
        f"- Target Market: {state['target_market']}\n\n"
        f"CRITICAL: You must return ONLY a valid JSON object. No markdown, no code fences, no explanations, no extra text.\n\n"
        f"Use this exact JSON schema:\n"
        f"{{\n"
        f"  \"social_posts\": {{\n"
        f"    \"x\": [\"Post 1 for X/Twitter\", \"Post 2 for X/Twitter\"],\n"
        f"    \"instagram\": [\"Post 1 for Instagram\", \"Post 2 for Instagram\"],\n"
        f"    \"linkedin\": [\"Post 1 for LinkedIn\", \"Post 2 for LinkedIn\"]\n"
        f"  }},\n"
        f"  \"email_campaigns\": [\n"
        f"    {{ \"subject\": \"Email Subject 1\", \"content\": \"Email content 1\" }},\n"
        f"    {{ \"subject\": \"Email Subject 2\", \"content\": \"Email content 2\" }}\n"
        f"  ],\n"
        f"  \"hashtags\": [\"#hashtag1\", \"#hashtag2\", \"#hashtag3\"],\n"
        f"  \"influencer_briefs\": [\n"
        f"    {{ \"name\": \"Influencer Name 1\", \"brief\": \"Brief for influencer 1\" }},\n"
        f"    {{ \"name\": \"Influencer Name 2\", \"brief\": \"Brief for influencer 2\" }}\n"
        f"  ],\n"
        f"  \"press_release\": \"Full press release text here\",\n"
        f"  \"content_calendar\": [\n"
        f"    {{ \"date\": \"2024-01-01\", \"channel\": \"Social Media\", \"content\": \"Content for this date\" }},\n"
        f"    {{ \"date\": \"2024-01-02\", \"channel\": \"Email\", \"content\": \"Content for this date\" }}\n"
        f"  ]\n"
        f"}}\n\n"
        f"Generate 2-3 items for each array. Make content engaging and specific to the product. Return ONLY the JSON object."
    )
    state = await generate_with_retries_async(prompt, "marketing_content", state, max_retries=1)

    # Attempt to parse/normalize JSON to guarantee strict JSON downstream
    try:
        import json, re
        raw = state.get("marketing_content", "").strip()
        parsed = None
        
        # Try direct JSON parsing first
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON object if model added extra text
            # Look for JSON object between curly braces
            match = re.search(r'\{[\s\S]*\}', raw)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
            
            # If still no luck, try to find JSON after common prefixes
            if not parsed:
                for prefix in ['```json', '```', 'JSON:', 'Response:']:
                    if prefix in raw:
                        json_start = raw.find(prefix) + len(prefix)
                        json_text = raw[json_start:].strip()
                        match = re.search(r'\{[\s\S]*\}', json_text)
                        if match:
                            try:
                                parsed = json.loads(match.group(0))
                                break
                            except json.JSONDecodeError:
                                continue
        
        if isinstance(parsed, dict):
            # Store pretty-printed JSON for clients
            state["marketing_content"] = json.dumps(parsed, ensure_ascii=False, indent=2)
            # Also store the parsed object for potential future use
            state["marketing_content_json"] = parsed
        else:
            # If JSON parsing failed, create a fallback structure
            fallback_content = {
                "social_posts": {
                    "x": ["Failed to generate structured content. Please try again."],
                    "instagram": ["Failed to generate structured content. Please try again."],
                    "linkedin": ["Failed to generate structured content. Please try again."]
                },
                "email_campaigns": [{"subject": "Content Generation Error", "content": "Please regenerate the marketing content."}],
                "hashtags": ["#error", "#retry"],
                "influencer_briefs": [{"name": "Error", "brief": "Content generation failed. Please try again."}],
                "press_release": "Content generation failed. Please try again.",
                "content_calendar": [{"date": "N/A", "channel": "Error", "content": "Please regenerate content."}]
            }
            state["marketing_content"] = json.dumps(fallback_content, ensure_ascii=False, indent=2)
            state["marketing_content_json"] = fallback_content
            
    except Exception as e:
        # Complete fallback - create minimal valid JSON
        fallback_content = {
            "social_posts": {"x": ["Error"], "instagram": ["Error"], "linkedin": ["Error"]},
            "email_campaigns": [{"subject": "Error", "content": "Please try again"}],
            "hashtags": ["#error"],
            "influencer_briefs": [{"name": "Error", "brief": "Please try again"}],
            "press_release": "Please try again",
            "content_calendar": [{"date": "N/A", "channel": "Error", "content": "Please try again"}]
        }
        state["marketing_content"] = json.dumps(fallback_content, ensure_ascii=False, indent=2)
        state["marketing_content_json"] = fallback_content

    log_step(state, "marketing_content", state.get("marketing_content", ""))
    maybe_update_memory_summary(state)
    return state


async def parallel_phase_1(state: dict):
    """Execute product_description and pricing_strategy in parallel"""
    tasks = [
        product_description(state.copy()),
        pricing_strategy(state.copy())
    ]
    results = await asyncio.gather(*tasks)
    
    # Merge results back into the main state
    for result in results:
        for key, value in result.items():
            if key not in ['product_name', 'product_details', 'target_market', 'market_research']:
                state[key] = value
    
    return state


async def parallel_phase_2(state: dict):
    """Execute launch_plan and marketing_content in parallel"""
    tasks = [
        launch_plan(state.copy()),
        marketing_content(state.copy())
    ]
    results = await asyncio.gather(*tasks)
    
    # Merge results back into the main state
    for result in results:
        for key, value in result.items():
            if key not in ['product_name', 'product_details', 'target_market', 'market_research', 'product_description', 'pricing_strategy']:
                state[key] = value
    
    return state


def build_workflow():
    graph = StateGraph(dict)
    graph.add_node("market_research", market_research)
    graph.add_node("parallel_phase_1", parallel_phase_1)
    graph.add_node("parallel_phase_2", parallel_phase_2)

    graph.set_entry_point("market_research")

    def route_after_market_research(state: dict) -> str:
        quality = state.get("market_research_quality", "poor")
        mr_retries = state.get("_mr_retries", 0)
        max_mr_retries = 2
        if quality == "poor" and mr_retries < max_mr_retries:
            state["_mr_retries"] = mr_retries + 1
            state["_mr_query_hint"] = "broaden keywords and include competitor names"
            return "market_research"
        return "parallel_phase_1"

    graph.add_conditional_edges(
        "market_research",
        route_after_market_research,
        {"market_research": "market_research", "parallel_phase_1": "parallel_phase_1"}
    )

    graph.add_edge("parallel_phase_1", "parallel_phase_2")
    graph.add_edge("parallel_phase_2", END)

    return graph.compile()


