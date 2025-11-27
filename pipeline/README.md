# TechPulse Curation Pipeline

Automated content curation system for the TechPulse website.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd pipeline
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Pipeline

```bash
python run_pipeline.py
```

This will:
1. Fetch articles from configured RSS sources
2. Deduplicate and filter content
3. Assign scores (placeholder for Phase 1)
4. Generate JSON files in `content/`

### 3. View Results

- **Homepage data:** `content/latest.json`
- **Daily archive:** `content/daily/YYYY-MM-DD.json`
- **Logs:** `pipeline.log`

## 📁 Structure

```
pipeline/
├── config.yaml              # Pipeline configuration
├── run_pipeline.py          # Main orchestrator
├── requirements.txt         # Python dependencies
├── ingestion/
│   ├── sources.yaml        # RSS feed sources
│   └── rss_fetcher.py      # Feed fetching logic
├── processing/
│   └── deduplicator.py     # Deduplication & filtering
└── output/
    └── json_generator.py   # JSON content generation
```

## ⚙️ Configuration

### Add/Remove Sources

Edit `ingestion/sources.yaml`:

```yaml
sources:
  - name: "Your Source Name"
    url: "https://example.com/feed.rss"
    type: "rss"
    category: "ai_news"
    priority: "high"
```

### Adjust Pipeline Settings

Edit `config.yaml`:

```yaml
pipeline:
  max_articles_per_day: 15    # How many articles to select
  lookback_hours: 48          # How far back to fetch
  min_word_count: 200         # Minimum article length
```

## 🧪 Testing

Test individual components:

```bash
# Test RSS fetcher
cd ingestion
python rss_fetcher.py

# Test deduplicator
cd processing
python deduplicator.py

# Test JSON generator
cd output
python json_generator.py
```

## 📊 Current Features (Phase 1)

- ✅ RSS feed ingestion from 10+ sources
- ✅ Deduplication by URL and title similarity
- ✅ Quality filtering (word count, spam detection)
- ✅ Placeholder scoring (random variance)
- ✅ JSON output for website consumption
- ✅ Daily archive generation

## 🔮 Coming in Phase 2

- [ ] AI-powered taste profile scoring
- [ ] OpenAI embeddings integration
- [ ] LLM-based summarization
- [ ] Smart categorization
- [ ] GitHub PR automation
- [ ] Twitter/X integration

## 🐛 Troubleshooting

### "No articles fetched"
- Check your internet connection
- Some RSS feeds may be temporarily down
- Check `pipeline.log` for specific errors

### "Module not found"
- Ensure you activated the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### "JSON file not created"
- Check file permissions in the `content/` directory
- Ensure the pipeline completed successfully (check logs)

## 📝 Logs

The pipeline logs all operations to:
- **Console:** Real-time progress
- **File:** `pipeline.log` (detailed debug info)

## 🎯 Next Steps

1. **Run the pipeline** to generate your first content
2. **Review the output** in `content/latest.json`
3. **Test the website** to see dynamic loading
4. **Customize sources** in `sources.yaml`
5. **Adjust scoring** when ready for Phase 2

---

**Built for TechPulse** 🚀
