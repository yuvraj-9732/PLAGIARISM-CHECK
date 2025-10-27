import time
from ddgs import DDGS
from typing import List, Dict

class WebSearchEngine:
    def __init__(self, config):
        self.config = config
        self.ddgs = DDGS()
        self.last_request_time = 0
    
    def search(self, query: str, num_results: int = None) -> List[Dict]:
        """Search the web using DuckDuckGo"""
        if num_results is None:
            num_results = self.config['SEARCH_RESULTS_PER_QUERY']
        
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.config['REQUEST_DELAY']:
            time.sleep(self.config['REQUEST_DELAY'] - elapsed)
        
        try:
            results = []
            # Search DuckDuckGo
            for r in self.ddgs.text(query, max_results=num_results):
                results.append({
                    'title': r.get('title', ''),
                    'link': r.get('href', ''),
                    'snippet': r.get('body', ''),
                    'displayLink': self._extract_domain(r.get('href', ''))
                })
            
            self.last_request_time = time.time()
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return ''