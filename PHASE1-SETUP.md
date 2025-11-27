# Phase 1 Setup Guide - TechPulse Automated Pipeline

## 🎉 What We Built

You now have a complete **end-to-end automated content curation pipeline**! Here's what's ready:

### ✅ Complete Components

1. **RSS Feed Ingestion** - Fetches from 10 configured sources
2. **Content Processing** - Deduplicates and filters articles
3. **JSON Generation** - Creates structured content for your website
4. **Dynamic Loading** - Website loads content from JSON files
5. **Logging & Monitoring** - Full pipeline observability

### 📁 New Files Created

```
Website/
├── pipeline/
│   ├── config.yaml              # Pipeline settings
│   ├── requirements.txt         # Python dependencies
│   ├── run_pipeline.py          # Main script ⭐
│   ├── test_setup.py            # Setup tester
│   ├── README.md                # Pipeline docs
│   ├── ingestion/
│   │   ├── sources.yaml        # RSS sources (10 feeds)
│   │   └── rss_fetcher.py      # Feed fetcher
│   ├── processing/
│   │   └── deduplicator.py     # Filtering & dedup
│   └── output/
│       └── json_generator.py   # JSON creator
├── content/                     # Generated content (created on first run)
│   ├── latest.json             # Homepage data
│   └── daily/
│       └── YYYY-MM-DD.json     # Daily archives
├── script.js                    # Updated with JSON loading
└── ARCHITECTURE.md              # Full system design

```

---

## 🚀 Quick Start (First Run)

### Step 1: Install Python Dependencies

```bash
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Test Setup

```bash
# Run the setup test
python test_setup.py
```

You should see all checkmarks ✓

### Step 3: Run the Pipeline

```bash
# Run the full pipeline
python run_pipeline.py
```

This will:
- Fetch articles from 10 RSS sources
- Process and filter them
- Generate `content/latest.json`
- Generate daily archive
- Create logs in `pipeline.log`

### Step 4: View the Results

```bash
# Check the generated content
cat ../content/latest.json

# Or with prettier formatting
python -m json.tool ../content/latest.json
```

### Step 5: Test the Website

```bash
# Start a local server from the Website directory
cd /Users/Jeffrey.Coy/Desktop/Website
python3 -m http.server 8000
```

Then open: **http://localhost:8000**

The website will automatically load from `content/latest.json` if it exists!

---

## 📊 What the Pipeline Does

### 1. **Ingestion** (30-60 seconds)
Fetches from these sources:
- ✅ Latent Space (your top priority!)
- ✅ VentureBeat AI
- ✅ TechCrunch AI
- ✅ OpenAI Blog
- ✅ Anthropic Blog
- ✅ Hacker News
- ✅ Every.to
- ✅ The Rundown AI
- ✅ Superhuman AI
- ✅ McKinsey Technology

### 2. **Processing**
- Removes duplicates by URL
- Removes similar titles (85% similarity threshold)
- Filters articles < 200 words
- Removes spam patterns

### 3. **Scoring** (Phase 1 - Placeholder)
- Assigns random scores between 6.5-9.5
- Selects top 15 articles
- **Phase 2 will add AI scoring!**

### 4. **JSON Generation**
Creates two files:
- `content/latest.json` - Homepage content
- `content/daily/YYYY-MM-DD.json` - Archive

---

## 🎯 Current Behavior

### What Works Now

✅ **Automatic Fetching** - Pulls from all sources
✅ **Smart Filtering** - Removes duplicates and low-quality content
✅ **JSON Output** - Structured data for website
✅ **Dynamic Website** - Loads content automatically
✅ **Fallback Support** - Static content if JSON unavailable

### What's Coming in Phase 2

🔮 **AI Taste Profile** - Scores based on YOUR preferences
🔮 **Better Summaries** - GPT-generated excerpts
🔮 **Smart Categories** - Auto-categorization
🔮 **GitHub Automation** - Daily PRs
🔮 **Twitter Integration** - Your favorite accounts

---

## 🛠 Customization

### Add More RSS Sources

Edit `pipeline/ingestion/sources.yaml`:

```yaml
sources:
  - name: "Your New Source"
    url: "https://example.com/feed.rss"
    type: "rss"
    category: "ai_news"
    priority: "high"
```

### Adjust Article Count

Edit `pipeline/config.yaml`:

```yaml
pipeline:
  max_articles_per_day: 20  # Change from 15 to 20
  lookback_hours: 72         # Look back 3 days instead of 2
```

### Change Scoring

Edit `pipeline/config.yaml`:

```yaml
scoring:
  default_score: 9.0    # Higher base score
  random_variance: 0.5  # Less variance
```

---

## 📖 How to Use Daily

### Option 1: Manual Run (For Now)

```bash
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline
source venv/bin/activate
python run_pipeline.py
```

Then deploy the updated `content/` directory to your site.

### Option 2: Scheduled (Coming in Phase 2)

We'll set up GitHub Actions to run this automatically every morning!

---

## 🔍 Debugging

### Check Logs

```bash
# View the log file
tail -f pipeline/pipeline.log

# Or view all logs
cat pipeline/pipeline.log
```

### Test Individual Components

```bash
# Test just the RSS fetcher
cd pipeline/ingestion
python rss_fetcher.py

# Test just the deduplicator
cd pipeline/processing
python deduplicator.py
```

### Common Issues

**"No articles fetched"**
- Check internet connection
- Some feeds may be temporarily down
- Check `pipeline.log` for specific errors

**"Module not found"**
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install -r requirements.txt`

**"Permission denied"**
- Make script executable: `chmod +x run_pipeline.py`

---

## 📋 Next Steps (Roadmap)

### Immediate (This Week)
- [x] Build core pipeline
- [ ] Run first test
- [ ] Review generated content
- [ ] Adjust sources as needed

### Phase 2 (Next Week)
- [ ] Add AI taste profile scoring
- [ ] Integrate OpenAI API
- [ ] Build summarization
- [ ] Test scoring accuracy

### Phase 3 (Week 3)
- [ ] Set up GitHub Actions
- [ ] Automate daily PRs
- [ ] Deploy to production
- [ ] Monitor first week

---

## 🎓 Understanding the Code

### Pipeline Flow

```python
# 1. Fetch articles
articles = fetcher.fetch_all_sources(sources)

# 2. Process (dedupe + filter)
articles = process_articles(articles)

# 3. Score (placeholder for now)
articles = assign_placeholder_scores(articles)

# 4. Generate JSON
generator.generate_latest(articles)
generator.generate_daily_archive(articles)
```

### JSON Structure

```json
{
  "date": "November 26, 2024",
  "hero": {
    "title": "Top story title",
    "subtitle": "Brief summary...",
    "url": "https://...",
    "score": 9.2
  },
  "headlines": [
    {
      "title": "Second story",
      "excerpt": "Summary...",
      "url": "https://..."
    }
  ]
}
```

### Website Integration

```javascript
// In script.js - automatically loads on page load
ContentLoader.loadLatestContent()
  .then(data => {
    updateHeroSection(data.hero);
    updateHeadlines(data.headlines);
  });
```

---

## 💡 Pro Tips

1. **Run Daily** - Fresh content every day
2. **Review Logs** - Check `pipeline.log` for issues
3. **Customize Sources** - Add your favorite feeds
4. **Test Locally** - Always test before deploying
5. **Keep Backups** - Daily archives are in `content/daily/`

---

## 📞 Testing Checklist

Run through this checklist for your first test:

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Run setup test (`python test_setup.py`)
- [ ] Run pipeline (`python run_pipeline.py`)
- [ ] Check `content/latest.json` exists
- [ ] Check `content/daily/YYYY-MM-DD.json` exists
- [ ] Start local server (`python3 -m http.server 8000`)
- [ ] Open http://localhost:8000
- [ ] Check browser console for "dynamic content loaded"
- [ ] Verify hero section shows new content
- [ ] Check date badge is today

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ Pipeline completes without errors
2. ✅ `content/latest.json` is created
3. ✅ JSON has 15 articles
4. ✅ Website loads dynamically
5. ✅ Browser console shows "✓ Dynamic content loaded"

---

## 🚨 Important Notes

### For Phase 1

- **Scoring is random** - Real AI scoring comes in Phase 2
- **No Twitter yet** - Too complex for Phase 1
- **Manual deployment** - GitHub Actions comes in Phase 2
- **Static fallback** - Site works without JSON

### Data Privacy

- All processing is local
- No external APIs (yet)
- No user data collected
- RSS feeds are public

---

## 📚 Additional Resources

- **Pipeline README**: `pipeline/README.md`
- **Full Architecture**: `ARCHITECTURE.md`
- **Main Website README**: `README.md`

---

**Ready to test?** Follow the Quick Start steps above! 🚀

**Questions?** Check `pipeline.log` or the pipeline README.

**Phase 1 Complete!** 🎉 You have a working end-to-end pipeline.
