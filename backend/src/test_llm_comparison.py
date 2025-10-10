#!/usr/bin/env python3
"""
Comprehensive LLM comparison with automated evaluation criteria.
Compares market research results across different LLMs with scoring.

EVALUATION CRITERIA FRAMEWORK:
=============================

This module provides an automated, objective way to evaluate and compare LLM responses
for market research tasks. The evaluation is based on 6 key criteria with weighted scoring:

1. CONTENT QUALITY (25% weight) - Score: 0-10
   - Measures depth, accuracy, and comprehensiveness of the response
   - Looks for: Business insights, data-driven statements, strategic analysis
   - Bonus points for: Market metrics, specific company mentions, competitive analysis

2. STRUCTURE & CLARITY (15% weight) - Score: 0-10
   - Evaluates organization, formatting, and readability
   - Looks for: Clear sections, bullet points, logical flow, paragraph structure
   - Bonus points for: Organized headings, numbered lists, transition words

3. RELEVANCE (20% weight) - Score: 0-10
   - Assesses how well response addresses the specific product and target market
   - Looks for: Product name mentions, target market insights, industry-specific terms
   - Bonus points for: Demographic-specific analysis, tailored recommendations

4. ACTIONABILITY (20% weight) - Score: 0-10
   - Measures practical insights and actionable recommendations
   - Looks for: Action-oriented language, specific recommendations, concrete next steps
   - Bonus points for: Quantifiable insights, strategic advice, implementation guidance

5. COMPLETENESS (15% weight) - Score: 0-10
   - Evaluates coverage of key market research areas
   - Looks for: Competitors, trends, opportunities, market size, customer insights
   - Bonus points for: Challenges, geographic analysis, pricing insights

6. CONCISENESS (5% weight) - Score: 0-10
   - Assesses efficient use of words (optimal range: 150-400 words)
   - Penalizes responses that are too brief or overly verbose
   - Bonus/penalty for: Repetition, redundancy, information density

TOTAL SCORE: Weighted average of all criteria (0-10 scale)

USAGE:
======
# Run full comparison of all models:
python test_llm_comparison.py

# Quick comparison of specific models:
from test_llm_comparison import compare_models_quick
compare_models_quick(["llama3.3-70b-instruct", "openai-gpt-4o"])

# Evaluate a custom response:
evaluator = MarketResearchEvaluator("Product Name", "Target Market")
score = evaluator.evaluate_response("Your response text here")
print(score)
"""

import os
import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_gradient import ChatGradient
from .workflow import market_research

load_dotenv()

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
        return (
            self.content_quality * weights['content_quality'] +
            self.structure_clarity * weights['structure_clarity'] +
            self.relevance * weights['relevance'] +
            self.actionability * weights['actionability'] +
            self.completeness * weights['completeness'] +
            self.conciseness * weights['conciseness']
        )
    
    def __str__(self) -> str:
        return f"Total: {self.total_score:.2f}/10 | Quality: {self.content_quality:.1f} | Structure: {self.structure_clarity:.1f} | Relevance: {self.relevance:.1f} | Actionable: {self.actionability:.1f} | Complete: {self.completeness:.1f} | Concise: {self.conciseness:.1f}"

class MarketResearchEvaluator:
    """Automated evaluator for market research responses."""
    
    def __init__(self, product_name: str, target_market: str):
        self.product_name = product_name.lower()
        self.target_market = target_market.lower()
    
    def evaluate_response(self, response: str) -> EvaluationScore:
        """
        Evaluate a market research response across multiple criteria.
        
        Args:
            response: The LLM-generated market research text
            
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
        business_terms = ['market size', 'growth rate', 'revenue', 'profit', 'cagr', 
                         'market share', 'penetration', 'adoption rate', 'customer lifetime value']
        found_terms = sum(1 for term in business_terms if term in response_lower)
        score += min(found_terms * 0.3, 2.0)
        
        # Check for data-driven insights (+1)
        data_indicators = ['%', 'percent', 'million', 'billion', 'study shows', 'research indicates', 'according to']
        if any(indicator in response_lower for indicator in data_indicators):
            score += 1.0
        
        # Check for strategic insights (+1.5)
        strategic_terms = ['competitive advantage', 'differentiation', 'value proposition', 
                          'market positioning', 'brand positioning', 'unique selling']
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
        section_indicators = ['competitors:', 'competition:', 'trends:', 'opportunities:', 
                            'market trends:', 'key players:', 'analysis:', 'overview:']
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
        if 'water bottle' in self.product_name or 'bottle' in self.product_name:
            industry_terms = ['hydration', 'beverage', 'reusable', 'sustainable', 'eco-friendly', 'bpa-free']
            found = sum(1 for term in industry_terms if term in response_lower)
            score += min(found * 0.3, 2.0)
        
        # Demographic-specific insights (+1)
        if 'millennials' in self.target_market:
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
            'competitors': ['competitor', 'competition', 'rival', 'alternative'],
            'market_trends': ['trend', 'growth', 'emerging', 'shift', 'demand'],
            'opportunities': ['opportunity', 'gap', 'potential', 'untapped'],
            'market_size': ['market size', 'market value', 'industry worth', 'billion', 'million'],
            'customer_insights': ['customer', 'consumer', 'user', 'buyer', 'audience'],
            'challenges': ['challenge', 'barrier', 'obstacle', 'risk', 'threat'],
            'geographic': ['region', 'global', 'local', 'geographic', 'market penetration'],
            'pricing': ['price', 'pricing', 'cost', 'affordable', 'premium', 'budget']
        }
        
        for component, keywords in components.items():
            if any(keyword in response_lower for keyword in keywords):
                score += 1.0
        
        return min(score, 10.0)
    
    def _evaluate_conciseness(self, response: str, response_lower: str) -> float:
        """Evaluate efficient use of words - not too verbose or too brief."""
        word_count = len(response.split())
        
        # Optimal range: 150-400 words for market research
        if 150 <= word_count <= 400:
            score = 10.0
        elif 100 <= word_count < 150 or 400 < word_count <= 500:
            score = 8.0
        elif 50 <= word_count < 100 or 500 < word_count <= 600:
            score = 6.0
        elif 25 <= word_count < 50 or 600 < word_count <= 800:
            score = 4.0
        else:
            score = 2.0
        
        # Penalty for excessive repetition (-1)
        sentences = response.split('.')
        if len(sentences) > 5:
            unique_sentences = set(sentences)
            repetition_ratio = len(unique_sentences) / len(sentences)
            if repetition_ratio < 0.8:
                score -= 1.0
        
        return max(score, 0.0)

async def test_market_research_with_llms(llm_models):
    """
    Test market research function with different LLM models and evaluate responses.
    
    Args:
        llm_models: List of model names to test
    """
    
    # Test data
    test_state = {
        'product_name': 'EcoSmart Water Bottle',
        'target_market': 'environmentally conscious millennials'
    }
    
    api_key = os.getenv("DIGITALOCEAN_INFERENCE_KEY")
    if not api_key:
        print("❌ DIGITALOCEAN_INFERENCE_KEY not found in environment variables")
        print("Please set your API key in a .env file or environment variable")
        return
    
    # Initialize evaluator
    evaluator = MarketResearchEvaluator(
        product_name=test_state['product_name'],
        target_market=test_state['target_market']
    )
    
    results = []
    
    print("🚀 Testing Market Research with Different LLMs + Automated Evaluation")
    print("=" * 80)
    
    for i, model_name in enumerate(llm_models, 1):
        print(f"\n[{i}/{len(llm_models)}] Testing {model_name}")
        print("🔹" * 60)
        
        try:
            # Create LLM instance for this model
            llm = ChatGradient(
                api_key=api_key,
                temperature=0.7,
                model=model_name
            )
            
            # Temporarily replace the global llm in config module
            from . import config
            original_llm = config.llm
            config.llm = llm
            
            # Run market research (async function)
            result_state = await market_research(test_state.copy())
            response = result_state['market_research']
            
            # Evaluate the response
            score = evaluator.evaluate_response(response)
            
            # Store results for final comparison
            results.append({
                'model': model_name,
                'response': response,
                'score': score,
                'word_count': len(response.split())
            })
            
            # Print the response with evaluation
            print(f"📝 Response ({len(response.split())} words):")
            print("-" * 40)
            print(response)
            print("-" * 40)
            print(f"📊 Evaluation: {score}")
            print("")
            
            # Restore original llm
            config.llm = original_llm
            
        except Exception as e:
            print(f"❌ Error with {model_name}: {str(e)}")
            results.append({
                'model': model_name,
                'response': None,
                'score': None,
                'error': str(e)
            })
    
    # Generate final comparison report
    print("\n" + "=" * 80)
    print("🏆 FINAL EVALUATION REPORT")
    print("=" * 80)
    
    # Sort by total score (highest first)
    valid_results = [r for r in results if r['score'] is not None]
    valid_results.sort(key=lambda x: x['score'].total_score, reverse=True)
    
    if valid_results:
        print(f"\n🥇 RANKING (Total Score out of 10.0):")
        print("-" * 50)
        for rank, result in enumerate(valid_results, 1):
            score = result['score']
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
            print(f"{medal} {result['model']:<25} | {score.total_score:.2f}/10.0")
        
        # Detailed breakdown for top performer
        best_result = valid_results[0]
        best_score = best_result['score']
        print(f"\n🎯 DETAILED BREAKDOWN - WINNER: {best_result['model']}")
        print("-" * 50)
        print(f"Content Quality:    {best_score.content_quality:.1f}/10.0")
        print(f"Structure & Clarity: {best_score.structure_clarity:.1f}/10.0")
        print(f"Relevance:          {best_score.relevance:.1f}/10.0")
        print(f"Actionability:      {best_score.actionability:.1f}/10.0")
        print(f"Completeness:       {best_score.completeness:.1f}/10.0")
        print(f"Conciseness:        {best_score.conciseness:.1f}/10.0")
        print(f"Word Count:         {best_result['word_count']} words")
        
        # Category winners
        print(f"\n🏅 CATEGORY WINNERS:")
        print("-" * 30)
        categories = ['content_quality', 'structure_clarity', 'relevance', 'actionability', 'completeness', 'conciseness']
        category_names = ['Content Quality', 'Structure & Clarity', 'Relevance', 'Actionability', 'Completeness', 'Conciseness']
        
        for cat, name in zip(categories, category_names):
            best_in_category = max(valid_results, key=lambda x: getattr(x['score'], cat))
            print(f"{name:<18}: {best_in_category['model']} ({getattr(best_in_category['score'], cat):.1f}/10.0)")
    
    # Error summary
    error_results = [r for r in results if 'error' in r]
    if error_results:
        print(f"\n❌ ERRORS ENCOUNTERED:")
        print("-" * 30)
        for result in error_results:
            print(f"{result['model']}: {result['error']}")
    
    print(f"\n✨ Evaluation complete! Tested {len(llm_models)} models.")
    
    return results

def save_evaluation_results(results: List[Dict], filename: str = "llm_evaluation_results.json"):
    """
    Save evaluation results to a JSON file for further analysis.
    
    Args:
        results: List of evaluation results from test_market_research_with_llms
        filename: Output filename for the JSON report
    """
    # Convert results to JSON-serializable format
    json_results = []
    for result in results:
        json_result = {
            'model': result['model'],
            'response': result['response'],
            'word_count': result.get('word_count', 0)
        }
        
        if 'error' in result:
            json_result['error'] = result['error']
        elif result['score']:
            score = result['score']
            json_result['scores'] = {
                'total_score': round(score.total_score, 2),
                'content_quality': round(score.content_quality, 2),
                'structure_clarity': round(score.structure_clarity, 2),
                'relevance': round(score.relevance, 2),
                'actionability': round(score.actionability, 2),
                'completeness': round(score.completeness, 2),
                'conciseness': round(score.conciseness, 2)
            }
        
        json_results.append(json_result)
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': str(os.popen('date').read().strip()),
            'test_product': 'EcoSmart Water Bottle',
            'test_target_market': 'environmentally conscious millennials',
            'evaluation_criteria': {
                'content_quality': 'Depth, accuracy, and comprehensiveness (25% weight)',
                'structure_clarity': 'Organization and readability (15% weight)',
                'relevance': 'Product/market specific insights (20% weight)',
                'actionability': 'Practical recommendations (20% weight)',
                'completeness': 'Coverage of market research areas (15% weight)',
                'conciseness': 'Optimal word usage (5% weight)'
            },
            'results': json_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Evaluation results saved to: {filename}")

async def compare_models_quick(models: List[str] = None):
    """
    Quick comparison function for testing specific models.
    
    Args:
        models: List of model names to compare (defaults to top 2 models)
    """
    if models is None:
        models = ["llama3.3-70b-instruct", "openai-gpt-4o"]
    
    print(f"🚀 Quick Model Comparison: {' vs '.join(models)}")
    results = await test_market_research_with_llms(models)
    
    if results:
        # Save results with timestamp
        timestamp = str(int(os.popen('date +%s').read().strip()))
        filename = f"quick_comparison_{timestamp}.json"
        save_evaluation_results(results, filename)
    
    return results

async def main():
    # Available models on DigitalOcean's Gradient platform
    models_to_test = [
        "llama3.3-70b-instruct",
        "openai-gpt-4o", 
        "openai-gpt-oss-20b",
        "deepseek-r1-distill-llama-70b"
    ]
    
    # Run comprehensive evaluation
    results = await test_market_research_with_llms(models_to_test)
    
    # Save detailed results for analysis
    if results:
        save_evaluation_results(results, "market_research_evaluation.json")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
