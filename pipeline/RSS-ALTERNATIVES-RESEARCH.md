# RSS Alternatives Research: Axios, Every.to, Superhuman AI

**Date**: November 30, 2025  
**Status**: Investigation Complete

## Executive Summary

After thorough investigation, **none of these three sources have working RSS feeds**. However, I've identified alternative methods to retrieve their content:

| Source | RSS Available? | Alternative Method | Difficulty | Recommended |
|--------|---------------|-------------------|------------|-------------|
| **Axios** | ❌ No (stale 2021 data) | Sitemap scraping | Medium | ⚠️ Maybe |
| **Every.to** | ❌ No | HTML scraping | High | ❌ No |
| **Superhuman AI** | ❌ No | Sitemap + HTML scraping | Medium | ✅ Yes |

---

## Detailed Findings

### 1. Axios Technology

**RSS Status**: ❌ **BROKEN**
- API endpoint `https://api.axios.com/feed/technology` returns articles from Feb 2021
- Feed appears abandoned or not actively maintained
- Cloudflare protection blocks some automated access attempts

**Alternative Options**:

#### Option A: Sitemap Scraping (Recommended)
```python
# Axios organizes sitemaps by category and month
# Example: https://www.axios.com/sitemaps/technology/nov-2025.xml
# Contains URLs to all tech articles for that month
```

**Pros**:
- Official sitemap, semi-structured data
- Organized by category and date
- Reliable URLs

**Cons**:
- Requires monthly sitemap checking
- No article metadata (would need to scrape each URL)
- More API calls required

#### Option B: Page Scraping
- Scrape `https://www.axios.com/technology` directly
- JavaScript-rendered content makes this difficult
- Cloudflare protection may block automated requests

**Recommendation**: ⚠️ **Use sitemap method if critical, otherwise skip**
- Axios coverage often overlaps with other tech news sources
- Implementation complexity may not justify the value
- Consider alternative sources like TechCrunch, VentureBeat (already working)

---

### 2. Every.to

**RSS Status**: ❌ **NO RSS AVAILABLE**
- Custom-built platform (not Substack, beehiiv, or Ghost)
- No RSS feed endpoint found
- Website built with Next.js (JavaScript-rendered)

**Platform Details**:
- Built by Dan Shipper and Nathan Baschez
- Left Substack in 2021 for custom solution
- Sitemap returns 500 error

**Alternative Options**:

#### Option A: Archive Page Scraping
```python
# Potential URL: https://every.to/archive or similar
# Would need to identify article list page
```

**Cons**:
- JavaScript-rendered content
- No structured data format
- Requires headless browser (Selenium/Playwright)
- High maintenance overhead
- Rate limiting concerns

#### Option B: Newsletter Signup
- Sign up for email newsletter
- Parse incoming emails
- Not suitable for real-time pipeline

**Recommendation**: ❌ **SKIP - NOT WORTH THE EFFORT**
- Every.to publishes infrequently
- Content is long-form essays, not daily news
- Better suited for manual curation
- High technical complexity for low article volume

---

### 3. Superhuman AI

**RSS Status**: ❌ **NO RSS AVAILABLE**
- Hosted on beehiiv but RSS feed not enabled by publisher
- Subdomain `superhuman.beehiiv.com` redirects to `www.superhuman.ai`
- Content accessible at `www.superhuman.ai/p/{slug}`

**Good News**: Structured sitemap available!
```
https://www.superhuman.ai/sitemap.xml
```

**Alternative Options**:

#### Option A: Sitemap + HTML Scraping (Recommended)
```python
# 1. Fetch sitemap: https://www.superhuman.ai/sitemap.xml
# 2. Filter URLs matching pattern: /p/{article-slug}
# 3. Scrape article metadata from each URL
# 4. Extract: title, date, excerpt from HTML/JSON-LD
```

**Implementation Details**:
```python
# Articles have embedded JSON-LD metadata:
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "...",
  "datePublished": "...",
  "description": "..."
}
</script>
```

**Pros**:
- Reliable sitemap with all article URLs
- Structured JSON-LD metadata in HTML
- Daily publication schedule (1 article/day)
- Well-organized content

**Cons**:
- Requires HTTP requests for each article (10-20/day)
- More complex than RSS parsing
- Could break if site structure changes

**Recommendation**: ✅ **IMPLEMENT THIS**
- High-quality AI news source
- Structured data available
- Worth the extra implementation effort
- Reasonable article volume (~30/month)

---

## Implementation Recommendations

### Priority 1: Implement Superhuman AI Scraper

Create a new module: `pipeline/ingestion/html_fetcher.py`

```python
"""
HTML Article Fetcher
For sites without RSS feeds but with structured sitemaps
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import json
import logging

logger = logging.getLogger(__name__)

class HTMLArticleFetcher:
    """Fetch articles from HTML pages with sitemap support"""
    
    def __init__(self, user_agent='TechPulse/1.0'):
        self.user_agent = user_agent
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
    
    def fetch_from_sitemap(self, sitemap_url: str, url_pattern: str, 
                          source_name: str, category: str,
                          lookback_hours: int = 48):
        """
        Fetch articles from sitemap
        
        Args:
            sitemap_url: URL to XML sitemap
            url_pattern: Regex pattern to match article URLs
            source_name: Name of source
            category: Content category
            lookback_hours: Only fetch recent articles
        """
        articles = []
        
        # Fetch sitemap
        response = self.session.get(sitemap_url, timeout=30)
        response.raise_for_status()
        
        # Parse sitemap XML
        root = ET.fromstring(response.content)
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Extract URLs matching pattern
        import re
        pattern = re.compile(url_pattern)
        
        urls = []
        for url_elem in root.findall('.//ns:url/ns:loc', namespace):
            url = url_elem.text
            if pattern.search(url):
                urls.append(url)
        
        logger.info(f"Found {len(urls)} potential articles in sitemap")
        
        # Fetch and parse each article
        for url in urls[:50]:  # Limit to recent 50
            try:
                article = self._scrape_article(url, source_name, category)
                if article:
                    # Check if recent enough
                    cutoff = datetime.now() - timedelta(hours=lookback_hours)
                    if article.published and article.published >= cutoff:
                        articles.append(article)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        logger.info(f"✓ Fetched {len(articles)} articles from {source_name}")
        return articles
    
    def _scrape_article(self, url: str, source_name: str, category: str):
        """Scrape a single article page"""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Try to extract JSON-LD structured data first
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                
                title = data.get('headline') or data.get('name')
                description = data.get('description')
                date_str = data.get('datePublished')
                
                published = None
                if date_str:
                    from dateutil import parser
                    published = parser.parse(date_str)
                
                if title and description:
                    return Article(
                        title=title,
                        url=url,
                        published=published or datetime.now(),
                        content=description,
                        source=source_name,
                        category=category
                    )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error parsing JSON-LD: {e}")
        
        # Fallback: try meta tags
        title = soup.find('meta', property='og:title')
        description = soup.find('meta', property='og:description')
        
        if title and description:
            return Article(
                title=title['content'],
                url=url,
                published=datetime.now(),  # No date available
                content=description['content'],
                source=source_name,
                category=category
            )
        
        return None
```

### Priority 2: Update sources.yaml

```yaml
# HTML Scraping Sources (no RSS available)
html_sources:
  - name: "Superhuman AI"
    sitemap_url: "https://www.superhuman.ai/sitemap.xml"
    url_pattern: "/p/[^/]+$"
    type: "html"
    category: "ai_news"
    priority: "high"
    description: "AI tools and news (HTML scraping via sitemap)"
```

### Priority 3: Update run_pipeline.py

```python
# Add HTML fetcher support
from ingestion.html_fetcher import HTMLArticleFetcher

# Fetch HTML-only sources
html_sources = [
    {
        'sitemap_url': 'https://www.superhuman.ai/sitemap.xml',
        'url_pattern': r'/p/[^/]+$',
        'name': 'Superhuman AI',
        'category': 'ai_news'
    }
]

html_fetcher = HTMLArticleFetcher()
for source in html_sources:
    html_articles = html_fetcher.fetch_from_sitemap(**source)
    all_articles.extend(html_articles)
```

---

## Cost-Benefit Analysis

| Source | Implementation Time | Maintenance | Article Volume | Content Quality | Worth It? |
|--------|-------------------|-------------|----------------|-----------------|-----------|
| Superhuman AI | 3-4 hours | Low | ~30/month | High | ✅ **YES** |
| Axios | 4-5 hours | Medium | ~60/month | Medium | ⚠️ **MAYBE** |
| Every.to | 6-8 hours | High | ~8/month | High | ❌ **NO** |

---

## Alternative Solution: Use Existing Working Sources

You already have excellent coverage with:
- ✅ **VentureBeat AI** (working, recent)
- ✅ **TechCrunch AI** (working, recent)
- ✅ **The Rundown AI** (fixed, working)
- ✅ **Hacker News** (working)
- ✅ **OpenAI Blog** (working)
- ✅ **Anthropic News** (working)
- ✅ **AI News** (working)
- ✅ **Latent Space** (podcast RSS)

**Suggestion**: Add these RSS sources instead:
```yaml
# Better alternatives with working RSS feeds
- name: "MIT Technology Review AI"
  url: "https://www.technologyreview.com/feed/"
  type: "rss"
  category: "ai_news"
  priority: "high"

- name: "The Verge AI"
  url: "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"
  type: "rss"
  category: "ai_news"
  priority: "high"

- name: "Ars Technica AI"
  url: "https://feeds.arstechnica.com/arstechnica/technology-lab"
  type: "rss"
  category: "tech_news"
  priority: "medium"
```

---

## Final Recommendation

1. ✅ **Implement Superhuman AI scraper** - Worth the effort for daily AI news
2. ⚠️ **Skip Axios for now** - Coverage overlap with existing sources
3. ❌ **Skip Every.to** - Too complex for low article volume
4. ✅ **Add MIT Tech Review, The Verge AI** - Working RSS, excellent coverage

**Total Development Time**: 3-4 hours for Superhuman AI scraper  
**Expected Benefit**: +1 daily AI news source, ~30 additional articles/month
