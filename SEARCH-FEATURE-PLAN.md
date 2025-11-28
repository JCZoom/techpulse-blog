# TechPulse Advanced Search Feature - Implementation Plan

## Overview
Build a powerful search interface inspired by Drafts and DEVONthink, allowing advanced syntax-based queries across all archived articles.

---

## 1. Search Syntax Design

### Basic Syntax
```
"exact phrase"           - Exact phrase match in title/content
word1 word2              - Match articles containing both words (implicit AND)
word1 OR word2           - Match articles with either word
-word                    - Exclude articles containing word (NOT)
```

### Tag/Category Syntax
```
tag:crypto               - Articles tagged with "crypto" category
tags:crypto;ai;business  - Articles with ANY of these tags (OR logic)
tags:crypto+ai           - Articles with ALL of these tags (AND logic)
category:"Enterprise AI" - Exact category match
```

### Source Filtering
```
source:VentureBeat       - Articles from VentureBeat AI
sources:OpenAI;Anthropic - Articles from either source
-source:TechCrunch       - Exclude TechCrunch articles
```

### Date Filtering
```
date:2025-11-28          - Articles from specific date
date:>2025-11-20         - Articles after date
date:<2025-11-28         - Articles before date
date:2025-11-20..2025-11-28 - Date range
this:week                - Articles from current week
this:month               - Articles from current month
last:7days               - Last 7 days
```

### Score Filtering
```
score:>7.5               - High-scoring articles (>7.5)
score:8..10              - Score range 8-10
score:<6                 - Lower scored articles
```

### Advanced Combinations
```
"AI agents" tag:enterprise score:>8 date:>2025-11-20
  → Exact phrase "AI agents", enterprise category, high score, recent

crypto OR blockchain -source:TechCrunch this:week
  → Crypto or blockchain, exclude TechCrunch, from this week

tags:ai;ml+source:OpenAI score:>7
  → AI or ML tags, OpenAI source, good score
```

---

## 2. User Interface Design

### Option A: Dedicated Search Page (RECOMMENDED)
**New page:** `search.html`

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  TechPulse Navigation                               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🔍 Advanced Search                                 │
│  ┌───────────────────────────────────────────────┐ │
│  │ "AI agents" tag:enterprise score:>7.5        │ │
│  └───────────────────────────────────────────────┘ │
│  [Search] [Clear] [Show Syntax Help]               │
│                                                     │
│  ─────────────────────────────────────────────────  │
│  Showing 12 results • 0.03s                        │
│                                                     │
│  [Article Card 1 - Score: 8.2]                     │
│  [Article Card 2 - Score: 7.9]                     │
│  [Article Card 3 - Score: 7.6]                     │
│  ...                                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Features:**
- Large search input with autocomplete
- Syntax help panel (toggle)
- Real-time search as you type (debounced)
- Result count and search time
- Results displayed as article cards (same as archive)
- Sort options: relevance, date, score

### Option B: Search Bar in Navigation (Quick Access)
Add to all pages:
```
┌──────────────────────────────────────────────────┐
│ TECHPULSE  [Home] [Archive] [🔍 Search] [About] │
└──────────────────────────────────────────────────┘
```
Clicking search → opens search page or modal

### Option C: Archive Page Integration
Add search bar to top of archive page:
```
Archive
┌────────────────────────────────────────┐
│ 🔍 Search articles...                  │
└────────────────────────────────────────┘
[All] [Enterprise AI] [AI CoE] [Strategy]
```
Search filters existing archive view

---

## 3. Data Architecture

### Search Index Structure
```javascript
{
  articles: [
    {
      id: "2025-11-28-1234",
      title: "Black Forest Labs launches Flux.2...",
      url: "https://...",
      source: "VentureBeat AI",
      category: "New Model Releases & Evals",
      tags: ["ai", "image-generation", "model-release"],
      published: "2025-11-26T03:46:00",
      score: 7.7,
      word_count: 1500,
      excerpt: "...",
      content: "Full RSS content...",
      date: "2025-11-28",
      date_display: "November 28, 2025"
    },
    // ... more articles
  ],
  index: {
    // Optional: pre-computed search index for performance
    byCategory: { ... },
    bySource: { ... },
    byDate: { ... }
  }
}
```

### Data Loading Strategy
**Option 1: Client-side (Simple, works for <5000 articles)**
- Load all daily JSON files on page load (same as archive)
- Build search index in browser
- Perform search client-side using JavaScript

**Option 2: Pre-built Index (Better performance)**
- Pipeline generates `content/search-index.json` during each run
- Contains all articles + pre-computed indexes
- Faster loading, one HTTP request

**Option 3: Full-text search service (Overkill for now)**
- Use Algolia, Meilisearch, or Typesense
- Requires backend setup
- Best for 10,000+ articles

**RECOMMENDATION: Start with Option 1, migrate to Option 2 when archive grows**

---

## 4. Search Algorithm Implementation

### Parsing Query
```javascript
function parseSearchQuery(query) {
  return {
    phrases: [],      // ["AI agents", "neural networks"]
    terms: [],        // ["crypto", "blockchain"]
    excludeTerms: [], // ["hype", "celebrity"]
    tags: [],         // ["enterprise", "ai"]
    tagLogic: "OR",   // "OR" or "AND"
    sources: [],      // ["VentureBeat AI", "OpenAI Blog"]
    excludeSources: [],
    dateFilter: null, // { operator: ">", date: "2025-11-20" }
    scoreFilter: null, // { operator: ">", value: 7.5 }
    dateRange: null   // { from: "2025-11-20", to: "2025-11-28" }
  };
}
```

### Query Parser Examples
```javascript
Input: '"AI agents" tag:enterprise score:>7.5 date:>2025-11-20'

Output: {
  phrases: ["AI agents"],
  terms: [],
  excludeTerms: [],
  tags: ["enterprise"],
  tagLogic: "OR",
  sources: [],
  dateFilter: { operator: ">", date: "2025-11-20" },
  scoreFilter: { operator: ">", value: 7.5 }
}
```

### Search Matching Logic
```javascript
function matchArticle(article, parsedQuery) {
  // 1. Check exact phrases
  if (!matchPhrases(article, parsedQuery.phrases)) return false;
  
  // 2. Check keywords (AND logic by default)
  if (!matchTerms(article, parsedQuery.terms)) return false;
  
  // 3. Check exclusions
  if (matchExclusions(article, parsedQuery.excludeTerms)) return false;
  
  // 4. Check tags/categories
  if (!matchTags(article, parsedQuery.tags, parsedQuery.tagLogic)) return false;
  
  // 5. Check sources
  if (!matchSources(article, parsedQuery.sources)) return false;
  if (matchExcludedSources(article, parsedQuery.excludeSources)) return false;
  
  // 6. Check date filters
  if (!matchDateFilter(article, parsedQuery.dateFilter)) return false;
  
  // 7. Check score filter
  if (!matchScoreFilter(article, parsedQuery.scoreFilter)) return false;
  
  return true;
}
```

### Scoring & Ranking Results
```javascript
function scoreResult(article, parsedQuery) {
  let score = 0;
  
  // Title matches are worth more
  if (titleMatches(article.title, parsedQuery.terms)) score += 10;
  
  // Exact phrase in title = highest score
  if (titleContainsPhrases(article.title, parsedQuery.phrases)) score += 20;
  
  // Content matches
  if (contentMatches(article.content, parsedQuery.terms)) score += 5;
  
  // AI relevance score
  score += article.score * 2;
  
  // Recency bonus (newer articles slightly higher)
  const daysOld = daysSince(article.published);
  score += Math.max(0, 5 - daysOld * 0.1);
  
  return score;
}
```

---

## 5. Implementation Files

### New Files to Create

**1. `search.html`**
- Main search page
- Search input + syntax help
- Results display area
- Loading states

**2. `js/search-engine.js`**
- Query parser
- Search algorithm
- Result scoring
- Filter matching functions

**3. `js/search-ui.js`**
- UI interactions
- Autocomplete suggestions
- Syntax highlighting in search box
- Real-time search (debounced)

**4. `css/search.css` (or add to styles.css)**
- Search box styling
- Results layout
- Syntax help panel
- Highlight matched terms in results

### Files to Modify

**1. `script.js`**
- Add search initialization
- Reuse article card rendering
- Reuse data loading functions

**2. Navigation (index.html, archive.html, etc.)**
- Add "Search" link to nav menu

---

## 6. Feature Breakdown by Phase

### Phase 1: MVP (Core Search)
**Goal:** Basic working search with common queries

Features:
- ✅ Simple keyword search (implicit AND)
- ✅ Exact phrase search with quotes
- ✅ Category filtering: `tag:enterprise`
- ✅ Source filtering: `source:VentureBeat`
- ✅ Basic date filter: `date:2025-11-28`
- ✅ Results displayed as article cards
- ✅ Search on dedicated page

**Estimated Time:** 4-6 hours

### Phase 2: Advanced Operators
**Goal:** Power user features

Features:
- ✅ OR operator: `word1 OR word2`
- ✅ NOT operator: `-word`
- ✅ Multiple tags: `tags:ai;ml;crypto`
- ✅ Tag AND logic: `tags:ai+enterprise`
- ✅ Date ranges: `date:2025-11-20..2025-11-28`
- ✅ Score filtering: `score:>7.5`
- ✅ Relative dates: `this:week`, `last:7days`

**Estimated Time:** 3-4 hours

### Phase 3: UX Enhancements
**Goal:** Make it delightful to use

Features:
- ✅ Real-time search (as you type, debounced 300ms)
- ✅ Syntax help panel (toggle)
- ✅ Autocomplete suggestions
- ✅ Query history (localStorage)
- ✅ Highlight matched terms in results
- ✅ Search analytics (track popular queries)
- ✅ Keyboard shortcuts (CMD+K to open search)

**Estimated Time:** 4-5 hours

### Phase 4: Performance & Polish
**Goal:** Fast and scalable

Features:
- ✅ Pre-built search index (search-index.json)
- ✅ Search result caching
- ✅ Fuzzy matching for typos
- ✅ Search suggestions ("Did you mean...")
- ✅ Export search results (CSV/JSON)
- ✅ Save searches (bookmarkable URLs)

**Estimated Time:** 3-4 hours

---

## 7. Example User Workflows

### Workflow 1: Find Recent Enterprise AI Articles
```
User types: tag:enterprise date:>2025-11-20 score:>7.5
Result: Shows 8 high-quality enterprise AI articles from last week
```

### Workflow 2: Research Specific Technology
```
User types: "retrieval augmented generation" OR RAG
Result: All articles mentioning RAG or the full phrase
```

### Workflow 3: Compare Sources
```
Search 1: tag:ai source:VentureBeat
Search 2: tag:ai source:OpenAI
Result: Compare coverage from different sources
```

### Workflow 4: Find Hidden Gems
```
User types: score:6..7 this:month
Result: Good articles that didn't make headlines
```

### Workflow 5: Exclude Noise
```
User types: blockchain -crypto -NFT source:Axios
Result: Blockchain articles excluding crypto hype
```

---

## 8. Technical Considerations

### Performance
- **Target:** Search completes in <100ms for 1000 articles
- **Strategy:** Client-side JavaScript search (fast enough for our scale)
- **Optimization:** Build reverse indexes for tags, sources, dates
- **Fallback:** If archive grows >5000 articles, switch to search-index.json

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features (arrow functions, destructuring, Set/Map)
- No IE11 support needed

### Mobile Experience
- Responsive search input
- Touch-friendly result cards
- Simplified syntax help on mobile
- Virtual keyboard doesn't cover results

### Accessibility
- Keyboard navigation (Tab, Enter, Escape)
- ARIA labels for screen readers
- Focus management
- High contrast mode support

---

## 9. Search Index Generation (Phase 4)

### Pipeline Integration
Modify `pipeline/output/json_generator.py`:

```python
def generate_search_index(self, articles: List) -> Dict:
    """Generate comprehensive search index"""
    
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_articles": len(articles),
        "articles": [],
        "indexes": {
            "categories": {},
            "sources": {},
            "dates": {},
            "tags": set()
        }
    }
    
    # Add all articles with searchable fields
    for article in articles:
        index["articles"].append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "category": article.category,
            "published": article.published.isoformat(),
            "score": article.score,
            "word_count": article.word_count,
            "content": article.content,  # For full-text search
            "excerpt": self._generate_excerpt(article.content),
            "image_url": article.image_url
        })
    
    # Build reverse indexes
    # ... (optimize for fast filtering)
    
    return index
```

Output: `content/search-index.json` (updated with each pipeline run)

---

## 10. Future Enhancements (Post-Launch)

### Advanced Features
- **Saved Searches:** Bookmark favorite queries
- **Search Alerts:** Email when new articles match query
- **Visual Filters:** Click tags/sources to add to query
- **Search History:** Recently searched terms
- **Related Articles:** "More like this" based on search
- **Search Analytics:** Most searched terms, popular filters

### AI-Powered Search
- **Semantic Search:** "articles about AI adoption challenges"
- **Question Answering:** "How do I build an AI team?"
- **Summarization:** Summarize search results
- **Clustering:** Group similar results together

### Export & Integration
- **RSS Feed:** Create RSS from search results
- **API Endpoint:** Search via API (future)
- **Zapier Integration:** Trigger actions on new results

---

## 11. Success Metrics

### Key Metrics to Track
- **Search Usage:** % of visitors using search
- **Query Volume:** Searches per day/week
- **Popular Queries:** Most common searches
- **Result Quality:** Click-through rate on results
- **Zero Results:** Queries with no matches (improve coverage)
- **Syntax Adoption:** % using advanced syntax vs basic

### Goals (3 months post-launch)
- 30% of archive visitors use search
- <5% zero-result queries
- Average 3 results clicked per search
- 10% of users adopting advanced syntax

---

## 12. Implementation Order (Recommended)

### Week 1: MVP
1. Create `search.html` page structure
2. Build query parser (basic keywords + phrases)
3. Implement search algorithm (match & filter)
4. Display results as article cards
5. Add navigation link to search page
6. Test with current archive (~50 articles)

### Week 2: Advanced Syntax
1. Add tag filtering (`tag:`, `tags:`)
2. Add source filtering
3. Add date filtering
4. Add score filtering
5. Implement OR/NOT operators
6. Add syntax help panel

### Week 3: UX Polish
1. Real-time search with debouncing
2. Highlight matched terms in results
3. Query history (localStorage)
4. Mobile responsive design
5. Keyboard shortcuts (CMD+K)
6. Loading states & error handling

### Week 4: Optimization
1. Build search index in pipeline
2. Add result caching
3. Performance testing with large dataset
4. Analytics integration
5. Documentation and user guide

---

## 13. Testing Plan

### Test Cases

**Basic Search:**
- [ ] Single keyword: `agents`
- [ ] Multiple keywords: `AI agents`
- [ ] Exact phrase: `"Black Forest Labs"`
- [ ] Empty search shows all articles

**Tag/Category Search:**
- [ ] Single tag: `tag:enterprise`
- [ ] Multiple tags OR: `tags:ai;ml;crypto`
- [ ] Multiple tags AND: `tags:ai+enterprise`
- [ ] Non-existent tag shows zero results

**Source Search:**
- [ ] Single source: `source:VentureBeat`
- [ ] Multiple sources: `sources:OpenAI;Anthropic`
- [ ] Exclude source: `-source:TechCrunch`

**Date Search:**
- [ ] Exact date: `date:2025-11-28`
- [ ] After date: `date:>2025-11-20`
- [ ] Before date: `date:<2025-11-30`
- [ ] Date range: `date:2025-11-20..2025-11-28`
- [ ] Relative: `this:week`, `last:7days`

**Score Search:**
- [ ] Greater than: `score:>7.5`
- [ ] Less than: `score:<8`
- [ ] Range: `score:7..8`

**Combined Queries:**
- [ ] `"AI agents" tag:enterprise score:>7.5`
- [ ] `crypto OR blockchain -source:TechCrunch`
- [ ] `tag:ai date:>2025-11-20 score:>7`

**Edge Cases:**
- [ ] Special characters in search
- [ ] Very long queries (>200 chars)
- [ ] Malformed syntax (handle gracefully)
- [ ] Unicode characters
- [ ] HTML in article titles (escape properly)

---

## 14. Documentation for Users

### Quick Start Guide
```markdown
# Search Syntax Guide

## Basic Search
- Type any words to search titles and content
- Use quotes for exact phrases: "AI agents"

## Filter by Category
- Single: tag:enterprise
- Multiple: tags:ai;ml;crypto (OR logic)
- All tags: tags:ai+enterprise (AND logic)

## Filter by Source
- source:VentureBeat
- sources:OpenAI;Anthropic

## Filter by Date
- Exact: date:2025-11-28
- After: date:>2025-11-20
- Range: date:2025-11-20..2025-11-28
- Relative: this:week, last:7days

## Filter by Score
- score:>7.5 (high quality)
- score:8..10 (excellent)

## Advanced
- OR: crypto OR blockchain
- NOT: -hype -celebrity
- Combine: "AI safety" tag:enterprise score:>8 this:week
```

---

## 15. Open Questions to Resolve

### Before Implementation:
1. **Where should search live?**
   - Dedicated page (`search.html`)? ✅ RECOMMENDED
   - Integrated into archive page?
   - Modal/overlay on all pages?

2. **Default behavior for multiple terms?**
   - Implicit AND (match all terms)? ✅ RECOMMENDED
   - Implicit OR (match any term)?

3. **Case sensitivity?**
   - Case-insensitive by default? ✅ RECOMMENDED
   - Case-sensitive mode option?

4. **How to handle article content?**
   - Search title + excerpt only (faster)? ✅ RECOMMENDED
   - Search full RSS content (more accurate)?

5. **Result limit?**
   - Show all results?
   - Paginate (e.g., 20 per page)? ✅ RECOMMENDED for 100+ results
   - Infinite scroll?

6. **Query persistence?**
   - Store in URL query params (shareable)? ✅ RECOMMENDED
   - Store in localStorage (privacy)?
   - Both?

---

## 16. Files to Create/Modify Summary

### New Files (7)
```
search.html              - Main search page
js/search-engine.js      - Core search logic
js/search-ui.js          - UI interactions
css/search.css           - Search-specific styles
SEARCH-USER-GUIDE.md     - User documentation
tests/search-tests.js    - Unit tests
content/search-index.json - Pre-built index (Phase 4)
```

### Modified Files (6)
```
index.html               - Add search nav link
archive.html             - Add search nav link
runners-up.html          - Add search nav link
about.html               - Add search nav link
script.js                - Share utility functions
pipeline/output/json_generator.py - Generate search index
```

---

## Next Steps

1. **Review this plan** - Discuss any changes/priorities
2. **Choose approach** - Dedicated search page vs archive integration
3. **Phase selection** - Start with MVP or go straight to Phase 2?
4. **Begin implementation** - Start coding!

**Estimated Total Time:**
- Phase 1 (MVP): 4-6 hours
- Phase 2 (Advanced): 3-4 hours  
- Phase 3 (UX): 4-5 hours
- Phase 4 (Polish): 3-4 hours
**Total: 14-19 hours** for full implementation

---

## Questions for You

Before I start implementing:

1. **Preferred location?** Dedicated search page, archive integration, or both?
2. **Start with which phase?** MVP only, or go through Phase 2 immediately?
3. **Priority features?** Any specific syntax you want first?
4. **Mobile importance?** How critical is mobile experience?
5. **Analytics?** Should we track searches from day one?

Let me know your preferences and I'll start building! 🚀
