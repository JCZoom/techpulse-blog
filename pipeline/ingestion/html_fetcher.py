"""
HTML Article Fetcher for TechPulse
Fetches articles from sites without RSS feeds using sitemap + HTML scraping
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import xml.etree.ElementTree as ET
import json
import re
from .rss_fetcher import Article

# Configure logging
logger = logging.getLogger(__name__)


class HTMLArticleFetcher:
    """Fetches articles from HTML pages with sitemap support"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.user_agent = 'TechPulse/1.0 (https://jeffcoy.net; AI content curator)'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
    def fetch_from_sitemap(self, sitemap_url: str, url_pattern: str, 
                          source_name: str, category: str = "general",
                          lookback_hours: int = 48, max_articles: int = 50) -> List[Article]:
        """
        Fetch articles from a sitemap URL
        
        Args:
            sitemap_url: URL to XML sitemap
            url_pattern: Regex pattern to match article URLs (e.g., r'/p/[^/]+$')
            source_name: Human-readable source name
            category: Content category
            lookback_hours: Only fetch articles from last N hours
            max_articles: Maximum number of articles to scrape
            
        Returns:
            List of Article objects
        """
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        logger.info(f"Fetching sitemap: {source_name} ({sitemap_url})")
        
        try:
            # Fetch sitemap
            response = self.session.get(sitemap_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse sitemap XML
            root = ET.fromstring(response.content)
            
            # Handle both sitemap formats (with and without namespace)
            namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            # Try with namespace first
            url_elements = root.findall('.//ns:url/ns:loc', namespace)
            if not url_elements:
                # Try without namespace
                url_elements = root.findall('.//loc')
            
            # Extract URLs matching pattern
            pattern = re.compile(url_pattern)
            matching_urls = []
            
            for url_elem in url_elements:
                url = url_elem.text
                if pattern.search(url):
                    matching_urls.append(url)
            
            logger.info(f"Found {len(matching_urls)} potential articles in sitemap")
            
            # Limit to most recent articles
            urls_to_scrape = matching_urls[:max_articles]
            
            # Fetch and parse each article
            for i, url in enumerate(urls_to_scrape, 1):
                try:
                    article = self._scrape_article(url, source_name, category)
                    if article:
                        # Check if recent enough
                        if article.published and article.published >= cutoff_time:
                            articles.append(article)
                            logger.debug(f"  [{i}/{len(urls_to_scrape)}] ✓ {article.title[:60]}")
                        else:
                            logger.debug(f"  [{i}/{len(urls_to_scrape)}] ✗ Too old: {article.title[:60]}")
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} articles from {source_name}")
            
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch sitemap {source_name}: {e}")
        except ET.ParseError as e:
            logger.error(f"✗ Failed to parse sitemap XML {source_name}: {e}")
        except Exception as e:
            logger.error(f"✗ Unexpected error fetching {source_name}: {e}")
        
        return articles
    
    def _scrape_article(self, url: str, source_name: str, category: str) -> Optional[Article]:
        """Scrape a single article page"""
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Strategy 1: Try to extract JSON-LD structured data
        article = self._extract_from_jsonld(soup, url, source_name, category)
        if article:
            return article
        
        # Strategy 2: Try Open Graph meta tags
        article = self._extract_from_opengraph(soup, url, source_name, category)
        if article:
            return article
        
        # Strategy 3: Try standard HTML elements
        article = self._extract_from_html(soup, url, source_name, category)
        if article:
            return article
        
        logger.warning(f"Could not extract article data from {url}")
        return None
    
    def _extract_from_jsonld(self, soup: BeautifulSoup, url: str, 
                            source_name: str, category: str) -> Optional[Article]:
        """Extract article data from JSON-LD structured data"""
        
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    data = data[0] if data else {}
                
                # Look for NewsArticle, BlogPosting, or Article types
                if data.get('@type') in ['NewsArticle', 'BlogPosting', 'Article']:
                    title = data.get('headline') or data.get('name')
                    description = data.get('description')
                    date_str = data.get('datePublished') or data.get('dateCreated')
                    author = data.get('author', {})
                    if isinstance(author, dict):
                        author = author.get('name')
                    elif isinstance(author, list) and author:
                        author = author[0].get('name') if isinstance(author[0], dict) else str(author[0])
                    
                    published = None
                    if date_str:
                        try:
                            from dateutil import parser
                            published = parser.parse(date_str)
                        except Exception:
                            published = datetime.now()
                    
                    if title and description and len(description.split()) >= 3:
                        return Article(
                            title=title,
                            url=url,
                            published=published or datetime.now(),
                            content=description,
                            source=source_name,
                            category=category,
                            author=author
                        )
            except (json.JSONDecodeError, KeyError, AttributeError) as e:
                logger.debug(f"Error parsing JSON-LD: {e}")
                continue
        
        return None
    
    def _extract_from_opengraph(self, soup: BeautifulSoup, url: str,
                               source_name: str, category: str) -> Optional[Article]:
        """Extract article data from Open Graph meta tags"""
        
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_type = soup.find('meta', property='og:type')
        
        # Also try article:published_time
        og_published = soup.find('meta', property='article:published_time')
        og_author = soup.find('meta', property='article:author')
        
        if og_title and og_description:
            title = og_title.get('content', '')
            description = og_description.get('content', '')
            
            published = datetime.now()
            if og_published:
                try:
                    from dateutil import parser
                    published = parser.parse(og_published.get('content', ''))
                except Exception:
                    pass
            
            author = None
            if og_author:
                author = og_author.get('content')
            
            if title and description and len(description.split()) >= 3:
                return Article(
                    title=title,
                    url=url,
                    published=published,
                    content=description,
                    source=source_name,
                    category=category,
                    author=author
                )
        
        return None
    
    def _extract_from_html(self, soup: BeautifulSoup, url: str,
                          source_name: str, category: str) -> Optional[Article]:
        """Extract article data from standard HTML elements (fallback)"""
        
        # Try to find title
        title_elem = (
            soup.find('h1') or 
            soup.find('meta', {'name': 'title'}) or
            soup.find('title')
        )
        
        # Try to find description
        desc_elem = (
            soup.find('meta', {'name': 'description'}) or
            soup.find('p', class_=re.compile(r'(description|excerpt|summary)', re.I))
        )
        
        if title_elem and desc_elem:
            # Extract text
            if hasattr(title_elem, 'get'):
                title = title_elem.get('content', '')
            else:
                title = title_elem.get_text(strip=True)
            
            if hasattr(desc_elem, 'get'):
                description = desc_elem.get('content', '')
            else:
                description = desc_elem.get_text(strip=True)
            
            if title and description and len(description.split()) >= 3:
                return Article(
                    title=title,
                    url=url,
                    published=datetime.now(),
                    content=description,
                    source=source_name,
                    category=category
                )
        
        return None


# Example usage
if __name__ == '__main__':
    # Test the HTML fetcher
    fetcher = HTMLArticleFetcher()
    
    # Test Superhuman AI
    print("Testing Superhuman AI...")
    articles = fetcher.fetch_from_sitemap(
        sitemap_url="https://www.superhuman.ai/sitemap.xml",
        url_pattern=r'/p/[^/]+$',
        source_name="Superhuman AI",
        category="ai_news",
        lookback_hours=168,  # 7 days for testing
        max_articles=10
    )
    
    print(f"\n{'='*60}")
    print(f"Fetched {len(articles)} articles")
    print(f"{'='*60}\n")
    
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source} | Category: {article.category}")
        print(f"   URL: {article.url}")
        print(f"   Published: {article.published}")
        print(f"   Content preview: {article.content[:100]}...")
        print()
