# TechPulse Search - Quick Reference Guide

## How to Use Search

### Access Search
- **Keyboard shortcut:** Press `/` anywhere on the site to focus the search bar
- **Click:** Click the search bar in the navigation
- **Syntax helper:** Press `/` again while focused to see available syntax options

### Basic Search
```
AI agents          → Find articles containing both "AI" and "agents"
"exact phrase"     → Find exact phrase match
crypto OR blockchain → Find articles with either term
-hype              → Exclude articles containing "hype"
```

### Filter by Category/Tag
```
tag:enterprise                → Single category
tags:ai;ml;crypto            → Any of these (OR)
tags:ai+enterprise           → All of these (AND)
category:"Enterprise AI"     → Exact category name
```

### Filter by Source
```
source:VentureBeat           → Articles from VentureBeat
sources:OpenAI;Anthropic     → Multiple sources (OR)
-source:TechCrunch           → Exclude source
```

### Filter by Date
```
date:2025-11-28                      → Exact date
date:>2025-11-20                     → After date
date:<2025-11-30                     → Before date
date:2025-11-20..2025-11-28         → Date range
this:week                            → Current week
this:month                           → Current month
last:7days                           → Last 7 days
```

### Filter by Score
```
score:>7.5         → High quality (score > 7.5)
score:<8           → Lower scores
score:7..9         → Score range
```

### Combined Searches
```
"AI agents" tag:enterprise score:>8 date:>2025-11-20
→ Exact phrase, enterprise category, high score, recent

crypto OR blockchain -source:TechCrunch this:week
→ Crypto or blockchain, exclude TechCrunch, this week

tags:ai;ml+source:OpenAI score:>7
→ AI or ML tags, OpenAI source, good score
```

## Search Results

### Result Display
- **Compact cards** (like runners-up page)
- **Shows:** Title, category, source, score, read time, publication time
- **Clickable:** Article title → full article, Source name → source website

### Sorting Options
- **Relevance** (default) - Best matches first
- **Date** - Newest first
- **Score** - Highest AI relevance score first

### Performance
- Searches typically complete in **<100ms**
- Currently indexes **last 60 days** of articles
- Loads all available daily archive files

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `/` | Focus search bar |
| `/` (when focused) | Toggle syntax helper |
| `Enter` | Execute search |
| `↑` / `↓` | Navigate syntax helper |
| `Esc` | Close syntax helper |

## Tips & Tricks

### Finding High-Quality Articles
```
score:>8 this:month
```

### Research a Specific Topic
```
"retrieval augmented generation" OR RAG tag:enterprise
```

### Compare Source Coverage
Search separately:
```
tag:ai source:VentureBeat
tag:ai source:OpenAI
```

### Find Hidden Gems
```
score:6..7 this:month -source:TechCrunch
```

### Exclude Noise
```
blockchain -crypto -NFT -hype source:Axios
```

## Examples from Your Archive

### Enterprise AI Adoption
```
tag:enterprise score:>7.5 last:7days
```

### New Model Releases
```
tags:model;release;benchmark this:month
```

### Privacy & Security
```
tags:privacy;security date:>2025-11-01
```

### All OpenAI Content
```
source:OpenAI score:>7
```

### Recent High-Quality Everything
```
score:>8 this:week
```

## Search Syntax Helper

When you press `/` while in the search box, you'll see a ChatGPT-style dropdown with:

- **16 syntax patterns** - All available search operators
- **Live filtering** - Type to filter suggestions
- **Examples** - See syntax with real examples
- **Click to insert** - Click any item to add to search
- **Keyboard navigation** - Arrow keys + Enter

## Current Categories

Based on your `taste_profile.yaml`, you can search by:

- Enterprise AI Adoption for SaaS
- Building AI Division & Center of Excellence
- AI for COO & Operations
- Enterprise AI Strategy & Roadmap
- RAG & Retrieval Systems
- Process Automation
- New Model Releases & Evals
- AI Business Cases & ROI
- Personal Productivity & Automation
- AI Job Market Impact
- McKinsey & Strategy Reports
- Big Tech Moves & Partnerships
- Grok & xAI
- AI Privacy & Surveillance
- Cybersecurity & Hacking
- AI Cost Efficiency & Value
- Developer Tools & AI Coding
- AI Infrastructure
- Research Papers

Use shortened versions in searches: `tag:enterprise`, `tag:privacy`, `tag:model`, etc.

## Current Sources

Available sources to filter by:

- VentureBeat AI
- TechCrunch AI
- Hacker News
- Latent Space
- OpenAI Blog
- Anthropic Blog
- Every.to
- The Rundown AI
- Superhuman AI
- McKinsey Technology
- Axios
- AI News
- Business Insider AI

## URL Parameters

Search results are bookmarkable! Share searches via URL:

```
https://jeffcoy.net/search.html?q=tag:enterprise%20score:>8&sort=relevance
```

Parameters:
- `q` - URL-encoded search query
- `sort` - `relevance`, `date`, or `score`

## Performance Notes

- **Search index:** Loads ~60 days of articles (typically 500-2000 articles)
- **Load time:** ~1-2 seconds on first page load
- **Search speed:** <100ms for most queries
- **Caching:** Results cached during session
- **Mobile:** Fully responsive, touch-friendly

## Troubleshooting

### No results?
- Check spelling
- Try broader terms
- Remove some filters
- Use OR operator: `word1 OR word2`

### Too many results?
- Add more specific terms
- Use exact phrases: `"exact words"`
- Add filters: `tag:`, `source:`, `score:`
- Narrow date range: `this:week`

### Syntax not working?
- Check quotes are matched: `"phrase"`
- No spaces in operators: `tag:enterprise` not `tag: enterprise`
- Date format: `YYYY-MM-DD` (e.g., `2025-11-28`)
- Score as number: `7.5` not `seven`

## Future Enhancements (Planned)

- Saved searches (bookmarks)
- Search history
- "More like this" for articles
- Semantic search (AI-powered)
- Export results to CSV
- Search alerts (email when new matches)

---

**Questions or issues?** Open an issue or check the full plan in `SEARCH-FEATURE-PLAN.md`
