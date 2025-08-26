import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from langgraph.graph import StateGraph, END
from langchain_gradient import ChatGradient
from dotenv import load_dotenv

load_dotenv()

# Set your Gradient API key as an environment variable
DIGITALOCEAN_INFERENCE_KEY = os.getenv("DIGITALOCEAN_INFERENCE_KEY")

llm = ChatGradient(
    api_key=DIGITALOCEAN_INFERENCE_KEY,
    temperature=0.7,
    model="llama3.3-70b-instruct"
)

# 1. Market Research
def market_research(state: dict):
    prompt = (
        f"Conduct a brief market research for a product named '{state['product_name']}' targeting '{state['target_market']}'. "
        f"Summarize key competitors, market trends, and potential opportunities."
    )
    state['market_research'] = llm.invoke(prompt).content
    return state

# 2. Product Description Generation
def product_description(state: dict):
    prompt = (
        f"Write a compelling e-commerce product description for '{state['product_name']}'. "
        f"Product details: {state['product_details']}. "
        f"Target market: {state['target_market']}."
    )
    state['product_description'] = llm.invoke(prompt).content
    return state

# 3. Pricing Strategy Suggestion
def pricing_strategy(state: dict):
    prompt = (
        f"Based on the following market research and product details, suggest a pricing strategy for '{state['product_name']}':\n"
        f"Market research: {state['market_research']}\n"
        f"Product details: {state['product_details']}"
    )
    state['pricing_strategy'] = llm.invoke(prompt).content
    return state

# 4. Launch Plan Creation
def launch_plan(state: dict):
    prompt = (
        f"Create a step-by-step launch plan for '{state['product_name']}' targeting '{state['target_market']}'. "
        f"Include pre-launch, launch, and post-launch activities."
    )
    state['launch_plan'] = llm.invoke(prompt).content
    return state

# 5. Marketing Content Generation
def marketing_content(state: dict):
    prompt = (
        f"Generate:\n"
        f"1. A social media post (Twitter/X style, max 280 characters)\n"
        f"2. An email announcement (max 150 words)\n"
        f"For the product '{state['product_name']}'. Use the following product description:\n"
        f"{state['product_description']}"
    )
    state['marketing_content'] = llm.invoke(prompt).content
    return state

# Build the LangGraph workflow
graph = StateGraph(dict)
graph.add_node("market_research", market_research)
graph.add_node("product_description", product_description)
graph.add_node("pricing_strategy", pricing_strategy)
graph.add_node("launch_plan", launch_plan)
graph.add_node("marketing_content", marketing_content)

graph.set_entry_point("market_research")
graph.add_edge("market_research", "product_description")
graph.add_edge("product_description", "pricing_strategy")
graph.add_edge("pricing_strategy", "launch_plan")
graph.add_edge("launch_plan", "marketing_content")
graph.add_edge("marketing_content", END)
workflow = graph.compile()


class LaunchRequest(BaseModel):
    product_name: str
    product_details: str
    target_market: str

class LaunchResponse(BaseModel):
    product_name: str
    product_details: str
    target_market: str
    market_research: str
    product_description: str
    pricing_strategy: str
    launch_plan: str
    marketing_content: str

# Create FastAPI app
app = FastAPI(
    title="Product Launch Assistant API",
    description="AI-powered product launch planning API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# No CORS configuration needed - both frontend and backend deployed on same domain

# API Routes - remove /api prefix since DigitalOcean handles routing
@app.post("/launch_assistant", response_model=LaunchResponse)
async def generate_launch_plan(request: LaunchRequest):
    """
    Generate a comprehensive product launch plan using AI.
    
    This endpoint takes product information and returns:
    - Market research and competitor analysis
    - Product description optimization  
    - Pricing strategy recommendations
    - Step-by-step launch plan with timelines
    - Marketing content and social media campaigns
    """
    try:
        state = {
            "product_name": request.product_name,
            "product_details": request.product_details,
            "target_market": request.target_market
        }
        final_state = workflow.invoke(state)
        return LaunchResponse(
            product_name=final_state.get("product_name", ""),
            product_details=final_state.get("product_details", ""),
            target_market=final_state.get("target_market", ""),
            market_research=final_state.get("market_research", ""),
            product_description=final_state.get("product_description", ""),
            pricing_strategy=final_state.get("pricing_strategy", ""),
            launch_plan=final_state.get("launch_plan", ""),
            marketing_content=final_state.get("marketing_content", "")
        )
        
        return response
        
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