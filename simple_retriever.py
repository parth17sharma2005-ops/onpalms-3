import requests
import json
from typing import List, Dict
from bs4 import BeautifulSoup
import re
import time

class SimpleRAG:
    def __init__(self):
        """Initialize simple RAG without vector database"""
        self.content_cache = {}
        self.last_fetch = 0
        self.fetch_interval = 3600  # Refetch every hour
    
    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and extract meaningful text"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def fetch_wordpress_content(self) -> Dict[str, str]:
        """Fetch and cache WordPress content"""
        current_time = time.time()
        
        # Return cached content if recent
        if self.content_cache and (current_time - self.last_fetch) < self.fetch_interval:
            return self.content_cache
        
        print("🔄 Fetching fresh WordPress content...")
        
        urls = [
            "https://www.onpalms.com/wp-json/wp/v2/pages?per_page=100",
            "https://www.onpalms.com/wp-json/wp/v2/posts?per_page=100"
        ]
        
        all_content = {}
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                content_type = "pages" if "pages" in url else "posts"
                
                for item in data:
                    title = self.clean_html_content(item.get("title", {}).get("rendered", ""))
                    content = self.clean_html_content(item.get("content", {}).get("rendered", ""))
                    excerpt = self.clean_html_content(item.get("excerpt", {}).get("rendered", ""))
                    
                    full_text = f"{title}\n{excerpt}\n{content}".strip()
                    
                    if full_text and len(full_text) > 50:
                        key = f"{content_type}_{item['id']}_{title[:30]}"
                        all_content[key] = full_text
                
                print(f"✅ Fetched {len(data)} {content_type}")
                time.sleep(0.5)  # Be respectful
                
            except Exception as e:
                print(f"❌ Error fetching {url}: {str(e)}")
                continue
        
        self.content_cache = all_content
        self.last_fetch = current_time
        
        print(f"✅ Cached {len(all_content)} content pieces")
        return all_content
    
    def simple_search(self, query: str, n_results: int = 5) -> List[str]:
        """Simple keyword-based search"""
        content = self.fetch_wordpress_content()
        
        if not content:
            return ["PALMS™ is a comprehensive warehouse management system designed to optimize your operations."]
        
        query_lower = query.lower()
        scored_results = []
        
        for key, text in content.items():
            text_lower = text.lower()
            
            # Simple scoring based on keyword matches
            score = 0
            
            # Score based on query words appearing in content
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    score += text_lower.count(word) * len(word)
            
            # Boost score if words appear in title area (first 100 chars)
            title_area = text_lower[:100]
            for word in query_words:
                if len(word) > 2 and word in title_area:
                    score += 10
            
            if score > 0:
                scored_results.append((score, text))
        
        # Sort by score and return top results
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        results = [text for score, text in scored_results[:n_results]]
        
        # If no good matches, return some general content
        if not results and content:
            results = list(content.values())[:n_results]
        
        return results

# Global instance
simple_rag = SimpleRAG()

def retrieve(query: str, n_results: int = 5) -> List[str]:
    """Retrieve function for backward compatibility"""
    return simple_rag.simple_search(query, n_results)

if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Simple RAG System...")
    
    test_queries = [
        "warehouse management",
        "PALMS features", 
        "inventory management"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        results = retrieve(query, 3)
        print(f"📄 Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            preview = result[:150] + "..." if len(result) > 150 else result
            print(f"  {i}. {preview}")
