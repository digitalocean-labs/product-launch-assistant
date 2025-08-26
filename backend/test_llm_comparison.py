#!/usr/bin/env python3
"""
Simple test to compare market research results across different LLMs.
Pass an array of LLM models and get printed responses for comparison.
"""

import os
from dotenv import load_dotenv
from langchain_gradient import ChatGradient
from main import market_research

load_dotenv()

def test_market_research_with_llms(llm_models):
    """
    Test market research function with different LLM models.
    
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
    
    print("🚀 Testing Market Research with Different LLMs")
    
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
            
            # Temporarily replace the global llm in main module
            import main
            original_llm = main.llm
            main.llm = llm
            
            # Run market research
            result_state = market_research(test_state.copy())
            response = result_state['market_research']
            
            # Print the response
            print(response)
            
            # Restore original llm
            main.llm = original_llm
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print(f"\n✨ Comparison complete!")


if __name__ == "__main__":
    # Available models on DigitalOcean's Gradient platform
    models_to_test = [
        "llama3.3-70b-instruct",
        "llama3.1-70b-instruct", 
        "llama3.1-8b-instruct",
        "mixtral-8x7b-instruct"
    ]
    
    # You can modify this list to test specific models
    # For example: models_to_test = ["llama3.1-8b-instruct", "llama3.3-70b-instruct"]
    
    test_market_research_with_llms(models_to_test)
