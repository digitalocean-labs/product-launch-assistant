import json
import requests
from .config import SERPER_API_KEY


def web_search(query: str, max_results: int = 5) -> str:
    try:
        url = "https://google.serper.dev/search"
        payload = {"q": query, "num": max_results}
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            data = response.json()
            results = []
            if 'organic' in data:
                for result in data['organic'][:max_results]:
                    title = result.get('title', '')
                    snippet = result.get('snippet', '')
                    link = result.get('link', '')
                    results.append(f"• {title}\n  {snippet}\n  Source: {link}\n")
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                if 'description' in kg:
                    results.insert(0, f"📝 Overview: {kg['description']}\n")
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
        return f"⚠️ Web search unavailable: {str(e)}. Using AI-only analysis."


