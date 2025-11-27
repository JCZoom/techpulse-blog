"""
JSON Content Generator for TechPulse
Generates structured JSON files that the website consumes
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import random

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate JSON content files for the website"""
    
    def __init__(self, output_dir: str = "content"):
        """
        Args:
            output_dir: Root directory for content files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "daily").mkdir(exist_ok=True)
        (self.output_dir / "categories").mkdir(exist_ok=True)
    
    def generate_latest(self, articles: List, date_str: str = None) -> Dict:
        """
        Generate latest.json for the homepage
        
        Args:
            articles: List of Article objects (should be pre-sorted by score)
            date_str: Date string for display (e.g., "November 26, 2024")
            
        Returns:
            Content dictionary
        """
        if not date_str:
            date_str = datetime.now().strftime("%B %d, %Y")
        
        logger.info("Generating latest.json...")
        
        # Sort by score (highest first)
        sorted_articles = sorted(articles, key=lambda a: a.score or 0, reverse=True)
        
        # Select hero article (highest score)
        hero = self._format_hero_article(sorted_articles[0]) if sorted_articles else None
        
        # Select headline articles (next 4-6 articles)
        headlines = [self._format_headline_article(a) for a in sorted_articles[1:7]]
        
        # Select runners-up articles (next 25 articles after headlines)
        runners_up = [self._format_runnerup_article(a) for a in sorted_articles[7:32]]
        
        # Find video content if any
        video_spotlight = self._find_video_content(sorted_articles)
        
        # Group by category
        categories = self._generate_category_summary(sorted_articles)
        
        content = {
            "generated_at": datetime.now().isoformat(),
            "date": date_str,
            "hero": hero,
            "headlines": headlines,
            "runners_up": runners_up,
            "video_spotlight": video_spotlight,
            "categories": categories,
            "stats": {
                "total_articles": len(articles),
                "categories_count": len(categories),
                "runners_up_count": len(runners_up)
            }
        }
        
        # Write to file
        output_file = self.output_dir / "latest.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Generated latest.json with {len(sorted_articles)} articles")
        
        return content
    
    def generate_daily_archive(self, articles: List, date: datetime = None) -> Dict:
        """
        Generate daily archive file (content/daily/YYYY-MM-DD.json)
        
        Args:
            articles: List of Article objects
            date: Date for the archive (defaults to today)
            
        Returns:
            Archive content dictionary
        """
        if not date:
            date = datetime.now()
        
        date_key = date.strftime("%Y-%m-%d")
        logger.info(f"Generating daily archive for {date_key}...")
        
        archive_data = {
            "date": date_key,
            "date_display": date.strftime("%B %d, %Y"),
            "articles": [self._format_archive_article(a) for a in articles],
            "stats": {
                "total_articles": len(articles),
                "avg_score": sum(a.score or 0 for a in articles) / len(articles) if articles else 0,
                "sources": list(set(a.source for a in articles)),
                "categories": list(set(a.category for a in articles))
            }
        }
        
        # Write to file
        output_file = self.output_dir / "daily" / f"{date_key}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Generated daily archive: {output_file}")
        
        return archive_data
    
    def _format_hero_article(self, article) -> Dict:
        """Format article for hero section"""
        return {
            "title": article.title,
            "subtitle": self._generate_excerpt(article.content, max_words=50),
            "category": self._format_category_name(article.category),
            "url": article.url,
            "source": article.source,
            "author": getattr(article, 'author', None) or article.source,  # Use real author or source
            "read_time": self._estimate_read_time(article.content),
            "score": round(article.score, 1) if article.score else 8.0,
            "published": article.published.isoformat() if article.published else None,
            "image_url": getattr(article, 'image_url', None)  # Add image URL
        }
    
    def _format_headline_article(self, article) -> Dict:
        """Format article for headlines grid"""
        return {
            "title": article.title,
            "excerpt": self._generate_excerpt(article.content, max_words=30),
            "category": self._format_category_name(article.category),
            "url": article.url,
            "source": article.source,
            "read_time": self._estimate_read_time(article.content),
            "published": article.published.isoformat() if article.published else None,
            "score": round(article.score, 1) if article.score else 8.0,
            "image_url": getattr(article, 'image_url', None)
        }
    
    def _format_runnerup_article(self, article) -> Dict:
        """Format article for runners-up page (compact format)"""
        return {
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "author": getattr(article, 'author', None) or article.source,
            "category": self._format_category_name(article.category),
            "read_time": self._estimate_read_time(article.content),
            "published": article.published.isoformat() if article.published else None,
            "score": round(article.score, 1) if article.score else 7.0,
            "image_url": getattr(article, 'image_url', None)
        }
    
    def _format_archive_article(self, article) -> Dict:
        """Format article for archive page"""
        return {
            "id": self._generate_article_id(article),
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "category": article.category,
            "published": article.published.isoformat() if article.published else None,
            "score": round(article.score, 1) if article.score else 8.0,
            "word_count": len(article.content.split()) if article.content else 0
        }
    
    def _find_video_content(self, articles: List) -> Dict:
        """Find and format video content"""
        
        # Look for YouTube links or video-related sources
        video_sources = ['youtube', 'vimeo', 'video']
        
        for article in articles:
            url_lower = article.url.lower()
            source_lower = article.source.lower()
            
            if any(vs in url_lower or vs in source_lower for vs in video_sources):
                return {
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "thumbnail": self._extract_video_thumbnail(article.url),
                    "duration": "Unknown"  # Would need video API to get this
                }
        
        # No video found
        return None
    
    def _extract_video_thumbnail(self, url: str) -> str:
        """Extract video thumbnail URL (YouTube only for now)"""
        if 'youtube.com' in url or 'youtu.be' in url:
            # Extract video ID and construct thumbnail URL
            # This is a simplified version
            return "https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg"
        return None
    
    def _generate_category_summary(self, articles: List) -> List[Dict]:
        """Generate category summary for homepage"""
        
        category_counts = {}
        category_icons = {
            'ai_research': '🔬',
            'ai_news': '🤖',
            'ai_podcast': '🎙️',
            'general_tech': '💻',
            'startups': '🚀',
            'tech_analysis': '📊',
            'tech_strategy': '📈'
        }
        
        for article in articles:
            cat = article.category
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        categories = []
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            categories.append({
                "name": self._format_category_name(cat),
                "slug": cat,
                "count": count,
                "icon": category_icons.get(cat, '📄')
            })
        
        return categories
    
    def _format_category_name(self, category: str) -> str:
        """Convert category slug to display name"""
        replacements = {
            'ai_research': 'AI Research',
            'ai_news': 'AI News',
            'ai_podcast': 'AI Podcast',
            'general_tech': 'Tech',
            'startups': 'Startups',
            'tech_analysis': 'Analysis',
            'tech_strategy': 'Strategy'
        }
        return replacements.get(category, category.replace('_', ' ').title())
    
    def _generate_excerpt(self, content: str, max_words: int = 30) -> str:
        """Generate a clean excerpt from content"""
        if not content:
            return ""
        
        words = content.split()[:max_words]
        excerpt = ' '.join(words)
        
        # Add ellipsis if truncated
        if len(content.split()) > max_words:
            excerpt += '...'
        
        return excerpt
    
    def _estimate_read_time(self, content: str) -> str:
        """Estimate reading time (assumes 200 words per minute)"""
        if not content:
            return "1 min"
        
        word_count = len(content.split())
        minutes = max(1, round(word_count / 200))
        
        return f"{minutes} min"
    
    def _generate_article_id(self, article) -> str:
        """Generate a unique ID for an article"""
        if article.published:
            date_str = article.published.strftime("%Y-%m-%d")
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Create a simple hash from title
        title_hash = abs(hash(article.title)) % 10000
        
        return f"{date_str}-{title_hash:04d}"


def assign_placeholder_scores(articles: List, 
                              default_score: float = 8.0,
                              variance: float = 1.5) -> List:
    """
    Assign placeholder scores to articles (for Phase 1)
    In Phase 2, this will be replaced with AI scoring
    
    Args:
        articles: List of Article objects
        default_score: Base score
        variance: Random variance to add/subtract
        
    Returns:
        Articles with scores assigned
    """
    logger.info("Assigning placeholder scores...")
    
    for article in articles:
        # Add some randomness for testing
        score = default_score + random.uniform(-variance, variance)
        # Clamp to 1-10 range
        article.score = max(1.0, min(10.0, score))
    
    logger.info(f"✓ Assigned scores to {len(articles)} articles")
    
    return articles


# Example usage
if __name__ == '__main__':
    from ingestion.rss_fetcher import Article
    from datetime import datetime
    
    # Create test articles
    test_articles = [
        Article(
            "AI Breakthrough: New Model Achieves Human-Level Performance",
            "https://example.com/1",
            datetime.now(),
            "This is a groundbreaking development in AI research that shows " * 30,
            "AI Research Weekly",
            "ai_research"
        ),
        Article(
            "Startup Raises $100M for AI Infrastructure",
            "https://example.com/2",
            datetime.now(),
            "A new startup focused on AI infrastructure has raised significant funding " * 25,
            "TechCrunch",
            "startups"
        ),
    ]
    
    # Assign scores
    test_articles = assign_placeholder_scores(test_articles)
    
    # Generate content
    generator = ContentGenerator(output_dir="../content")
    
    latest = generator.generate_latest(test_articles)
    daily = generator.generate_daily_archive(test_articles)
    
    print(f"\n{'='*60}")
    print("Generated content files:")
    print(f"  - latest.json")
    print(f"  - daily/{datetime.now().strftime('%Y-%m-%d')}.json")
    print(f"{'='*60}\n")
