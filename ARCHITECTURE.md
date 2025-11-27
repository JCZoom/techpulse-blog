# TechPulse Automated Curation System - Architecture

## Executive Summary

This document outlines the architecture for an **AI-powered automated content curation system** that will populate your TechPulse website with daily curated tech and AI news. The system ingests content from multiple sources, scores it against your personal taste profile, generates enriched summaries, and produces structured JSON files that your static site consumes.

**Key Goal:** Zero manual curation - just approve a GitHub PR each morning.

---

## Current State Analysis

### Existing Website Architecture
- **Platform:** Static HTML/CSS/JS site
- **Hosting:** Cloudflare Pages (deployment target)
- **Repository:** GitHub
- **Content Structure:** Currently manual HTML content
- **Brand:** TechPulse (already aligned with your vision!)

### Key Files
- `index.html` - Homepage with hero, article grid, categories
- `article.html` - Full article template
- `archive.html` - Historical articles by month
- `category.html` - Topic-specific pages
- `styles.css` - Complete styling
- `script.js` - Interactive features

---

## Proposed System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DAILY AUTOMATION PIPELINE                    │
│                     (GitHub Actions - Cron)                      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │    PHASE 1: Content Ingestion             │
         │  ┌─────────────────────────────────────┐  │
         │  │ • RSS Feeds (HN, TC, VentureBeat)   │  │
         │  │ • NewsAPI / GNews API               │  │
         │  │ • YouTube RSS feeds                 │  │
         │  │ • Reddit APIs (r/machinelearning)   │  │
         │  │ • Company Blogs (OpenAI, Anthropic) │  │
         │  │ • Podcast RSS feeds                 │  │
         │  └─────────────────────────────────────┘  │
         └───────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │    PHASE 2: Deduplication & Filtering     │
         │  ┌─────────────────────────────────────┐  │
         │  │ • URL/title fuzzy matching          │  │
         │  │ • Content length filtering          │  │
         │  │ • Quality score (basic heuristics)  │  │
         │  │ • Recency filtering (24-72 hrs)     │  │
         │  └─────────────────────────────────────┘  │
         └───────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │    PHASE 3: Taste Profile Scoring         │
         │  ┌─────────────────────────────────────┐  │
         │  │ 1. Embedding Generation             │  │
         │  │    (OpenAI text-embedding-3-small)  │  │
         │  │                                     │  │
         │  │ 2. Similarity to Your Profile       │  │
         │  │    (Cosine similarity to seed list) │  │
         │  │                                     │  │
         │  │ 3. LLM Relevance Refinement         │  │
         │  │    (GPT-4o-mini batch scoring)      │  │
         │  │                                     │  │
         │  │ 4. Combined Score (1-10 scale)      │  │
         │  └─────────────────────────────────────┘  │
         └───────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │    PHASE 4: AI Enrichment                 │
         │  ┌─────────────────────────────────────┐  │
         │  │ • Generate TechPulse-style summary  │  │
         │  │ • Extract key insights              │  │
         │  │ • Categorize (AI, Startups, etc.)   │  │
         │  │ • Assign to section (Hero, Grid)    │  │
         │  │ • Estimate read time                │  │
         │  │ • Generate better headlines         │  │
         │  └─────────────────────────────────────┘  │
         └───────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │    PHASE 5: Content Generation            │
         │  ┌─────────────────────────────────────┐  │
         │  │ Generate JSON files:                │  │
         │  │ • content/daily/YYYY-MM-DD.json     │  │
         │  │ • content/latest.json               │  │
         │  │ • content/categories/*.json         │  │
         │  │ • content/archive/YYYY/MM.json      │  │
         │  └─────────────────────────────────────┘  │
         └───────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────┐
         │    PHASE 6: GitHub PR Creation            │
         │  ┌─────────────────────────────────────┐  │
         │  │ • Create branch                     │  │
         │  │ • Commit JSON files                 │  │
         │  │ • Open PR with summary              │  │
         │  │ • Tag for review                    │  │
         │  └─────────────────────────────────────┘  │
         └───────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  YOU REVIEW & MERGE  │
                    └──────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  Cloudflare Pages    │
                    │  Auto-Deploy         │
                    └──────────────────────┘
```

---

## Detailed Component Architecture

### 1. Data Ingestion Module (`pipeline/ingestion/`)

**Purpose:** Collect raw content from diverse sources

**Components:**
```
pipeline/ingestion/
├── base.py              # Abstract feed interface
├── rss_fetcher.py       # RSS feed handler
├── newsapi_fetcher.py   # NewsAPI integration
├── youtube_fetcher.py   # YouTube RSS/API
├── reddit_fetcher.py    # Reddit API wrapper
├── blog_scraper.py      # Custom blog scraper
└── sources.yaml         # Source configuration
```

**Key Features:**
- Unified Article schema (title, url, content, published, source)
- Parallel fetching with asyncio
- Rate limiting and retries
- Source metadata tracking
- Error handling and logging

**Data Sources (Initial Set):**
```yaml
rss_feeds:
  - url: https://news.ycombinator.com/rss
    name: Hacker News
    category: general_tech
  - url: https://techcrunch.com/feed/
    name: TechCrunch
    category: startups
  - url: https://venturebeat.com/feed/
    name: VentureBeat
    category: ai

apis:
  - name: NewsAPI
    endpoint: https://newsapi.org/v2/everything
    topics: [artificial intelligence, machine learning, tech startups]
  
company_blogs:
  - url: https://openai.com/blog/rss
    name: OpenAI Blog
  - url: https://www.anthropic.com/rss
    name: Anthropic
```

---

### 2. Content Processing Module (`pipeline/processing/`)

**Purpose:** Deduplicate, filter, and normalize content

**Components:**
```
pipeline/processing/
├── deduplicator.py      # URL/content similarity detection
├── content_extractor.py # Full text extraction (readability)
├── quality_filter.py    # Content quality scoring
└── normalizer.py        # Standardize article format
```

**Deduplication Strategy:**
- URL exact match (primary)
- Title fuzzy matching (Levenshtein distance > 0.85)
- Content fingerprinting (MinHash for near-duplicate detection)

**Quality Filters:**
- Minimum word count (200 words)
- Not paywalled (detect paywall patterns)
- Valid publication date (last 72 hours default)
- Language detection (English only initially)

---

### 3. Taste Profile System (`pipeline/taste_profile/`)

**Purpose:** Score articles based on your preferences

**Components:**
```
pipeline/taste_profile/
├── profile_manager.py   # Load/update taste profile
├── embedder.py          # Generate embeddings
├── scorer.py            # Compute relevance scores
└── seed_articles.json   # Your curated examples
```

**Scoring Algorithm:**
```python
# Pseudo-code
def score_article(article, profile):
    # Step 1: Embedding similarity (fast, batch)
    embedding = get_embedding(article.content)
    cosine_score = cosine_similarity(embedding, profile.centroid)
    
    # Step 2: Keyword/topic match
    topic_score = match_topics(article, profile.preferred_topics)
    
    # Step 3: LLM refinement (for top candidates only)
    if cosine_score > 0.7:
        llm_score = llm_judge(article, profile.examples)
    else:
        llm_score = 0
    
    # Combined score
    final_score = (cosine_score * 0.5 + 
                   topic_score * 0.2 + 
                   llm_score * 0.3)
    
    return final_score * 10  # Scale to 1-10
```

**Seed Articles Format:**
```json
{
  "seed_articles": [
    {
      "title": "Example of article I like",
      "url": "https://...",
      "why_liked": "Deep technical analysis, clear writing",
      "category": "ai_infrastructure",
      "score": 9
    }
  ],
  "preferred_topics": [
    "ai infrastructure", "LLM architecture", "AI agents",
    "startup launches", "breakthrough research", "ai policy"
  ],
  "anti_patterns": [
    "clickbait", "low-signal news", "PR fluff"
  ]
}
```

---

### 4. AI Enrichment Module (`pipeline/enrichment/`)

**Purpose:** Generate summaries, categorize, and enhance articles

**Components:**
```
pipeline/enrichment/
├── summarizer.py        # Generate TechPulse summaries
├── categorizer.py       # Classify into topics
├── layout_mapper.py     # Assign to site sections
├── headline_generator.py # Improve headlines
└── prompts/
    ├── summary_prompt.txt
    ├── category_prompt.txt
    └── headline_prompt.txt
```

**Summary Generation Prompt:**
```
You are a tech journalist writing for TechPulse, a curated daily tech newsletter.
Write a concise 2-3 sentence summary of this article that:
- Captures the key development or announcement
- Explains why it matters
- Uses active voice and clear language
- Avoids marketing fluff

Article: {content}

Summary:
```

**Categories:**
- AI Infrastructure
- AI Models
- AI Agents
- Startups & Business
- Hardware & Chips
- Policy & Regulation
- Climate Tech
- Developer Tools
- Culture & Opinion

**Section Assignment Logic:**
```python
def assign_section(article):
    if article.score >= 9:
        return "hero"  # Featured story
    elif article.score >= 7.5:
        return "headlines"  # Today's Headlines grid
    elif article.category == "video":
        return "video_spotlight"
    elif article.depth == "deep_dive":
        return "deep_reads"
    else:
        return "latest"
```

---

### 5. Content Output Module (`pipeline/output/`)

**Purpose:** Generate structured JSON for website consumption

**Components:**
```
pipeline/output/
├── json_generator.py    # Create content JSON files
├── html_generator.py    # Optional: generate HTML snippets
└── schema.py            # JSON schema definitions
```

**JSON Schema:**

**`content/latest.json`** (Homepage data):
```json
{
  "generated_at": "2024-11-26T08:00:00Z",
  "date": "November 26, 2024",
  "hero": {
    "title": "Alphabet Races Toward $4 Trillion Valuation",
    "subtitle": "The surge reflects growing investor confidence...",
    "category": "AI Infrastructure",
    "url": "https://...",
    "author": "AI Curator",
    "read_time": "7 min",
    "score": 9.2
  },
  "headlines": [
    {
      "title": "Google's Gemini 3 Pro Crushes Benchmarks",
      "excerpt": "Google's Gemini 3 Pro sets new records...",
      "category": "AI Models",
      "url": "https://...",
      "read_time": "9 min",
      "published": "2024-11-26T06:00:00Z",
      "score": 8.7
    }
  ],
  "video_spotlight": {
    "title": "The Future of AI Reasoning",
    "url": "https://youtube.com/...",
    "thumbnail": "https://...",
    "duration": "15:23"
  },
  "categories": [
    {
      "name": "AI Infrastructure",
      "slug": "ai-infrastructure",
      "count": 12,
      "icon": "🏗️"
    }
  ]
}
```

**`content/daily/2024-11-26.json`** (Archive data):
```json
{
  "date": "2024-11-26",
  "articles": [
    {
      "id": "2024-11-26-01",
      "title": "...",
      "excerpt": "...",
      "category": "AI Models",
      "url": "...",
      "score": 9.2,
      "ingested_from": "VentureBeat",
      "published": "2024-11-26T06:00:00Z"
    }
  ],
  "stats": {
    "total_ingested": 247,
    "total_scored": 158,
    "selected": 15,
    "avg_score": 8.1
  }
}
```

---

### 6. GitHub Integration Module (`pipeline/github/`)

**Purpose:** Create automated pull requests

**Components:**
```
pipeline/github/
├── pr_creator.py        # GitHub API wrapper
├── commit_builder.py    # Stage and commit changes
└── pr_template.md       # PR description template
```

**PR Workflow:**
```python
def create_daily_pr(date, content_files):
    # 1. Create branch
    branch_name = f"daily-content-{date}"
    
    # 2. Commit files
    for file_path, content in content_files.items():
        commit_file(branch_name, file_path, content)
    
    # 3. Create PR
    pr_body = generate_pr_summary(content_files)
    create_pull_request(
        title=f"📰 TechPulse Daily Content - {date}",
        body=pr_body,
        head=branch_name,
        base="main"
    )
```

**PR Template:**
```markdown
## 📰 TechPulse Daily Content - November 26, 2024

**Summary:** 15 articles selected from 247 sources

### 🏆 Hero Story
- **Alphabet Races Toward $4 Trillion Valuation** (score: 9.2)
  AI Infrastructure | 7 min read

### 📊 Headlines (5)
- Google's Gemini 3 Pro Crushes Benchmarks (8.7)
- OpenAI Launches GPT-4 Turbo with Vision (8.5)
- ...

### 📹 Video Spotlight
- The Future of AI Reasoning (YouTube)

### 📈 Stats
- Sources checked: 24
- Articles ingested: 247
- Passed quality filter: 158
- Selected for publication: 15
- Average score: 8.1

### 🏷️ Categories
- AI Infrastructure: 4 articles
- AI Models: 3 articles
- Startups: 2 articles
- Hardware: 2 articles
- Policy: 1 article

---
**Generated by TechPulse Curation Agent**
```

---

### 7. Orchestration Module (`pipeline/`)

**Purpose:** Coordinate the entire pipeline

**Main Script:**
```
pipeline/
├── run_pipeline.py      # Main orchestration script
├── config.py            # Configuration management
├── logger.py            # Logging setup
└── scheduler.py         # Cron job handler
```

**Pipeline Execution:**
```python
# run_pipeline.py
async def main():
    logger.info("Starting TechPulse daily curation...")
    
    # 1. Ingest
    articles = await ingest_all_sources()
    logger.info(f"Ingested {len(articles)} articles")
    
    # 2. Process
    articles = deduplicate(articles)
    articles = filter_quality(articles)
    articles = extract_full_content(articles)
    logger.info(f"{len(articles)} after processing")
    
    # 3. Score
    profile = load_taste_profile()
    scored_articles = score_all(articles, profile)
    top_articles = select_top_articles(scored_articles, n=15)
    logger.info(f"Selected {len(top_articles)} articles")
    
    # 4. Enrich
    enriched = await enrich_articles(top_articles)
    
    # 5. Generate content
    content_files = generate_json_files(enriched)
    
    # 6. Create PR
    pr_url = create_github_pr(content_files)
    logger.info(f"PR created: {pr_url}")
```

---

## Frontend Integration

### Updating the Website to Consume JSON

**Modify `script.js` to load JSON:**
```javascript
// Load daily content
async function loadDailyContent() {
    try {
        const response = await fetch('content/latest.json');
        const data = await response.json();
        
        // Update hero section
        updateHero(data.hero);
        
        // Update headlines grid
        updateHeadlines(data.headlines);
        
        // Update video spotlight
        updateVideoSpotlight(data.video_spotlight);
        
        // Update date badge
        document.getElementById('currentDate').textContent = data.date;
    } catch (error) {
        console.error('Failed to load content:', error);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadDailyContent);
```

**Content Directory Structure:**
```
content/
├── latest.json              # Current day's content
├── daily/
│   ├── 2024-11-26.json
│   ├── 2024-11-25.json
│   └── ...
├── categories/
│   ├── ai-infrastructure.json
│   ├── startups.json
│   └── ...
├── archive/
│   └── 2024/
│       ├── 11.json          # November 2024
│       └── 10.json
└── metadata.json            # Site-wide stats
```

---

## Infrastructure & Deployment

### GitHub Actions Workflow

**`.github/workflows/daily-curation.yml`:**
```yaml
name: Daily TechPulse Curation

on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily
  workflow_dispatch:      # Manual trigger

jobs:
  curate:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r pipeline/requirements.txt
      
      - name: Run curation pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python pipeline/run_pipeline.py
      
      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v6
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          branch: daily-content-${{ env.DATE }}
          title: '📰 TechPulse Daily Content'
          body-path: .github/pr-body.md
```

### Environment Variables & Secrets

**Required Secrets (GitHub):**
- `OPENAI_API_KEY` - For embeddings and LLM scoring
- `NEWSAPI_KEY` - For NewsAPI access
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

**Optional Secrets:**
- `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`
- `YOUTUBE_API_KEY`
- `ANTHROPIC_API_KEY` (if using Claude)

### Configuration File

**`pipeline/config.yaml`:**
```yaml
pipeline:
  max_articles_per_day: 15
  lookback_hours: 48
  min_score: 7.0
  
ingestion:
  timeout_seconds: 30
  max_retries: 3
  
scoring:
  embedding_model: "text-embedding-3-small"
  llm_model: "gpt-4o-mini"
  batch_size: 20
  
output:
  content_dir: "content"
  archive_by_month: true
  
github:
  create_pr: true
  auto_merge: false
  branch_prefix: "daily-content-"
```

---

## API Cost Estimation

### OpenAI API Costs (per day)

**Embeddings:**
- 200 articles × 500 tokens avg = 100,000 tokens
- Cost: ~$0.002 per 1K tokens = **$0.20/day**

**LLM Scoring:**
- Top 50 articles × 1,000 tokens = 50,000 tokens
- GPT-4o-mini: ~$0.15 per 1M input tokens = **$0.008/day**

**Summarization:**
- 15 selected articles × 2,000 tokens = 30,000 tokens in + 5,000 out
- Cost: **$0.01/day**

**Total Estimated Daily Cost: ~$0.25/day = $7.50/month**

### NewsAPI Costs
- Free tier: 100 requests/day
- Developer plan: $449/month for 250,000 requests
- **Recommendation:** Start with free tier + RSS feeds

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Get basic ingestion and output working

- [ ] Set up project structure
- [ ] Implement RSS feed fetcher
- [ ] Build basic deduplication
- [ ] Create JSON output generator
- [ ] Test with mock data
- [ ] Update website to load from JSON

**Deliverables:**
- `pipeline/ingestion/rss_fetcher.py`
- `pipeline/processing/deduplicator.py`
- `pipeline/output/json_generator.py`
- `script.js` updates for JSON loading
- Sample `content/latest.json`

---

### Phase 2: Taste Profile (Week 3)
**Goal:** Implement intelligent scoring

- [ ] Create seed articles collection (10-20 examples)
- [ ] Build embedding system
- [ ] Implement similarity scoring
- [ ] Add basic LLM refinement
- [ ] Test scoring accuracy

**Deliverables:**
- `pipeline/taste_profile/seed_articles.json`
- `pipeline/taste_profile/embedder.py`
- `pipeline/taste_profile/scorer.py`
- Scoring evaluation report

---

### Phase 3: AI Enrichment (Week 4)
**Goal:** Generate quality summaries and categorization

- [ ] Build summarization system
- [ ] Implement category classifier
- [ ] Create headline generator
- [ ] Add layout assignment logic
- [ ] Test enrichment quality

**Deliverables:**
- `pipeline/enrichment/summarizer.py`
- `pipeline/enrichment/categorizer.py`
- `pipeline/enrichment/prompts/`

---

### Phase 4: GitHub Automation (Week 5)
**Goal:** Full end-to-end automation

- [ ] Build GitHub PR creator
- [ ] Set up GitHub Actions workflow
- [ ] Configure secrets
- [ ] Test full pipeline
- [ ] Set up monitoring/alerts

**Deliverables:**
- `pipeline/github/pr_creator.py`
- `.github/workflows/daily-curation.yml`
- Complete working pipeline

---

### Phase 5: Enhancement (Week 6+)
**Goal:** Polish and optimize

- [ ] Add more content sources
- [ ] Improve scoring algorithm
- [ ] Add analytics tracking
- [ ] Build admin dashboard (optional)
- [ ] A/B test different prompts

---

## Monitoring & Quality Control

### Metrics to Track

**Daily Pipeline:**
- Sources fetched successfully
- Articles ingested
- Articles after deduplication
- Score distribution
- Average score of selected articles
- API costs

**Content Quality:**
- User engagement (if analytics added)
- PR approval rate
- Manual edits to PR content
- Category distribution balance

### Logging Strategy

```python
# Structured logging
logger.info("Pipeline started", extra={
    "stage": "ingestion",
    "date": today,
    "sources": 24
})

logger.info("Scoring complete", extra={
    "articles_scored": 158,
    "avg_score": 7.2,
    "top_score": 9.4,
    "articles_selected": 15
})
```

### Alert Conditions
- Pipeline failure
- API errors (rate limits, auth)
- No articles meet threshold
- PR creation fails
- Unusual score distribution

---

## Alternative Architectures Considered

### Option A: Cloudflare Worker + KV
**Pros:** Edge computing, fast reads
**Cons:** More complex, vendor lock-in
**Decision:** Not needed initially for daily updates

### Option B: AWS Lambda + S3
**Pros:** Scalable, flexible
**Cons:** More infrastructure, cost complexity
**Decision:** GitHub Actions simpler for daily jobs

### Option C: Full CMS (Contentful, Sanity)
**Pros:** UI for editing, webhooks
**Cons:** Monthly cost, overkill for automated content
**Decision:** JSON files sufficient for now

---

## What We Can Build Together

### I Can Help You Build:

1. **✅ Complete Python Pipeline**
   - All ingestion modules
   - Processing and filtering logic
   - Embedding and scoring system
   - AI enrichment modules
   - JSON generators

2. **✅ Frontend Integration**
   - Update script.js to load JSON
   - Create dynamic content rendering
   - Archive page data loading
   - Category page automation

3. **✅ GitHub Actions Workflow**
   - Complete CI/CD setup
   - PR automation
   - Error handling

4. **✅ Configuration & Setup**
   - Config files
   - Requirements.txt
   - Documentation
   - Testing scripts

### You'll Need To:

1. **🔑 Set Up API Keys**
   - OpenAI API key
   - NewsAPI key (optional)
   - GitHub token (auto-provided)

2. **📝 Provide Taste Profile**
   - 10-20 example articles you love
   - List of preferred topics
   - Anti-patterns to avoid

3. **✅ Review Daily PRs**
   - Approve and merge (30 seconds)
   - Occasional edits if needed

4. **🚀 Deploy Initial Setup**
   - Push to GitHub
   - Configure Cloudflare Pages
   - Set up GitHub secrets

---

## Next Steps

### Immediate Actions:

1. **Review this architecture** - Any questions or changes?

2. **Choose starting point:**
   - Option A: Start with Phase 1 (ingestion + JSON output)
   - Option B: Build taste profile first (seed articles)
   - Option C: Update frontend first (JSON loading)

3. **Set up development environment:**
   ```bash
   mkdir pipeline
   cd pipeline
   python -m venv venv
   source venv/bin/activate
   pip install openai requests feedparser beautifulsoup4 pyyaml
   ```

4. **Create seed articles list** (10-20 examples)

### Recommended Path:

**Week 1 Focus:**
- Build RSS ingestion
- Create basic JSON output
- Update website to load from JSON
- Test with manual JSON file

**This gets you a working end-to-end flow quickly**, then we layer in intelligence.

---

## Questions to Discuss

1. **Content Sources:** Which sources are must-haves vs nice-to-haves?
2. **Update Frequency:** Daily? Twice daily? Morning + evening?
3. **Article Count:** 10-15 per day? More?
4. **Manual Override:** Want ability to add manual articles?
5. **Comments:** Add commenting system (Disqus, etc.)?
6. **Newsletter:** Actual email sending or just website?
7. **Analytics:** Want traffic tracking?

---

## Resources & References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Python feedparser](https://feedparser.readthedocs.io/)

---

**Ready to start building?** Let me know which phase you'd like to tackle first, and we'll begin! 🚀
