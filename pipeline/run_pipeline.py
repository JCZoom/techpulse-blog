#!/usr/bin/env python3
"""
TechPulse Daily Content Curation Pipeline

Main orchestrator that runs the full pipeline:
1. Fetch content from sources
2. Process and filter
3. Score articles (AI-powered)
4. Generate output files
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
import yaml
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.rss_fetcher import RSSFetcher, load_sources_from_yaml
from processing.deduplicator import process_articles
from processing.history_filter import filter_by_history
from processing.image_extractor import ImageExtractor
from output.json_generator import ContentGenerator, assign_placeholder_scores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline.log')
    ]
)
logger = logging.getLogger(__name__)


class TechPulsePipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """Initialize pipeline with configuration"""
        self.config = self._load_config(config_file)
        self.sources_file = Path(__file__).parent / "ingestion" / "sources.yaml"
        
        logger.info("="*60)
        logger.info("TechPulse Daily Curation Pipeline")
        logger.info("="*60)
    
    def _load_config(self, config_file: str) -> dict:
        """Load pipeline configuration"""
        config_path = Path(__file__).parent / config_file
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def run(self):
        """Execute the complete pipeline"""
        
        try:
            # Phase 1: Ingestion
            logger.info("\n📥 PHASE 1: Content Ingestion")
            logger.info("-" * 60)
            articles = self._ingest_content()
            
            if not articles:
                logger.error("❌ No articles fetched! Exiting.")
                return False
            
            # Phase 2: Processing
            logger.info("\n🔄 PHASE 2: Processing & Filtering")
            logger.info("-" * 60)
            articles = self._process_content(articles)
            
            if not articles:
                logger.error("❌ No articles after filtering! Exiting.")
                return False
            
            # Phase 3: Scoring (Placeholder for now)
            logger.info("\n⭐ PHASE 3: Scoring Articles")
            logger.info("-" * 60)
            articles = self._score_content(articles)
            
            # Phase 4: Content Generation
            logger.info("\n📝 PHASE 4: Generating Content Files")
            logger.info("-" * 60)
            self._generate_output(articles)
            
            # Summary
            logger.info("\n" + "="*60)
            logger.info("✅ Pipeline completed successfully!")
            logger.info("="*60)
            logger.info(f"Total articles published: {len(articles)}")
            logger.info(f"Content files generated in: {self.config['output']['content_dir']}")
            logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            return False
    
    def _ingest_content(self) -> list:
        """Fetch articles from all configured sources"""
        
        # Load sources
        sources = load_sources_from_yaml(self.sources_file)
        logger.info(f"Loading from {len(sources)} sources...")
        
        # Fetch articles
        fetcher = RSSFetcher(timeout=30, max_retries=3)
        lookback_hours = self.config['pipeline']['lookback_hours']
        
        articles = fetcher.fetch_all_sources(sources, lookback_hours=lookback_hours)
        
        logger.info(f"✓ Ingested {len(articles)} total articles")
        
        return articles
    
    def _process_content(self, articles: list) -> list:
        """Deduplicate, filter, and enrich articles"""
        
        min_words = self.config['pipeline']['min_word_count']
        
        articles = process_articles(
            articles,
            min_word_count=min_words,
            title_similarity=0.85
        )
        
        logger.info(f"✓ {len(articles)} articles after deduplication")
        
        # Filter out previously published articles
        content_dir = self.config['output']['content_dir']
        articles = filter_by_history(
            articles,
            content_dir=content_dir,
            lookback_days=7  # Don't republish articles from last 7 days
        )
        
        logger.info(f"✓ {len(articles)} articles after history filter")
        
        # Extract images from articles
        logger.info("Extracting images from articles...")
        extractor = ImageExtractor()
        article_dicts = [self._article_to_dict(a) for a in articles]
        enriched_dicts = extractor.add_images_to_articles(article_dicts)
        
        # Update articles with image URLs
        for article, enriched in zip(articles, enriched_dicts):
            if enriched.get('image_url'):
                article.image_url = enriched['image_url']
        
        return articles
    
    def _score_content(self, articles: list) -> list:
        """Score articles using AI or placeholder scoring"""
        
        scoring_config = self.config['scoring']
        
        if scoring_config['method'] == 'ai' and os.getenv('OPENAI_API_KEY'):
            logger.info("Using AI-powered scoring (Phase 2)")
            
            try:
                from scoring.ai_scorer import AIScorer
                
                # Initialize AI scorer
                scorer = AIScorer()
                
                # Convert articles to dicts for scoring
                article_dicts = [self._article_to_dict(a) for a in articles]
                
                # Score with AI
                scored_dicts = scorer.score_articles(article_dicts)
                
                # Update article objects with AI scores and categories
                for article, scored_dict in zip(articles, scored_dicts):
                    article.score = scored_dict.get('ai_score', 5.0)
                    if scored_dict.get('ai_category'):
                        article.category = scored_dict['ai_category']
                    if scored_dict.get('image_url'):
                        article.image_url = scored_dict['image_url']
                
            except Exception as e:
                logger.error(f"AI scoring failed: {e}")
                logger.info("Falling back to placeholder scoring")
                articles = assign_placeholder_scores(
                    articles,
                    default_score=scoring_config.get('default_score', 8.0),
                    variance=scoring_config.get('random_variance', 1.5)
                )
        
        elif scoring_config['method'] == 'placeholder':
            logger.info("Using placeholder scoring (Phase 1)")
            
            articles = assign_placeholder_scores(
                articles,
                default_score=scoring_config['default_score'],
                variance=scoring_config['random_variance']
            )
        else:
            logger.warning("Unknown scoring method, using placeholder")
            articles = assign_placeholder_scores(articles)
        
        # Sort by score and limit
        articles = sorted(articles, key=lambda a: a.score or 0, reverse=True)
        max_articles = self.config['pipeline']['max_articles_per_day']
        articles = articles[:max_articles]
        
        logger.info(f"✓ Selected top {len(articles)} articles")
        
        # Show score distribution
        scores = [a.score for a in articles if a.score]
        if scores:
            avg_score = sum(scores) / len(scores)
            logger.info(f"  Score range: {min(scores):.1f} - {max(scores):.1f} (avg: {avg_score:.1f})")
        
        return articles
    
    def _article_to_dict(self, article) -> dict:
        """Convert Article object to dictionary for AI scoring"""
        # Extract summary from content (first 300 chars)
        summary = article.content[:300] if article.content else ""
        
        return {
            'title': article.title,
            'url': article.url,
            'summary': summary,
            'content': article.content,
            'source': article.source,
            'category': article.category,
            'published': article.published,
            'author': getattr(article, 'author', None),
            'word_count': len(article.content.split()) if article.content else 0,
            'image_url': getattr(article, 'image_url', None)
        }
    
    def _generate_output(self, articles: list):
        """Generate JSON output files"""
        
        output_dir = self.config['output']['content_dir']
        generator = ContentGenerator(output_dir=output_dir)
        
        # Generate latest.json for homepage
        today_str = datetime.now().strftime("%B %d, %Y")
        latest_content = generator.generate_latest(articles, date_str=today_str)
        
        # Generate daily archive
        daily_content = generator.generate_daily_archive(articles)
        
        logger.info(f"✓ Generated content files:")
        logger.info(f"  - {output_dir}/latest.json")
        logger.info(f"  - {output_dir}/daily/{datetime.now().strftime('%Y-%m-%d')}.json")
        
        return latest_content, daily_content


def main():
    """Main entry point"""
    
    # Run the pipeline
    pipeline = TechPulsePipeline()
    success = pipeline.run()
    
    if success:
        print("\n🎉 Success! Check the 'content' directory for generated files.")
        print("\n📋 Next steps:")
        print("  1. Review content/latest.json")
        print("  2. Test the website with the new data")
        print("  3. Deploy to production")
        sys.exit(0)
    else:
        print("\n❌ Pipeline failed. Check pipeline.log for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
