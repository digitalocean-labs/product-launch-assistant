import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, StringConstraints
from typing import Annotated
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from langchain_gradient import ChatGradient
from dotenv import load_dotenv
import requests
import json
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

# Get API keys from environment variables
DIGITALOCEAN_INFERENCE_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Quality thresholds (tweak for demos or production)
MARKET_RESEARCH_MIN_CHARS = 800

llm = ChatGradient(
    api_key=DIGITALOCEAN_INFERENCE_KEY,
    temperature=0.7,
    model="llama3.3-70b-instruct"
)

# Secondary model used as a fallback if generation fails or quality is poor
llm_fallback = ChatGradient(
    api_key=DIGITALOCEAN_INFERENCE_KEY,
    temperature=0.7,
    model="llama3.1-8b-instruct"
)

# Simple in-memory session storage (for demo - use Redis/DB in production)
session_store: Dict[str, Dict[str, Any]] = {}

class SessionManager:
    @staticmethod
    def create_session(initial_data: dict) -> str:
        session_id = str(uuid.uuid4())
        session_store[session_id] = {
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "data": initial_data,
            "history": []
        }
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[dict]:
        if session_id in session_store:
            session_store[session_id]["last_accessed"] = datetime.now()
            return session_store[session_id]
        return None
    
    @staticmethod
    def update_session(session_id: str, data: dict):
        if session_id in session_store:
            session_store[session_id]["data"].update(data)
            session_store[session_id]["last_accessed"] = datetime.now()
            session_store[session_id]["history"].append({
                "timestamp": datetime.now(),
                "action": "update",
                "data": data
            })
    
    @staticmethod
    def cleanup_old_sessions():
        """Remove sessions older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        to_remove = [sid for sid, session in session_store.items() 
                     if session["last_accessed"] < cutoff]
        for sid in to_remove:
            del session_store[sid]


# -------------------------
# Security & Safety Utilities
# -------------------------

class RedactSecretsFilter(logging.Filter):
    """Redacts known secrets from logs to prevent leakage."""
    def filter(self, record: logging.LogRecord) -> bool:
        redactions = {
            DIGITALOCEAN_INFERENCE_KEY or "": "[REDACTED]",
            SERPER_API_KEY or "": "[REDACTED]"
        }
        msg = str(record.getMessage())
        for secret, replacement in redactions.items():
            if secret:
                msg = msg.replace(secret, replacement)
        record.msg = msg
        return True


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        # HSTS only makes sense behind HTTPS; App Platform terminates TLS
        response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Very simple in-memory rate limiter per IP (MVP)."""
    requests_per_minute: int = 60
    _ip_to_hits: Dict[str, list] = {}

    async def dispatch(self, request: Request, call_next):
        from time import time
        now = time()
        window = 60.0
        client_ip = request.client.host if request.client else "unknown"
        hits = self._ip_to_hits.get(client_ip, [])
        # drop old
        hits = [t for t in hits if now - t < window]
        if len(hits) >= self.requests_per_minute:
            # Too many requests
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
        hits.append(now)
        self._ip_to_hits[client_ip] = hits
        return await call_next(request)


def sanitize_text(text: str) -> str:
    return text.strip()


def validate_request_inputs(product_name: str, product_details: str, target_market: str):
    """Basic input safety checks for length and disallowed content."""
    banned = [" malware ", " ransomware ", " exploit ", " bomb "]
    blob = f" {product_name} {product_details} {target_market} ".lower()
    if any(term in blob for term in banned):
        raise HTTPException(status_code=400, detail="Input appears to contain disallowed content.")


# Helper function for web search using Serper API
def web_search(query: str, max_results: int = 5) -> str:
    """
    Perform web search using Serper API and return summarized results
    """
    try:
        url = "https://google.serper.dev/search"
        payload = {
            "q": query,
            "num": max_results
        }
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract and format search results
            results = []
            if 'organic' in data:
                for result in data['organic'][:max_results]:
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    link = result.get('link', '')
                    results.append(f"• {title}\n  {snippet}\n  Source: {link}\n")
            
            # Add knowledge graph info if available
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                if 'description' in kg:
                    results.insert(0, f"📝 Overview: {kg['description']}\n")
            
            # Add answer box if available
            if 'answerBox' in data:
                answer = data['answerBox'].get('answer', '')
                if answer:
                    results.insert(0, f"💡 Quick Answer: {answer}\n")
            
            search_summary = f"🔍 Web Search Results for: {query}\n\n"
            search_summary += "\n".join(results[:max_results])
            
            return search_summary
        else:
            return f"⚠️ Search API error: {response.status_code} - {response.text}"
            
    except Exception as e:
        # Fallback to basic description if API fails
        return f"⚠️ Web search unavailable: {str(e)}. Using AI-only analysis."

# -------------------------
# Guardrails: Quality assessment and retry/fallback helpers
# -------------------------

def assess_quality(text: str, minimum_characters: int = MARKET_RESEARCH_MIN_CHARS) -> str:
    """Robust quality assessment for generated content.
    - Checks length, structure, and content quality indicators
    - Avoids false positives from legitimate content
    """
    blob = (text or "").strip()
    
    # Length check
    if len(blob) < minimum_characters:
        return "poor"
    
    # Check for explicit failure indicators (more specific than generic "error")
    failure_indicators = [
        "⚠️ generation failed",
        "generation failed after retries",
        "api error:",
        "search api error:",
        "web search unavailable:",
        "failed to generate",
        "unable to generate",
        "generation error:",
        "api unavailable"
    ]
    
    blob_lower = blob.lower()
    for indicator in failure_indicators:
        if indicator in blob_lower:
            return "poor"
    
    # Check for structural quality indicators
    # Good content should have multiple sections/points
    section_indicators = ["1.", "2.", "3.", "•", "-", "*", "##", "###"]
    has_structure = any(indicator in blob for indicator in section_indicators)
    
    # Check for substantive content (not just placeholders)
    placeholder_phrases = [
        "placeholder text",
        "sample content",
        "example text",
        "lorem ipsum",
        "to be filled",
        "coming soon"
    ]
    
    has_placeholders = any(phrase in blob_lower for phrase in placeholder_phrases)
    
    # Check for minimum word count (more reliable than character count for some content)
    word_count = len(blob.split())
    min_words = minimum_characters // 6  # Rough estimate: 6 chars per word
    
    # Quality assessment
    if has_placeholders:
        return "poor"
    
    if word_count < min_words:
        return "poor"
    
    # If it has good length, structure, and no failure indicators, consider it good
    if has_structure or word_count >= min_words * 1.5:
        return "good"
    
    # Default to good if it passes basic checks
    return "good"


def generate_with_retries(prompt: str, section_key: str, state: dict, max_retries: int = 2) -> dict:
    """Attempt generation with primary model, retry on failure, then fallback model.
    Tracks retry counts and which model ultimately produced the output.
    """
    retries = state.setdefault("retries", {})
    model_used = state.setdefault("model_used", {})
    attempts = 0
    backoff_seconds = 0.5

    # Try primary model with retries
    while attempts <= max_retries:
        try:
            content = llm.invoke(prompt).content
            state[section_key] = content
            model_used[section_key] = getattr(llm, "model", "primary")
            retries[section_key] = attempts
            return state
        except Exception as e:
            attempts += 1
            retries[section_key] = attempts
            time.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 2.0)

    # Fallback model
    try:
        content = llm_fallback.invoke(prompt).content
        state[section_key] = content
        model_used[section_key] = getattr(llm_fallback, "model", "fallback")
        return state
    except Exception:
        # Final failure; leave an explicit error note for observability
        state[section_key] = "⚠️ Generation failed after retries and fallback."
        model_used[section_key] = "failed"
        return state

# Helper function for creating Mermaid diagrams
def create_launch_timeline_diagram(launch_plan_text: str) -> str:
    """
    Generate a Mermaid diagram for launch timeline
    """
    diagram = """```mermaid
graph TD
    A[Pre-Launch Phase] --> B[Market Research]
    B --> C[Product Development]
    C --> D[Beta Testing]
    D --> E[Launch Phase]
    E --> F[Marketing Campaign]
    F --> G[Sales Launch]
    G --> H[Post-Launch Phase]
    H --> I[Customer Feedback]
    I --> J[Performance Analysis]
    J --> K[Optimization]
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style H fill:#e8f5e8
```"""
    
    return diagram

# Helper function to generate downloadable files
def generate_launch_files(state: dict) -> dict:
    """
    Generate downloadable launch materials
    """
    files = {}
    
    # Launch checklist
    checklist = f"""# {state['product_name']} Launch Checklist

## Pre-Launch (8 weeks before)
- [ ] Complete market research analysis
- [ ] Finalize product description and messaging
- [ ] Set pricing strategy
- [ ] Build landing page
- [ ] Create marketing materials
- [ ] Set up analytics tracking
- [ ] Prepare customer support resources

## Launch Week
- [ ] Execute marketing campaigns
- [ ] Monitor performance metrics
- [ ] Respond to customer feedback
- [ ] Track sales and conversions

## Post-Launch (8 weeks after)
- [ ] Analyze performance data
- [ ] Gather customer feedback
- [ ] Optimize based on learnings
- [ ] Plan next iteration

Generated on: {os.getcwd()}
"""
    files['launch_checklist.md'] = checklist
    
    # Marketing calendar
    calendar = f"""# {state['product_name']} Marketing Calendar

## Week 1-2: Pre-Launch Buzz
- Social media teasers
- Influencer outreach
- Email list building

## Week 3-4: Launch Preparation
- Press releases
- Partner announcements
- Final content creation

## Launch Week
- Launch announcement
- Social media campaigns
- Email marketing blast

## Post-Launch Weeks
- Customer testimonials
- Performance optimization
- Retargeting campaigns
"""
    files['marketing_calendar.md'] = calendar
    
    return files

# 1. Market Research (Enhanced with web search)
def market_research(state: dict):
    # Get live market data
    search_query = f"{state['product_name']} {state['target_market']} market trends competitors 2024"
    # Incorporate guard-provided query hint if present (improves subsequent attempts)
    query_hint = state.get("_mr_query_hint")
    if query_hint:
        search_query = f"{search_query} {query_hint}"
    web_data = web_search(search_query)
    
    # Enhanced AI analysis with web data
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
    return state

# 2. Product Description Generation
def product_description(state: dict):
    prompt = (
        f"Write a compelling e-commerce product description for '{state['product_name']}'. "
        f"Product details: {state['product_details']}. "
        f"Target market: {state['target_market']}."
    )
    state = generate_with_retries(prompt, "product_description", state, max_retries=1)
    return state

# 3. Pricing Strategy (Enhanced with web search)
def pricing_strategy(state: dict):
    # Get current pricing data
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
    return state

# 4. Launch Plan (Enhanced with diagram generation)
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
    
    # Generate timeline diagram
    timeline_diagram = create_launch_timeline_diagram(launch_text)
    
    # Combine text plan with visual timeline
    state['launch_plan'] = f"{launch_text}\n\n--- VISUAL TIMELINE ---\n{timeline_diagram}"
    return state

# 5. Marketing Content (Enhanced with web search)
def marketing_content(state: dict):
    # Get trending marketing data
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
    return state

# Build the LangGraph workflow with guards, fallbacks, and retries
graph = StateGraph(dict)
graph.add_node("market_research", market_research)
graph.add_node("product_description", product_description)
graph.add_node("pricing_strategy", pricing_strategy)
graph.add_node("launch_plan", launch_plan)
graph.add_node("marketing_content", marketing_content)

graph.set_entry_point("market_research")

# Guarded transition: if market research quality is poor and retries remain, loop back to re-run
def route_after_market_research(state: dict) -> str:
    quality = state.get("market_research_quality", "poor")
    mr_retries = state.get("_mr_retries", 0)
    max_mr_retries = 2  # Maximum retries for market research
    
    if quality == "poor" and mr_retries < max_mr_retries:
        # Increment retry counter and adjust query hint for future runs
        state["_mr_retries"] = mr_retries + 1
        state["_mr_query_hint"] = "broaden keywords and include competitor names"
        return "market_research"
    
    # If quality is good or max retries reached, proceed to next step
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

workflow = graph.compile()


class LaunchRequest(BaseModel):
    product_name: Optional[str] = None
    product_details: Optional[str] = None
    target_market: Optional[str] = None
    session_id: Optional[str] = None

class LaunchResponse(BaseModel):
    session_id: str
    product_name: str
    product_details: str
    target_market: str
    market_research: str
    product_description: str
    pricing_strategy: str
    launch_plan: str
    marketing_content: str
    downloadable_files: Optional[dict] = None
    created_at: Optional[str] = None
    last_updated: Optional[str] = None
    # Observability for demoing guards/fallbacks/retries
    retries: Optional[dict] = None
    model_used: Optional[dict] = None
    market_research_quality: Optional[str] = None

class RefineRequest(BaseModel):
    session_id: str
    refinement_instructions: str
    section_to_refine: str  # "market_research", "pricing_strategy", etc.

class SessionHistoryResponse(BaseModel):
    session_id: str
    created_at: str
    last_accessed: str
    history: list

# Create FastAPI app
app = FastAPI(
    title="Product Launch Assistant API",
    description="AI-powered product launch planning API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes - remove /api prefix since DigitalOcean handles routing
@app.post("/launch_assistant", response_model=LaunchResponse)
async def generate_launch_plan(request: LaunchRequest):
    """
    Generate a comprehensive product launch plan using AI with live web data.
    Supports session management for iterative refinement.
    
    This endpoint takes product information and returns:
    - Market research with live competitor analysis (via Serper API)
    - Product description optimization  
    - Pricing strategy with current market data (via Serper API)
    - Step-by-step launch plan with visual timelines
    - Marketing content with trending campaign insights (via Serper API)
    - Downloadable launch materials (checklists, calendars)
    - Session ID for future refinements
    """
    try:
        # Check if this is a new session or existing one
        if request.session_id:
            session = SessionManager.get_session(request.session_id)
            if session:
                # Return existing data
                data = session["data"]
                return LaunchResponse(
                    session_id=request.session_id,
                    product_name=data.get("product_name", ""),
                    product_details=data.get("product_details", ""),
                    target_market=data.get("target_market", ""),
                    market_research=data.get("market_research", ""),
                    product_description=data.get("product_description", ""),
                    pricing_strategy=data.get("pricing_strategy", ""),
                    launch_plan=data.get("launch_plan", ""),
                    marketing_content=data.get("marketing_content", ""),
                    downloadable_files=data.get("downloadable_files", {}),
                    created_at=session["created_at"].isoformat(),
                    last_updated=session["last_accessed"].isoformat(),
                    retries=data.get("retries"),
                    model_used=data.get("model_used"),
                    market_research_quality=data.get("market_research_quality")
                )
        
        # Generate new launch plan
        if not request.product_name or not request.product_details or not request.target_market:
            raise HTTPException(status_code=400, detail="Product name, details, and target market are required for new launch plans")
            
        # Validate and sanitize
        validate_request_inputs(request.product_name, request.product_details, request.target_market)
        
        state = {
            "product_name": sanitize_text(request.product_name),
            "product_details": sanitize_text(request.product_details),
            "target_market": sanitize_text(request.target_market),
            # guardrail controls
            "max_retries": 1,
            "retries": {},
            "model_used": {}
        }
        final_state = workflow.invoke(state)
        
        # Generate downloadable files
        downloadable_files = generate_launch_files(final_state)
        final_state["downloadable_files"] = downloadable_files
        
        # Create new session
        session_id = SessionManager.create_session(final_state)
        
        return LaunchResponse(
            session_id=session_id,
            product_name=final_state.get("product_name", ""),
            product_details=final_state.get("product_details", ""),
            target_market=final_state.get("target_market", ""),
            market_research=final_state.get("market_research", ""),
            product_description=final_state.get("product_description", ""),
            pricing_strategy=final_state.get("pricing_strategy", ""),
            launch_plan=final_state.get("launch_plan", ""),
            marketing_content=final_state.get("marketing_content", ""),
            downloadable_files=downloadable_files,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            retries=final_state.get("retries"),
            model_used=final_state.get("model_used"),
            market_research_quality=final_state.get("market_research_quality")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating launch plan: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Product Launch Assistant API is running",
        "version": "1.0.0"
    }

# Refinement endpoint for iterative improvements
@app.post("/refine", response_model=LaunchResponse)
async def refine_launch_plan(request: RefineRequest):
    """
    Refine a specific section of an existing launch plan based on user feedback.
    """
    try:
        session = SessionManager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        data = session["data"]
        
        # Create refinement prompt
        section_content = data.get(request.section_to_refine, "")
        refinement_prompt = (
            f"Here is the current {request.section_to_refine} for product '{data.get('product_name')}':\n\n"
            f"{section_content}\n\n"
            f"User feedback: {request.refinement_instructions}\n\n"
            f"Please provide an improved version that addresses the user's feedback while maintaining quality and coherence."
        )
        
        # Generate refined content
        refined_content = llm.invoke(refinement_prompt).content
        
        # Update the session data
        data[request.section_to_refine] = refined_content
        SessionManager.update_session(request.session_id, {request.section_to_refine: refined_content})
        
        # If files need regeneration
        if request.section_to_refine in ["launch_plan", "marketing_content"]:
            updated_files = generate_launch_files(data)
            data["downloadable_files"] = updated_files
            SessionManager.update_session(request.session_id, {"downloadable_files": updated_files})
        
        return LaunchResponse(
            session_id=request.session_id,
            product_name=data.get("product_name", ""),
            product_details=data.get("product_details", ""),
            target_market=data.get("target_market", ""),
            market_research=data.get("market_research", ""),
            product_description=data.get("product_description", ""),
            pricing_strategy=data.get("pricing_strategy", ""),
            launch_plan=data.get("launch_plan", ""),
            marketing_content=data.get("marketing_content", ""),
            downloadable_files=data.get("downloadable_files", {}),
            created_at=session["created_at"].isoformat(),
            last_updated=session["last_accessed"].isoformat(),
            retries=data.get("retries"),
            model_used=data.get("model_used"),
            market_research_quality=data.get("market_research_quality")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining launch plan: {str(e)}")

# Session history endpoint
@app.get("/session/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    """
    Get the history of changes for a specific session.
    """
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionHistoryResponse(
        session_id=session_id,
        created_at=session["created_at"].isoformat(),
        last_accessed=session["last_accessed"].isoformat(),
        history=session["history"]
    )

# Test web search endpoint
@app.get("/test-search")
async def test_search(query: str = "product launch strategies 2024"):
    """
    Test endpoint to verify Serper API integration
    """
    try:
        search_results = web_search(query, max_results=3)
        return {
            "status": "success",
            "query": query,
            "results": search_results,
            "serper_api_configured": bool(SERPER_API_KEY)
        }
    except Exception as e:
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "serper_api_configured": bool(SERPER_API_KEY)
        }

# Root endpoint for API information
@app.get("/")
async def root():
    return {
        "message": "Product Launch Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("🚀 Starting Product Launch Assistant API")
    print(f"🔧 API Docs: http://localhost:{port}/api/docs")
    print(f"❤️  Health: http://localhost:{port}/api/health")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    ) 