"""
Image Extraction from Articles

Extracts featured images from article content and RSS feeds
"""

import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImageExtractor:
    """
    Extracts featured images from articles
    """
    
    def __init__(self):
        self.timeout = 10
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) TechPulse/1.0'
    
    def extract_image(self, article: Dict) -> Optional[str]:
        """
        Extract featured image URL from article
        
        Priority:
        1. RSS feed image (if available)
        2. Open Graph image from URL
        3. First substantial image in content
        
        Args:
            article: Article dictionary
            
        Returns:
            Image URL or None
        """
        # Check if RSS feed already has an image
        if article.get('image_url'):
            return article['image_url']
        
        # Try to extract from article URL
        url = article.get('url')
        if not url:
            return None
        
        try:
            # Get Open Graph image
            og_image = self._get_og_image(url)
            if og_image:
                return og_image
            
            # Try to find image in content
            if article.get('content'):
                content_image = self._extract_from_content(article['content'], url)
                if content_image:
                    return content_image
            
        except Exception as e:
            logger.debug(f"Error extracting image from {url}: {e}")
        
        return None
    
    def _get_og_image(self, url: str) -> Optional[str]:
        """
        Extract Open Graph image from URL
        
        Args:
            url: Article URL
            
        Returns:
            Image URL or None
        """
        try:
            headers = {'User-Agent': self.user_agent}
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image['content']
                return self._normalize_url(img_url, url)
            
            # Try Twitter card image
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                img_url = twitter_image['content']
                return self._normalize_url(img_url, url)
            
            # Try article:image
            article_image = soup.find('meta', property='article:image')
            if article_image and article_image.get('content'):
                img_url = article_image['content']
                return self._normalize_url(img_url, url)
            
        except Exception as e:
            logger.debug(f"Error fetching OG image: {e}")
        
        return None
    
    def _extract_from_content(self, content: str, base_url: str) -> Optional[str]:
        """
        Extract first substantial image from HTML content
        
        Args:
            content: HTML content
            base_url: Base URL for relative links
            
        Returns:
            Image URL or None
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all images
            images = soup.find_all('img')
            
            for img in images:
                src = img.get('src') or img.get('data-src')
                if not src:
                    continue
                
                # Skip small images (likely icons/logos)
                width = img.get('width')
                height = img.get('height')
                
                if width and height:
                    try:
                        if int(width) < 200 or int(height) < 200:
                            continue
                    except (ValueError, TypeError):
                        pass
                
                # Skip common icon/logo patterns
                if any(x in src.lower() for x in ['icon', 'logo', 'avatar', 'emoji', 'badge']):
                    continue
                
                # Normalize URL
                img_url = self._normalize_url(src, base_url)
                if self._is_valid_image_url(img_url):
                    return img_url
            
        except Exception as e:
            logger.debug(f"Error extracting from content: {e}")
        
        return None
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """
        Normalize relative URLs to absolute
        
        Args:
            url: Image URL (possibly relative)
            base_url: Base URL for resolving
            
        Returns:
            Absolute URL
        """
        if url.startswith('//'):
            return 'https:' + url
        elif url.startswith('/'):
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{url}"
        elif not url.startswith('http'):
            return urljoin(base_url, url)
        return url
    
    def _is_valid_image_url(self, url: str) -> bool:
        """
        Check if URL looks like a valid image
        
        Args:
            url: Image URL
            
        Returns:
            True if valid
        """
        if not url:
            return False
        
        # Check extension
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
        url_lower = url.lower()
        
        if any(url_lower.endswith(ext) for ext in image_extensions):
            return True
        
        # Check if it's a typical image hosting pattern
        if any(x in url_lower for x in ['images', 'img', 'media', 'cdn', 'uploads']):
            return True
        
        return False
    
    def add_images_to_articles(self, articles: list) -> list:
        """
        Add image URLs to articles that don't have them
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Articles with image_url added
        """
        logger.info(f"Extracting images for {len(articles)} articles...")
        
        images_found = 0
        for article in articles:
            if not article.get('image_url'):
                image_url = self.extract_image(article)
                if image_url:
                    article['image_url'] = image_url
                    images_found += 1
        
        logger.info(f"✓ Found images for {images_found}/{len(articles)} articles")
        
        return articles


def main():
    """Test the image extractor"""
    test_article = {
        'title': 'Test Article',
        'url': 'https://openai.com/blog/chatgpt',
        'content': '<html><body><img src="/images/test.jpg" width="800" height="600"></body></html>'
    }
    
    extractor = ImageExtractor()
    image_url = extractor.extract_image(test_article)
    
    print(f"Extracted image: {image_url}")


if __name__ == '__main__':
    main()
