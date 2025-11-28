"""
Article History Filter
Filter out articles that have been published in recent daily editions
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Set

logger = logging.getLogger(__name__)


class HistoryFilter:
    """Filter out previously published articles"""
    
    def __init__(self, content_dir: str = "../content", lookback_days: int = 7):
        """
        Initialize history filter
        
        Args:
            content_dir: Path to content directory
            lookback_days: How many days back to check for duplicates
        """
        self.content_dir = Path(content_dir)
        self.daily_dir = self.content_dir / "daily"
        self.lookback_days = lookback_days
        
    def get_published_urls(self) -> Set[str]:
        """
        Get set of URLs that have been published in recent daily editions
        
        Returns:
            Set of article URLs
        """
        published_urls = set()
        
        if not self.daily_dir.exists():
            logger.warning(f"Daily directory not found: {self.daily_dir}")
            return published_urls
        
        # Get recent daily files
        cutoff_date = datetime.now() - timedelta(days=self.lookback_days)
        
        for daily_file in self.daily_dir.glob("*.json"):
            try:
                # Parse date from filename (e.g., "2025-11-28.json")
                date_str = daily_file.stem  # Gets "2025-11-28"
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Skip if too old
                if file_date < cutoff_date:
                    continue
                
                # Load articles from this daily file
                with open(daily_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    articles = data.get('articles', [])
                    for article in articles:
                        url = article.get('url')
                        if url:
                            published_urls.add(url)
                            
                logger.debug(f"Loaded {len(articles)} articles from {daily_file.name}")
                
            except (ValueError, json.JSONDecodeError) as e:
                logger.warning(f"Error reading {daily_file}: {e}")
                continue
        
        logger.info(f"Found {len(published_urls)} previously published articles in last {self.lookback_days} days")
        return published_urls
    
    def filter_articles(self, articles: List) -> List:
        """
        Filter out articles that have been published recently
        
        Args:
            articles: List of Article objects
            
        Returns:
            Filtered list of articles (only new ones)
        """
        if not articles:
            return []
        
        # Get published URLs
        published_urls = self.get_published_urls()
        
        if not published_urls:
            logger.info("No published articles found - keeping all articles")
            return articles
        
        # Filter out published articles
        new_articles = []
        filtered_count = 0
        
        for article in articles:
            if article.url in published_urls:
                filtered_count += 1
                logger.debug(f"Filtering out previously published: {article.title[:60]}...")
            else:
                new_articles.append(article)
        
        logger.info(f"✓ Filtered out {filtered_count} previously published articles")
        logger.info(f"✓ {len(new_articles)} new articles remain")
        
        return new_articles


def filter_by_history(articles: List, content_dir: str = "../content", 
                     lookback_days: int = 7) -> List:
    """
    Convenience function to filter articles by publication history
    
    Args:
        articles: List of Article objects
        content_dir: Path to content directory
        lookback_days: How many days back to check
        
    Returns:
        Filtered list of articles
    """
    filter_obj = HistoryFilter(content_dir=content_dir, lookback_days=lookback_days)
    return filter_obj.filter_articles(articles)
