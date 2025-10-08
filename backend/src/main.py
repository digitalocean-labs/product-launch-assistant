import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import SERPER_API_KEY
from .models import LaunchRequest, LaunchResponse, SessionHistoryResponse
from .sessions import SessionManager
from .security import SecurityHeadersMiddleware, RateLimiterMiddleware
from .utils import sanitize_text, validate_request_inputs
from .files import generate_launch_files
from .workflow import build_workflow
# Removed refine flow: no longer need generation or memory helpers here

workflow = build_workflow()


app = FastAPI(
    title="Product Launch Assistant API",
    description="AI-powered product launch planning API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)


@app.post("/launch_assistant", response_model=LaunchResponse)
async def generate_launch_plan(request: LaunchRequest):
    try:
        if request.session_id:
            session = SessionManager.get_session(request.session_id)
            if session:
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
                    market_research_quality=data.get("market_research_quality"),
                    memory_summary=data.get("memory_summary"),
                    recent_events=data.get("recent_events")
                )
        if not request.product_name or not request.product_details or not request.target_market:
            raise HTTPException(status_code=400, detail="Product name, details, and target market are required for new launch plans")
        validate_request_inputs(request.product_name, request.product_details, request.target_market)
        state = {
            "product_name": sanitize_text(request.product_name),
            "product_details": sanitize_text(request.product_details),
            "target_market": sanitize_text(request.target_market),
            "max_retries": 1,
            "retries": {},
            "model_used": {}
        }
        final_state = await workflow.ainvoke(state)
        downloadable_files = generate_launch_files(final_state)
        final_state["downloadable_files"] = downloadable_files
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
            market_research_quality=final_state.get("market_research_quality"),
            memory_summary=final_state.get("memory_summary"),
            recent_events=final_state.get("recent_events")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating launch plan: {str(e)}")


@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Product Launch Assistant API is running",
        "version": "1.0.0"
    }


@app.get("/session/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str):
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionHistoryResponse(
        session_id=session_id,
        created_at=session["created_at"].isoformat(),
        last_accessed=session["last_accessed"].isoformat(),
        history=session["history"]
    )

@app.get("/test-search")
async def test_search(query: str = "product launch strategies 2024"):
    try:
        from .search import web_search
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
    print(f"🔧 API Docs: http://localhost:{port}/docs")
    print(f"❤️  Health: http://localhost:{port}/health")
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    ) 