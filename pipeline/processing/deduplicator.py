"""
Article Deduplication and Filtering
Removes duplicate articles and filters by quality
"""

from typing import List
from urllib.parse import urlparse
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class Deduplicator:
    """Remove duplicate articles using multiple strategies"""
    
    def __init__(self, title_similarity_threshold: float = 0.85):
        """
        Args:
            title_similarity_threshold: Minimum similarity ratio to consider titles duplicates
        """
        self.title_similarity_threshold = title_similarity_threshold
    
    def deduplicate(self, articles: List) -> List:
        """
        Remove duplicate articles using URL and title similarity
        
        Args:
            articles: List of Article objects
            
        Returns:
            Deduplicated list of articles
        """
        if not articles:
            return []
        
        logger.info(f"Deduplicating {len(articles)} articles...")
        
        seen_urls = set()
        seen_titles = []
        unique_articles = []
        
        for article in articles:
            # Check exact URL match
            normalized_url = self._normalize_url(article.url)
            if normalized_url in seen_urls:
                logger.debug(f"Duplicate URL: {article.title[:50]}")
                continue
            
            # Check title similarity
            if self._is_similar_title(article.title, seen_titles):
                logger.debug(f"Similar title: {article.title[:50]}")
                continue
            
            # Article is unique
            seen_urls.add(normalized_url)
            seen_titles.append(article.title.lower())
            unique_articles.append(article)
        
        removed = len(articles) - len(unique_articles)
        logger.info(f"✓ Removed {removed} duplicates, {len(unique_articles)} unique articles remain")
        
        return unique_articles
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for comparison (remove tracking params, etc.)"""
        try:
            parsed = urlparse(url)
            # Keep scheme, netloc, and path - ignore query params and fragments
            normalized = f"{parsed.netloc}{parsed.path}".lower()
            # Remove trailing slashes
            normalized = normalized.rstrip('/')
            return normalized
        except Exception:
            return url.lower()
    
    def _is_similar_title(self, title: str, seen_titles: List[str]) -> bool:
        """Check if title is too similar to any previously seen title"""
        title_lower = title.lower()
        
        for seen in seen_titles:
            similarity = SequenceMatcher(None, title_lower, seen).ratio()
            if similarity >= self.title_similarity_threshold:
                return True
        
        return False


class QualityFilter:
    """Filter articles based on quality criteria"""
    
    def __init__(self, min_word_count: int = 200):
        """
        Args:
            min_word_count: Minimum number of words in article content
        """
        self.min_word_count = min_word_count
    
    def filter(self, articles: List) -> List:
        """
        Filter articles by quality criteria
        
        Args:
            articles: List of Article objects
            
        Returns:
            Filtered list of quality articles
        """
        if not articles:
            return []
        
        logger.info(f"Filtering {len(articles)} articles for quality...")
        
        quality_articles = []
        
        for article in articles:
            # Check word count
            word_count = len(article.content.split()) if article.content else 0
            if word_count < self.min_word_count:
                logger.debug(f"Too short ({word_count} words): {article.title[:50]}")
                continue
            
            # Check for common spam patterns
            if self._is_spam(article):
                logger.debug(f"Spam detected: {article.title[:50]}")
                continue
            
            # Article passes quality checks
            quality_articles.append(article)
        
        removed = len(articles) - len(quality_articles)
        logger.info(f"✓ Removed {removed} low-quality articles, {len(quality_articles)} remain")
        
        return quality_articles
    
    def _is_spam(self, article) -> bool:
        """Detect common spam patterns"""
        
        # Check for common spam keywords in title
        spam_keywords = [
            'click here', 'buy now', 'limited time', 'act now',
            'congratulations', 'you won', 'free money'
        ]
        
        title_lower = article.title.lower()
        for keyword in spam_keywords:
            if keyword in title_lower:
                return True
        
        # Check for excessive capitalization
        if article.title.isupper() and len(article.title) > 10:
            return True
        
        # Check for suspicious URLs
        suspicious_domains = ['bit.ly', 't.co']  # Expand as needed
        for domain in suspicious_domains:
            if domain in article.url.lower():
                # Don't auto-reject, but could flag
                pass
        
        return False


def process_articles(articles: List, min_word_count: int = 200,
                     title_similarity: float = 0.85) -> List:
    """
    Complete processing pipeline: deduplicate and filter
    
    Args:
        articles: List of Article objects
        min_word_count: Minimum words for quality filter
        title_similarity: Threshold for title similarity
        
    Returns:
        Processed list of articles
    """
    logger.info(f"Starting article processing with {len(articles)} articles...")
    
    # Deduplicate
    deduplicator = Deduplicator(title_similarity_threshold=title_similarity)
    articles = deduplicator.deduplicate(articles)
    
    # Filter for quality
    quality_filter = QualityFilter(min_word_count=min_word_count)
    articles = quality_filter.filter(articles)
    
    logger.info(f"✓ Processing complete: {len(articles)} articles ready")
    
    return articles


# Example usage
if __name__ == '__main__':
    # Test with dummy data
    from ingestion.rss_fetcher import Article
    from datetime import datetime
    
    test_articles = [
        Article("Test Article", "https://example.com/1", datetime.now(), 
                "This is a test article with enough content " * 50, "TestSource"),
        Article("Test Article", "https://example.com/2", datetime.now(),  # Duplicate title
                "Different content but same title " * 50, "TestSource2"),
        Article("Another Article", "https://example.com/1", datetime.now(),  # Duplicate URL
                "Different title but same URL " * 50, "TestSource3"),
        Article("Short", "https://example.com/3", datetime.now(), 
                "Too short", "TestSource4"),  # Will be filtered
        Article("CLICK HERE NOW!!!", "https://example.com/4", datetime.now(),
                "Spam content " * 50, "TestSource5"),  # Spam
    ]
    
    processed = process_articles(test_articles, min_word_count=100)
    
    print(f"\n{'='*60}")
    print(f"Processed {len(test_articles)} → {len(processed)} articles")
    print(f"{'='*60}\n")
    
    for article in processed:
        print(f"- {article.title}")
