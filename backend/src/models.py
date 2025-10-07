from typing import Optional
from pydantic import BaseModel


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
    retries: Optional[dict] = None
    model_used: Optional[dict] = None
    market_research_quality: Optional[str] = None
    memory_summary: Optional[str] = None
    recent_events: Optional[list] = None


class RefineRequest(BaseModel):
    session_id: str
    refinement_instructions: str
    section_to_refine: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    created_at: str
    last_accessed: str
    history: list


