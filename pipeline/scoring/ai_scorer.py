"""
AI-Powered Content Scoring System

Uses OpenAI embeddings to match articles against your taste profile
"""

import os
import yaml
import logging
from typing import List, Dict, Optional
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIScorer:
    """
    Scores articles based on AI embeddings and taste profile matching
    """
    
    def __init__(self, profile_path: str = None):
        """
        Initialize the AI scorer
        
        Args:
            profile_path: Path to taste_profile.yaml
        """
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        
        # Load taste profile
        if profile_path is None:
            profile_path = Path(__file__).parent / 'taste_profile.yaml'
        
        with open(profile_path, 'r') as f:
            self.profile = yaml.safe_load(f)
        
        logger.info("✓ AI Scorer initialized")
        
        # Cache for embeddings (to save API calls)
        self.embedding_cache = {}
        
        # Generate profile embeddings
        self._generate_profile_embeddings()
    
    def _generate_profile_embeddings(self):
        """Generate embeddings for taste profile topics"""
        logger.info("Generating taste profile embeddings...")
        
        self.topic_embeddings = []
        self.topic_weights = []
        self.topic_names = []
        
        # Process priority topics
        for topic in self.profile.get('priority_topics', []):
            topic_text = f"{topic['name']}: {' '.join(topic['keywords'])}"
            embedding = self._get_embedding(topic_text)
            
            self.topic_embeddings.append(embedding)
            self.topic_weights.append(topic['weight'])
            self.topic_names.append(topic['name'])
        
        # Process secondary topics
        for topic in self.profile.get('secondary_topics', []):
            topic_text = f"{topic['name']}: {' '.join(topic['keywords'])}"
            embedding = self._get_embedding(topic_text)
            
            self.topic_embeddings.append(embedding)
            self.topic_weights.append(topic['weight'])
            self.topic_names.append(topic['name'])
        
        # Process avoid topics (negative weights)
        for topic in self.profile.get('avoid_topics', []):
            topic_text = f"{topic['name']}: {' '.join(topic['keywords'])}"
            embedding = self._get_embedding(topic_text)
            
            self.topic_embeddings.append(embedding)
            self.topic_weights.append(topic['weight'])
            self.topic_names.append(f"AVOID: {topic['name']}")
        
        logger.info(f"✓ Generated {len(self.topic_embeddings)} topic embeddings")
    
    def _get_embedding(self, text: str, model: str = "text-embedding-3-small") -> np.ndarray:
        """
        Get embedding for text using OpenAI API
        
        Args:
            text: Text to embed
            model: OpenAI embedding model
            
        Returns:
            Embedding vector as numpy array
        """
        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            # Clean text
            text = text.replace("\n", " ").strip()
            if not text:
                return np.zeros(1536)  # Default embedding size
            
            # Get embedding from OpenAI
            response = self.client.embeddings.create(
                input=[text],
                model=model
            )
            
            embedding = np.array(response.data[0].embedding)
            
            # Cache it
            self.embedding_cache[text] = embedding
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return np.zeros(1536)
    
    def score_article(self, article: Dict) -> tuple:
        """
        Score a single article based on taste profile
        
        Args:
            article: Article dictionary with title, summary, source, etc.
            
        Returns:
            Tuple of (score, best_matching_category)
        """
        # Build article text for embedding
        article_text = self._build_article_text(article)
        
        # Get article embedding
        article_embedding = self._get_embedding(article_text)
        
        # Calculate topic relevance score and get best category
        topic_score, best_category = self._calculate_topic_relevance(article_embedding, return_category=True)
        
        # Calculate source trust score
        source_score = self._calculate_source_trust(article.get('source', ''))
        
        # Calculate content quality score
        quality_score = self._calculate_content_quality(article)
        
        # Calculate recency score
        recency_score = self._calculate_recency_score(article.get('published'))
        
        # Calculate uniqueness score (for now, placeholder)
        uniqueness_score = 0.7
        
        # Combine scores based on weights
        weights = self.profile.get('scoring', {})
        final_score = (
            topic_score * weights.get('topic_relevance', 0.4) +
            source_score * weights.get('source_trust', 0.15) +
            quality_score * weights.get('content_quality', 0.2) +
            recency_score * weights.get('recency', 0.15) +
            uniqueness_score * weights.get('uniqueness', 0.1)
        )
        
        # Scale to 0-10
        final_score = max(0, min(10, final_score * 10))
        
        return round(final_score, 1), best_category
    
    def _build_article_text(self, article: Dict) -> str:
        """Build comprehensive text representation of article"""
        parts = []
        
        if article.get('title'):
            parts.append(f"Title: {article['title']}")
        
        if article.get('summary'):
            parts.append(f"Summary: {article['summary']}")
        
        if article.get('category'):
            parts.append(f"Category: {article['category']}")
        
        return " | ".join(parts)
    
    def _calculate_topic_relevance(self, article_embedding: np.ndarray, return_category: bool = False):
        """Calculate how well article matches topic interests"""
        if len(self.topic_embeddings) == 0:
            if return_category:
                return 0.5, "General"
            return 0.5
        
        # Calculate cosine similarity with each topic
        similarities = []
        for topic_emb, weight in zip(self.topic_embeddings, self.topic_weights):
            sim = cosine_similarity(
                article_embedding.reshape(1, -1),
                topic_emb.reshape(1, -1)
            )[0][0]
            
            # Apply topic weight
            weighted_sim = sim * weight
            similarities.append(weighted_sim)
        
        # Use max similarity (best topic match)
        max_sim = max(similarities)
        best_idx = similarities.index(max_sim)
        best_topic_name = self.topic_names[best_idx]
        
        # Clean up category name (remove "AVOID:" prefix)
        if best_topic_name.startswith("AVOID:"):
            best_topic_name = "General"
        
        # Scale from [-1, 1] to [0, 1]
        score = (max_sim + 1) / 2
        
        if return_category:
            return max(0, min(1, score)), best_topic_name
        return max(0, min(1, score))
    
    def _calculate_source_trust(self, source: str) -> float:
        """Calculate source trust score"""
        source_weights = self.profile.get('source_weights', {})
        
        # Find matching source
        for source_name, weight in source_weights.items():
            if source_name.lower() in source.lower():
                # Scale weight to 0-1 range (assuming weights are 0.5-1.2)
                return (weight - 0.5) / 0.7
        
        # Default for unknown sources
        return 0.5
    
    def _calculate_content_quality(self, article: Dict) -> float:
        """Calculate content quality score"""
        score = 0.5  # Base score
        
        # Has substantial summary?
        summary = article.get('summary', '')
        if len(summary) > 200:
            score += 0.2
        elif len(summary) > 100:
            score += 0.1
        
        # Has good word count?
        word_count = article.get('word_count', 0)
        if word_count > 1000:
            score += 0.2
        elif word_count > 500:
            score += 0.1
        
        # Has author?
        if article.get('author'):
            score += 0.05
        
        # Has image?
        if article.get('image_url'):
            score += 0.05
        
        return min(1.0, score)
    
    def _calculate_recency_score(self, published_date) -> float:
        """Calculate recency score - newer is better"""
        if not published_date:
            return 0.5
        
        from datetime import datetime, timedelta
        
        try:
            if isinstance(published_date, str):
                # Try parsing ISO format
                pub_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))
            else:
                pub_date = published_date
            
            now = datetime.now(pub_date.tzinfo)
            age_hours = (now - pub_date).total_seconds() / 3600
            
            # Score based on age
            if age_hours < 6:
                return 1.0  # Very recent
            elif age_hours < 24:
                return 0.9  # Today
            elif age_hours < 48:
                return 0.7  # Yesterday
            elif age_hours < 168:  # 1 week
                return 0.5
            else:
                return 0.3  # Older
                
        except Exception as e:
            logger.debug(f"Error calculating recency: {e}")
            return 0.5
    
    def score_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Score multiple articles and add scores to them
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Articles with 'ai_score' and 'ai_category' added
        """
        logger.info(f"Scoring {len(articles)} articles with AI...")
        
        scored_articles = []
        for article in articles:
            try:
                score, category = self.score_article(article)
                article['ai_score'] = score
                article['ai_category'] = category
                scored_articles.append(article)
                
            except Exception as e:
                logger.error(f"Error scoring article '{article.get('title', 'Unknown')}': {e}")
                article['ai_score'] = 5.0  # Default score
                article['ai_category'] = "General"
                scored_articles.append(article)
        
        # Sort by score (highest first)
        scored_articles.sort(key=lambda x: x.get('ai_score', 0), reverse=True)
        
        logger.info(f"✓ Scored articles: {len(scored_articles)} total")
        if scored_articles:
            logger.info(f"  Top score: {scored_articles[0].get('ai_score', 0)}")
            logger.info(f"  Top article: {scored_articles[0].get('title', 'Unknown')[:60]}")
            logger.info(f"  Top category: {scored_articles[0].get('ai_category', 'Unknown')}")
        
        return scored_articles


def main():
    """Test the AI scorer"""
    # Test article
    test_article = {
        'title': 'New GPT-5 Model Released with Breakthrough Benchmarks',
        'summary': 'OpenAI releases GPT-5 with significant improvements in reasoning and coding capabilities. Achieves 95% on HumanEval and shows strong performance on enterprise use cases.',
        'source': 'OpenAI Blog',
        'category': 'AI News',
        'published': '2024-11-26T10:00:00Z',
        'word_count': 1200
    }
    
    # Initialize scorer
    scorer = AIScorer()
    
    # Score article
    score = scorer.score_article(test_article)
    
    print(f"\n{'='*60}")
    print(f"Article: {test_article['title']}")
    print(f"Score: {score}/10")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
