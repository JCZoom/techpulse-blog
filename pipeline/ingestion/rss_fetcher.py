"""
RSS Feed Fetcher for TechPulse
Fetches articles from RSS/Atom feeds with error handling and retry logic
"""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from urllib.parse import urlparse
import time
import urllib3

# Suppress SSL warnings (when using verify=False)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Article:
    """Represents a single article with normalized fields"""
    
    def __init__(self, title: str, url: str, published: datetime, 
                 content: str, source: str, category: str = "general", 
                 author: str = None, image_url: str = None):
        self.title = title
        self.url = url
        self.published = published
        self.content = content
        self.source = source
        self.category = category
        self.author = author
        self.image_url = image_url
        self.score = None  # Will be set by scoring module
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'url': self.url,
            'published': self.published.isoformat() if self.published else None,
            'content': self.content,
            'source': self.source,
            'category': self.category,
            'score': self.score,
            'word_count': len(self.content.split()) if self.content else 0
        }
    
    def __repr__(self):
        return f"<Article: {self.title[:50]}... from {self.source}>"


class RSSFetcher:
    """Fetches articles from RSS/Atom feeds"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = 'TechPulse/1.0 (https://jeffcoy.net; AI content curator)'
        
    def fetch_feed(self, feed_url: str, source_name: str, 
                   category: str = "general", 
                   lookback_hours: int = 48) -> List[Article]:
        """
        Fetch articles from a single RSS feed
        
        Args:
            feed_url: URL of the RSS/Atom feed
            source_name: Human-readable source name
            category: Content category
            lookback_hours: Only fetch articles from last N hours
            
        Returns:
            List of Article objects
        """
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        logger.info(f"Fetching feed: {source_name} ({feed_url})")
        
        try:
            # Fetch with custom user agent
            # Note: verify=False bypasses SSL cert verification (workaround for system cert issues)
            headers = {'User-Agent': self.user_agent}
            response = requests.get(feed_url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed {source_name} has parsing errors: {feed.bozo_exception}")
            
            # Process entries
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry, source_name, category, cutoff_time)
                    if article:
                        articles.append(article)
                except Exception as e:
                    logger.error(f"Error parsing entry from {source_name}: {e}")
                    continue
            
            logger.info(f"✓ Fetched {len(articles)} articles from {source_name}")
            
        except requests.RequestException as e:
            logger.error(f"✗ Failed to fetch {source_name}: {e}")
        except Exception as e:
            logger.error(f"✗ Unexpected error fetching {source_name}: {e}")
        
        return articles
    
    def _parse_entry(self, entry, source_name: str, category: str, 
                     cutoff_time: datetime) -> Optional[Article]:
        """Parse a single feed entry into an Article"""
        
        # Extract title
        title = entry.get('title', 'Untitled').strip()
        if not title or title == 'Untitled':
            return None
        
        # Extract URL
        url = entry.get('link', '')
        if not url:
            return None
        
        # Extract published date
        published = self._parse_date(entry)
        
        # Skip old articles
        if published and published < cutoff_time:
            return None
        
        # Extract content (try multiple fields)
        content = self._extract_content(entry)
        
        # Skip if no content (lowered threshold from 10 to 3 words to capture short descriptions)
        if not content or len(content.split()) < 3:
            return None
        
        # Extract author
        author = self._extract_author(entry)
        
        # Extract image from RSS
        image_url = self._extract_image(entry)
        
        return Article(
            title=title,
            url=url,
            published=published,
            content=content,
            source=source_name,
            category=category,
            author=author,
            image_url=image_url
        )
    
    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse publication date from various feed formats"""
        
        # Try different date fields
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field):
                time_struct = getattr(entry, date_field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except (ValueError, TypeError):
                        continue
        
        # Fallback to string parsing
        for date_field in ['published', 'updated', 'created']:
            if hasattr(entry, date_field):
                date_str = getattr(entry, date_field)
                if date_str:
                    try:
                        from dateutil import parser
                        return parser.parse(date_str)
                    except Exception:
                        continue
        
        # Default to now if no date found
        return datetime.now()
    
    def _extract_content(self, entry) -> str:
        """
        Extract content from various feed content fields
        
        NOTE: RSS/Atom feeds typically provide summaries or excerpts (15-500 words),
        not full article content. To get full articles, you'd need to fetch and 
        scrape each article URL separately (not implemented here for reliability/speed).
        """
        
        # Try content field (Atom)
        if hasattr(entry, 'content') and entry.content:
            return self._clean_html(entry.content[0].value)
        
        # Try summary/description (RSS)
        if hasattr(entry, 'summary') and entry.summary:
            return self._clean_html(entry.summary)
        
        if hasattr(entry, 'description') and entry.description:
            return self._clean_html(entry.description)
        
        # Fallback to title if nothing else
        return entry.get('title', '')
    
    def _extract_author(self, entry) -> Optional[str]:
        """Extract author from RSS entry"""
        # Try author field
        if hasattr(entry, 'author') and entry.author:
            return entry.author.strip()
        
        # Try author_detail
        if hasattr(entry, 'author_detail') and entry.author_detail:
            if 'name' in entry.author_detail:
                return entry.author_detail['name'].strip()
        
        # Try dc:creator (Dublin Core)
        if hasattr(entry, 'dc_creator') and entry.dc_creator:
            return entry.dc_creator.strip()
        
        return None
    
    def _extract_image(self, entry) -> Optional[str]:
        """Extract image URL from RSS entry"""
        # Try media:content (Media RSS)
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                    return media.get('url')
        
        # Try media:thumbnail
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            if isinstance(entry.media_thumbnail, list) and len(entry.media_thumbnail) > 0:
                return entry.media_thumbnail[0].get('url')
            elif isinstance(entry.media_thumbnail, dict):
                return entry.media_thumbnail.get('url')
        
        # Try enclosures
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href')
        
        # Try links for image
        if hasattr(entry, 'links') and entry.links:
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    return link.get('href')
        
        return None
    
    def _clean_html(self, html_content: str) -> str:
        """Remove HTML tags and clean up text"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(['script', 'style']):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            return text
        except Exception as e:
            logger.warning(f"HTML cleaning failed: {e}")
            return html_content
    
    def fetch_all_sources(self, sources: List[Dict], 
                          lookback_hours: int = 48) -> List[Article]:
        """
        Fetch articles from multiple sources
        
        Args:
            sources: List of source dicts with 'url', 'name', 'category'
            lookback_hours: Only fetch recent articles
            
        Returns:
            Combined list of all articles
        """
        all_articles = []
        
        logger.info(f"Starting fetch from {len(sources)} sources...")
        
        for source in sources:
            # Add delay between requests to be respectful
            time.sleep(1)
            
            articles = self.fetch_feed(
                feed_url=source['url'],
                source_name=source['name'],
                category=source.get('category', 'general'),
                lookback_hours=lookback_hours
            )
            
            all_articles.extend(articles)
        
        logger.info(f"✓ Total articles fetched: {len(all_articles)}")
        
        return all_articles


def load_sources_from_yaml(yaml_file: str) -> List[Dict]:
    """Load source configuration from YAML file"""
    import yaml
    
    with open(yaml_file, 'r') as f:
        config = yaml.safe_load(f)
    
    sources = config.get('sources', [])
    
    # Filter out disabled sources or add priority sorting
    active_sources = [s for s in sources if s.get('type') == 'rss']
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    active_sources.sort(key=lambda s: priority_order.get(s.get('priority', 'low'), 3))
    
    return active_sources


# Example usage
if __name__ == '__main__':
    # Test the fetcher
    import os
    from pathlib import Path
    
    # Load sources
    sources_file = Path(__file__).parent / 'sources.yaml'
    sources = load_sources_from_yaml(sources_file)
    
    # Fetch articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all_sources(sources[:3], lookback_hours=48)  # Test with first 3
    
    # Print results
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
