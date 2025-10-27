import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from urllib.parse import urlparse
import tldextract
from typing import Dict, Optional

class WebContentExtractor:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_content(self, url: str) -> Optional[Dict]:
        """Extract main content from a web page using newspaper or BeautifulSoup fallback"""
        try:
            # First try with newspaper (better for article extraction)
            try:
                article = Article(url)
                article.download()
                article.parse()
                
                if article.text and len(article.text) > 100:
                    return {
                        'title': article.title,
                        'text': article.text[:self.config['MAX_CONTENT_LENGTH']],
                        'authors': article.authors,
                        'publish_date': article.publish_date,
                        'url': url,
                        'domain': tldextract.extract(url).registered_domain,
                        'extraction_method': 'newspaper'
                    }
            except Exception as newspaper_error:
                print(f"Newspaper extraction failed for {url}: {newspaper_error}")
            
            # Fallback to BeautifulSoup
            try:
                response = self.session.get(url, timeout=self.config['REQUEST_TIMEOUT'])
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script, style, and nav elements
                for element in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
                    element.decompose()
                
                # Remove comments
                for comment in soup.findAll(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                    comment.extract()
                
                # Extract text
                text = soup.get_text()
                
                # Clean up text
                text = re.sub(r'\s+', ' ', text).strip()
                text = text[:self.config['MAX_CONTENT_LENGTH']]
                
                # Try to get title from meta tags if not in title tag
                title = soup.title.string if soup.title else ''
                if not title:
                    meta_title = soup.find('meta', attrs={'name': 'title'})
                    if meta_title:
                        title = meta_title.get('content', '')
                    else:
                        og_title = soup.find('meta', property='og:title')
                        if og_title:
                            title = og_title.get('content', '')
                
                return {
                    'title': title,
                    'text': text,
                    'authors': [],
                    'publish_date': None,
                    'url': url,
                    'domain': tldextract.extract(url).registered_domain,
                    'extraction_method': 'beautifulsoup'
                }
            except Exception as bs_error:
                print(f"BeautifulSoup extraction failed for {url}: {bs_error}")
                
        except Exception as e:
            print(f"Extraction error for {url}: {e}")
            return None
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return tldextract.extract(url).registered_domain
        except:
            return ""