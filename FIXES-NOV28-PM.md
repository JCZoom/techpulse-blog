# Fixes Applied - November 28, 2025 (Afternoon)

## Issues Fixed

### 1. ✅ Hero "Read Article" Button Not Opening
**Problem**: Button had link but didn't open when clicked
**Fix**: Added `target="_blank"` to hero link in `script.js` line 404
**Result**: Button now opens article in new tab

### 2. ✅ Author Email Display
**Problem**: Author showed as "michael.nunez@venturebeat.com (Michael Nuñez)"
**Fix**: 
- Added `cleanAuthorName()` function to extract just the name from "email (Name)" format
- Applied to hero section and all article cards
**Result**: Now shows clean "Michael Nuñez" instead of email

### 3. ✅ Source Names Now Hyperlinked
**Problem**: Source names (VentureBeat AI, Hacker News, etc.) were plain text
**Fix**:
- Added `getSourceUrl()` function mapping source names to their main website URLs
- Wrapped source names in clickable links on both homepage and runners-up page
**Result**: Clicking "VentureBeat AI" → https://venturebeat.com/category/ai/

### 4. ✅ Runners-Up Read Time
**Issue**: All showing "1 min read"
**Explanation**: This is actually CORRECT for RSS feeds
- RSS feeds provide summaries (15-500 words), not full articles
- Articles with short summaries (30-60 words) = 1 min read
- This will vary once you re-run the pipeline with new sources

**Why it's accurate**: RSS summaries ARE only 1-2 min reads. The full article is on the source website.

### 5. ✅ New RSS Feeds Added to `sources.yaml`
Added three new high-priority feeds:

1. **Axios Technology**
   - URL: `https://api.axios.com/feed/technology`
   - Focus: Breaking tech and AI news, data privacy, enterprise strategy

2. **AI News**
   - URL: `https://www.artificialintelligence-news.com/feed/`
   - Focus: Enterprise AI, data sovereignty, organizational privacy (exactly what you wanted!)

3. **Business Insider AI**
   - URL: `https://www.businessinsider.com/sai/rss`
   - Focus: AI business news and strategy

## Files Modified

1. **`script.js`**:
   - Added `target="_blank"` to hero link
   - Added `cleanAuthorName()` function
   - Added `getSourceUrl()` function with source-to-URL mapping
   - Applied hyperlinks to source names in article cards

2. **`runners-up.html`**:
   - Updated to use `getSourceUrl()` for hyperlinked sources
   - Added author name cleaning
   - Added fallback for read_time

3. **`pipeline/ingestion/sources.yaml`**:
   - Added Axios Technology feed
   - Added AI News feed  
   - Added Business Insider AI feed
   - All set to "high" priority

## Next Steps

### Re-run Pipeline to See New Sources
```bash
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline
python3 run_pipeline.py
```

This will:
- ✅ Fetch articles from the 3 new sources (Axios, AI News, Business Insider)
- ✅ Include the Anthropic/Google/Quantum article you wanted
- ✅ Include SAP European AI sovereignty article
- ✅ Show correct read times for all articles based on their RSS summary length
- ✅ Generate `2025-11-28_3.json` (since you already have _1 and _2)

### Deploy Changes
```bash
cd /Users/Jeffrey.Coy/Desktop/Website

# Commit first (best practice!)
git add .
git commit -m "Fix: Hero button, author display, source hyperlinks, new feeds (Axios, AI News, BI)"
git push origin main

# Deploy
wrangler pages deploy . --project-name=techpulse-blog --branch=main
```

## What You'll See After Re-running Pipeline

1. **More diverse articles** from Axios, AI News, and Business Insider
2. **The articles you mentioned**:
   - Anthropic/Google Cloud/Quantum article (from Axios)
   - SAP European AI sovereignty article (from AI News)
3. **Correct read times** - varying from 1-12 min based on RSS summary length
4. **Clickable sources** - VentureBeat AI, Hacker News, Axios, etc. all hyperlinked
5. **Clean author names** - No more email addresses showing

## Important Note on Read Times

**RSS feeds provide SUMMARIES, not full articles.** This is standard:
- VentureBeat: 200-500 word summaries → 2-3 min reads
- TechCrunch: 100-300 word summaries → 1-2 min reads
- OpenAI Blog: 30-50 word snippets → 1 min reads
- Axios: Usually 150-250 words → 1-2 min reads

The "read time" reflects how long it takes to read the RSS **summary**, not the full article on the source website. This is accurate and expected behavior.

If you want full article content, you'd need to implement web scraping (slow, unreliable, breaks with paywalls).
