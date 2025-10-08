"""
Agent evaluation module with LangSmith tracing.
Provides automated scoring for agent outputs across multiple criteria.
"""

import os
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from langsmith import Client

# Initialize LangSmith client
langsmith_client = None
langsmith_api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
if langsmith_api_key:
    try:
        langsmith_client = Client(api_key=langsmith_api_key)
        print("✅ LangSmith client initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize LangSmith client: {e}")
        langsmith_client = None
else:
    print("ℹ️  LangSmith API key not found. Tracing will be disabled.")

# TruLens support removed. Using LangSmith only.

@dataclass
class EvaluationScore:
    """Data class to hold evaluation scores for a model response."""
    content_quality: float  # 0-10: Depth, accuracy, and comprehensiveness
    structure_clarity: float  # 0-10: Organization and readability
    relevance: float  # 0-10: How well it addresses the specific product/market
    actionability: float  # 0-10: Practical insights and recommendations
    completeness: float  # 0-10: Coverage of key market research areas
    conciseness: float  # 0-10: Efficient use of words (not too verbose/brief)
    
    @property
    def total_score(self) -> float:
        """Calculate weighted total score."""
        weights = {
            'content_quality': 0.25,
            'structure_clarity': 0.15, 
            'relevance': 0.20,
            'actionability': 0.20,
            'completeness': 0.15,
            'conciseness': 0.05
        }
        base_score = (
            self.content_quality * weights['content_quality'] +
            self.structure_clarity * weights['structure_clarity'] +
            self.relevance * weights['relevance'] +
            self.actionability * weights['actionability'] +
            self.completeness * weights['completeness'] +
            self.conciseness * weights['conciseness']
        )
        return min(base_score, 10.0)
    
    def __str__(self) -> str:
        scores = f"Total: {self.total_score:.2f}/10 | Quality: {self.content_quality:.1f} | Structure: {self.structure_clarity:.1f} | Relevance: {self.relevance:.1f} | Actionable: {self.actionability:.1f} | Complete: {self.completeness:.1f} | Concise: {self.conciseness:.1f}"
        return scores


class MarketResearchEvaluator:
    """Automated evaluator for market research responses."""
    
    def __init__(self, product_name: str, target_market: str):
        self.product_name = product_name.lower()
        self.target_market = target_market.lower()
        # TruLens feedback removed.
    
    def evaluate_response(self, response: str, context: str = "") -> EvaluationScore:
        """
        Evaluate a market research response across multiple criteria.
        
        Args:
            response: The LLM-generated market research text
            context: Additional context for TruLens evaluation
            
        Returns:
            EvaluationScore with detailed scoring
        """
        response_lower = response.lower()
        
        # 1. Content Quality (0-10)
        content_quality = self._evaluate_content_quality(response, response_lower)
        
        # 2. Structure & Clarity (0-10)
        structure_clarity = self._evaluate_structure_clarity(response, response_lower)
        
        # 3. Relevance (0-10)
        relevance = self._evaluate_relevance(response, response_lower)
        
        # 4. Actionability (0-10) 
        actionability = self._evaluate_actionability(response, response_lower)
        
        # 5. Completeness (0-10)
        completeness = self._evaluate_completeness(response, response_lower)
        
        # 6. Conciseness (0-10)
        conciseness = self._evaluate_conciseness(response, response_lower)
        
        return EvaluationScore(
            content_quality=content_quality,
            structure_clarity=structure_clarity,
            relevance=relevance,
            actionability=actionability,
            completeness=completeness,
            conciseness=conciseness
        )
    
    def _evaluate_content_quality(self, response: str, response_lower: str) -> float:
        """Evaluate depth, accuracy, and comprehensiveness of content."""
        score = 5.0  # Base score
        
        # Check for specific business insights (up to +3)
        business_terms = ['market share', 'penetration', 'adoption rate', 'customer lifetime value']
        found_terms = sum(1 for term in business_terms if term in response_lower)
        score += min(found_terms * 0.3, 2.0)
        
        # Check for data-driven insights (+1)
        data_indicators = ['%', 'percent', 'million', 'billion', 'study shows', 'research indicates', 'according to']
        if any(indicator in response_lower for indicator in data_indicators):
            score += 1.0
        
        # Check for strategic insights (+1.5)
        strategic_terms = ['competitive advantage', 'market positioning', 'brand positioning', 'unique selling']
        if any(term in response_lower for term in strategic_terms):
            score += 1.5
        
        # Check for specific company/brand mentions (+0.5)
        if len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', response)) >= 3:
            score += 0.5
        
        return min(score, 10.0)
    
    def _evaluate_structure_clarity(self, response: str, response_lower: str) -> float:
        """Evaluate organization, formatting, and readability."""
        score = 5.0  # Base score
        
        # Check for clear sections/organization (+2)
        section_indicators = ['market overview:', 'key players:', 'market trends:', 'analysis:', 'overview:']
        sections_found = sum(1 for indicator in section_indicators if indicator in response_lower)
        score += min(sections_found * 0.5, 2.0)
        
        # Check for bullet points or numbered lists (+1.5)
        if ('•' in response or '*' in response or 
            len(re.findall(r'^\d+\.', response, re.MULTILINE)) >= 2):
            score += 1.5
        
        # Check for paragraph structure (+1)
        paragraphs = response.split('\n\n')
        if len(paragraphs) >= 3:
            score += 1.0
        
        # Check for logical flow keywords (+0.5)
        flow_words = ['however', 'therefore', 'additionally', 'furthermore', 'in contrast', 'meanwhile']
        if any(word in response_lower for word in flow_words):
            score += 0.5
        
        return min(score, 10.0)
    
    def _evaluate_relevance(self, response: str, response_lower: str) -> float:
        """Evaluate how well response addresses specific product and target market."""
        score = 3.0  # Base score
        
        # Product name mentioned (+2)
        if self.product_name in response_lower:
            score += 2.0
        
        # Target market mentioned (+2)  
        target_words = self.target_market.split()
        target_mentions = sum(1 for word in target_words if word in response_lower)
        score += min(target_mentions * 0.5, 2.0)
        
        # Industry-specific terms (+2)
        # This could be made more dynamic based on product type
        industry_terms = ['hydration', 'beverage', 'reusable', 'sustainable', 'eco-friendly', 'bpa-free']
        found = sum(1 for term in industry_terms if term in response_lower)
        score += min(found * 0.3, 2.0)
        
        # Demographic-specific insights (+1)
        if 'target market' in response_lower or 'target audience' in response_lower:
            demo_terms = ['social media', 'sustainability', 'convenience', 'wellness', 'fitness']
            if any(term in response_lower for term in demo_terms):
                score += 1.0
        
        return min(score, 10.0)
    
    def _evaluate_actionability(self, response: str, response_lower: str) -> float:
        """Evaluate practical insights and recommendations."""
        score = 4.0  # Base score
        
        # Action-oriented language (+2)
        action_words = ['should', 'recommend', 'suggest', 'consider', 'focus on', 'target', 'leverage']
        action_count = sum(1 for word in action_words if word in response_lower)
        score += min(action_count * 0.3, 2.0)
        
        # Specific recommendations (+2)
        recommendation_phrases = ['opportunity to', 'potential for', 'could benefit', 'strategy should']
        if any(phrase in response_lower for phrase in recommendation_phrases):
            score += 2.0
        
        # Concrete next steps (+1.5)
        concrete_terms = ['launch', 'price', 'position', 'market', 'partner', 'develop', 'create']
        concrete_count = sum(1 for term in concrete_terms if term in response_lower)
        score += min(concrete_count * 0.2, 1.5)
        
        # Quantifiable insights (+0.5)
        if any(char in response for char in ['$', '%', '€', '£']):
            score += 0.5
        
        return min(score, 10.0)
    
    def _evaluate_completeness(self, response: str, response_lower: str) -> float:
        """Evaluate coverage of key market research areas."""
        score = 2.0  # Base score
        
        # Core market research components (up to +8)
        components = {
            'competitors': ['competitor', 'rival', 'competition', 'market leader'],
            'trends': ['trend', 'growing', 'emerging', 'shifting'],
            'opportunities': ['opportunity', 'potential', 'gap', 'untapped'],
            'market_size': ['market size', 'market value', 'revenue', 'billion', 'million'],
            'customer_insights': ['customer', 'consumer', 'buyer', 'demographic'],
            'challenges': ['challenge', 'barrier', 'obstacle', 'risk'],
            'geographic': ['region', 'country', 'global', 'local', 'geographic'],
            'pricing': ['price', 'cost', 'pricing', 'affordable', 'premium']
        }
        
        for component, keywords in components.items():
            if any(keyword in response_lower for keyword in keywords):
                score += 1.0
        
        return min(score, 10.0)
    
    def _evaluate_conciseness(self, response: str, response_lower: str) -> float:
        """Evaluate efficient use of words (optimal range: 150-400 words)."""
        word_count = len(response.split())
        
        # Optimal range: 150-400 words
        if 150 <= word_count <= 400:
            return 10.0
        elif 100 <= word_count < 150:
            return 7.0
        elif 400 < word_count <= 600:
            return 7.0
        elif 50 <= word_count < 100:
            return 4.0
        elif 600 < word_count <= 800:
            return 4.0
        else:
            return 2.0


def log_evaluation_to_langsmith(run_id: str, evaluation_score: EvaluationScore, 
                               product_name: str, target_market: str) -> None:
    """Log evaluation results to LangSmith for tracking and analysis."""
    if not langsmith_client:
        return
        
    try:
        # Create feedback for the run
        langsmith_client.create_feedback(
            run_id=run_id,
            key="total_score",
            score=evaluation_score.total_score,
            value=evaluation_score.total_score
        )
        
        # Log individual component scores
        langsmith_client.create_feedback(
            run_id=run_id,
            key="content_quality",
            score=evaluation_score.content_quality,
            value=evaluation_score.content_quality
        )
        
        langsmith_client.create_feedback(
            run_id=run_id,
            key="relevance",
            score=evaluation_score.relevance,
            value=evaluation_score.relevance
        )
        
        # TruLens metrics removed
            
    except Exception as e:
        print(f"Warning: Failed to log evaluation to LangSmith: {e}")


def evaluate_agent_output(output: str, product_name: str, target_market: str, 
                         context: str = "", run_id: str = None) -> EvaluationScore:
    """
    Evaluate agent output with comprehensive scoring.
    
    Args:
        output: The agent-generated output to evaluate
        product_name: Product name for context
        target_market: Target market for context
        context: Additional context (unused placeholder)
        run_id: LangSmith run ID for logging
        
    Returns:
        EvaluationScore with all metrics
    """
    evaluator = MarketResearchEvaluator(product_name, target_market)
    score = evaluator.evaluate_response(output, context)
    
    # Log to LangSmith if run_id provided
    if run_id:
        log_evaluation_to_langsmith(run_id, score, product_name, target_market)
    
    return score
