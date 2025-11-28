# Archive System - How It Works

## Overview
The archive page now **automatically loads all articles** from every pipeline run and provides **dynamic category filtering** based on your actual taste profile categories.

## How Articles Get Archived

### Automatic Archiving Process
1. **Every pipeline run** creates a daily JSON file: `content/daily/YYYY-MM-DD.json`
2. **Multiple runs per day** create suffixed files: `2025-11-28_2.json`, `2025-11-28_3.json`, etc.
3. **All articles are preserved** - nothing gets deleted when you run the pipeline again
4. **Archive page automatically loads** all daily JSON files from the last 60 days

### What Happens When You Run the Pipeline

```bash
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline
python3 run_pipeline.py
```

**Before:**
```
content/daily/
├── 2025-11-26.json (19 articles)
├── 2025-11-28.json (19 articles)
```

**After:**
```
content/daily/
├── 2025-11-26.json (19 articles) ← PRESERVED
├── 2025-11-28.json (19 articles) ← PRESERVED
├── 2025-11-28_2.json (NEW - 25 articles with new sources!)
```

**Archive Page Shows:** 19 + 19 + 25 = **63 total articles** ✅

## Archive Page Features

### 1. Dynamic Loading
- **Scans last 60 days** for daily JSON files
- **Loads all versions** (base file + _2, _3, _4, _5 suffixes)
- **Sorts by date** (newest first)
- **Groups by date** with section headers

### 2. Category Filtering
The filter buttons are **dynamically generated** from your actual categories:

**Your Current Categories (from taste_profile.yaml):**
- Enterprise AI Adoption for SaaS → **"Enterprise AI"** button
- Building AI Division & Center of Excellence → **"AI CoE"** button
- Enterprise AI Strategy & Roadmap → **"AI Strategy"** button
- New Model Releases & Evals → **"Model Releases"** button
- AI Privacy & Surveillance → **"Privacy"** button
- And more...

**Filter Buttons:**
- **All** - Shows every article
- **Enterprise AI** - Only "Enterprise AI Adoption for SaaS" articles
- **AI CoE** - Only "Building AI Division & Center of Excellence" articles
- **AI Strategy** - Only "Enterprise AI Strategy & Roadmap" articles
- Etc.

### 3. Article Display
Each article card shows:
- **Title** (clickable to article)
- **Category badge**
- **Time ago** (e.g., "2 days ago")
- **Source** (clickable to source website)
- **Read time** (calculated from word count)
- **Score** (AI relevance score)
- **Image** (if available)

### 4. Smart Grouping
Articles are grouped by publication date:
```
November 28, 2025
├── Article 1 (8.2 score)
├── Article 2 (7.9 score)
└── Article 3 (7.6 score)

November 26, 2025
├── Article 1 (8.1 score)
└── Article 2 (7.8 score)
```

## How Categories Work

### Category Assignment
Categories are assigned by the AI scorer based on:
1. **Article content** (title + excerpt)
2. **Keywords** from `taste_profile.yaml`
3. **Relevance matching** to priority topics

### Adding New Categories
When you add new topics to `taste_profile.yaml`:
```yaml
priority_topics:
  - name: "Quantum Computing"
    weight: 1.1
    keywords: ["quantum", "qubit", "quantum computing"]
```

**Next pipeline run:**
1. Articles matching these keywords get tagged as "Quantum Computing"
2. Archive page **automatically adds** a "Quantum Computing" filter button
3. No code changes needed! ✅

## Example Workflow

### Day 1 - Morning
```bash
python3 run_pipeline.py
# Creates: 2025-11-28.json (19 articles)
# Archive shows: 19 articles
```

### Day 1 - Afternoon (New sources added)
```bash
python3 run_pipeline.py
# Creates: 2025-11-28_2.json (25 articles, includes Axios/AI News)
# Archive shows: 19 + 25 = 44 articles
```

### Day 2 - Morning
```bash
python3 run_pipeline.py
# Creates: 2025-11-29.json (22 articles)
# Archive shows: 19 + 25 + 22 = 66 articles
```

**Nothing gets deleted. Everything accumulates!**

## Benefits

### ✅ Automatic Archiving
- No manual work required
- Every pipeline run adds to archive
- Old articles never disappear

### ✅ Smart Filtering
- Filter by your actual categories
- Categories auto-update from new articles
- "All" button to see everything

### ✅ No Data Loss
- Multiple runs per day supported
- Suffixed filenames prevent overwrites
- All articles preserved forever (or 60 days lookback)

### ✅ Consistent Experience
- Same article card design as homepage
- Same source hyperlinking
- Shows relevance scores
- Clickable sources

## Technical Details

### File Structure
```
content/
├── latest.json          # Today's featured articles (hero + headlines)
└── daily/
    ├── 2024-11-26.json  # All articles from Nov 26, 2024
    ├── 2025-11-26.json  # All articles from Nov 26, 2025
    ├── 2025-11-28.json  # First run on Nov 28
    ├── 2025-11-28_2.json # Second run on Nov 28
    └── 2025-11-28_3.json # Third run on Nov 28
```

### Archive Loader Logic
```javascript
1. Scan last 60 days for daily JSON files
2. Try base filename + _2, _3, _4, _5 suffixes
3. Collect all articles into single array
4. Extract unique categories
5. Generate filter buttons dynamically
6. Render articles grouped by date
7. Apply filtering on button click
```

### Category Normalization
The system handles category name variations:
- "Building AI Division & Center of Excellence" → "AI CoE" (button text)
- "Enterprise Ai Adoption For Saas" → "Enterprise AI" (handles case differences)

## Next Steps

### After Re-running Pipeline
1. Run pipeline with new sources (Axios, AI News, Business Insider)
2. Visit archive page: https://jeffcoy.net/archive.html
3. See new articles automatically appear
4. Test category filters (click each button)
5. Verify articles are properly tagged

### Expected Results
- **More categories** if new articles match new topics
- **All runs visible** (today's 3 runs + previous days)
- **Working filters** - click "Enterprise AI" to see only those articles
- **Chronological order** - newest dates at top

## Troubleshooting

### "No articles showing"
- Check browser console for errors
- Verify daily JSON files exist in `content/daily/`
- Check file permissions

### "Filter buttons not working"
- Clear browser cache
- Check that articles have `category` field
- Verify category names match between files

### "Old articles missing"
- Archive only looks back 60 days
- Files older than 60 days won't be loaded
- Increase lookback in `archive.html` line 139 if needed

## Future Enhancements

Possible improvements:
1. **Search functionality** - Search articles by keyword
2. **Date range picker** - "Show articles from Nov 1-15"
3. **Source filter** - "Show only VentureBeat articles"
4. **Export to CSV** - Download archive data
5. **Pagination** - "Load more" for performance with hundreds of articles
6. **Infinite lookback** - Create index file of all daily files for unlimited history
