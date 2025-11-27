# 🧠 TechPulse Learning System

## Overview

Your TechPulse now **learns from your feedback**! Rate articles with thumbs up/down, and the AI will automatically adjust to show more of what you love and less of what you don't.

---

## 🎯 How It Works

### 1. Rate Articles
- Every article has 👍 (more like this) and 👎 (less like this) buttons
- Ratings are saved locally in your browser
- They persist across sessions

### 2. Export Ratings
- Visit `export_ratings.html` to download your ratings
- Get a `ratings.json` file with all your feedback

### 3. AI Learns & Adjusts
- Run the learning script to analyze your preferences
- AI automatically adjusts topic weights in `taste_profile.yaml`
- Next pipeline run will reflect your preferences!

---

## 🚀 Quick Start Guide

### Step 1: Rate Some Articles

1. Open your TechPulse site: `http://localhost:8080`
2. Read articles and click 👍 or 👎 on each
3. Rate at least **5-10 articles** for meaningful learning

**Tip:** The more you rate, the better the AI learns!

---

### Step 2: Export Your Ratings

**Option A: Use the Export Page (Easiest)**

1. Open in browser: `file:///Users/Jeffrey.Coy/Desktop/Website/export_ratings.html`
2. Click "📥 Download ratings.json"
3. Save to your `pipeline/` folder

**Option B: Manual Export**

1. Open browser console (F12)
2. Type: `copy(localStorage.getItem('techpulse_ratings'))`
3. Paste into new file: `pipeline/ratings.json`

---

### Step 3: Run the Learning Script

```bash
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline

# Dry run first (see what would change)
python3 learn_from_ratings.py ratings.json --dry-run

# Apply the changes
python3 learn_from_ratings.py ratings.json
```

---

### Step 4: See the Results

```bash
# Run the pipeline with your new preferences
python3 run_pipeline.py

# Refresh browser to see personalized content!
```

---

## 📊 Understanding the Learning

### What Gets Adjusted

The script adjusts **topic weights** in `taste_profile.yaml`:

```yaml
priority_topics:
  - name: "Enterprise AI Adoption for SaaS"
    weight: 1.2  # This gets adjusted based on your ratings!
    keywords: [...]
```

### How Adjustments Work

**Positive Ratings (👍):**
- Categories you upvote → weight increases
- More articles from that category in future
- Maximum weight: 1.5

**Negative Ratings (👎):**
- Categories you downvote → weight decreases
- Fewer articles from that category
- Minimum weight: 0.5

**Learning Rate:**
- Default: 0.2 (gentle learning)
- Higher (0.4-0.5) = aggressive adjustments
- Lower (0.1) = very gentle adjustments

---

## 📈 Example Learning Session

### Scenario
You rate 10 articles:
- 5 upvotes for "Enterprise AI" articles
- 3 downvotes for "Model Benchmarks" articles
- 2 upvotes for "AI Strategy" articles

### Analysis
```
Category Sentiment:
  💚 Enterprise AI Adoption
     Sentiment: +1.00 (5↑ 0↓)
     
  💛 AI Strategy
     Sentiment: +1.00 (2↑ 0↓)
     
  ❤️ Model Benchmarks
     Sentiment: -1.00 (0↑ 3↓)
```

### Changes Applied
```
📈 Enterprise AI Adoption for SaaS
   Weight: 1.2 → 1.4 (Δ +0.2)
   
📈 Enterprise AI Strategy & Roadmap
   Weight: 1.1 → 1.2 (Δ +0.1)
   
📉 New Model Releases & Evals
   Weight: 1.0 → 0.8 (Δ -0.2)
```

### Result
Next pipeline run:
- More enterprise AI content ✅
- Less model benchmark articles ✅
- Better match to your interests ✅

---

## 🎓 Advanced Usage

### Custom Learning Rate

```bash
# Gentle learning (safer for small datasets)
python3 learn_from_ratings.py ratings.json --learning-rate 0.1

# Aggressive learning (for 20+ ratings)
python3 learn_from_ratings.py ratings.json --learning-rate 0.4
```

### Dry Run (Preview Changes)

```bash
# See what would change WITHOUT actually changing
python3 learn_from_ratings.py ratings.json --dry-run

# Review the analysis
# If you like it, remove --dry-run to apply
```

### Reset to Defaults

```bash
# Backups are created automatically
# To restore:
cd pipeline/scoring
cp taste_profile_backup_YYYYMMDD_HHMMSS.yaml taste_profile.yaml
```

---

## 🔍 Reading the Analysis Report

When you run the learning script, you'll see:

### Overall Stats
```
📈 Overall Stats:
  Total ratings: 10
  👍 Up votes: 7
  👎 Down votes: 3
  Overall sentiment: +40.0%
```

**Meaning:** You generally like the content (good sign!)

---

### Category Sentiment
```
📊 Category Sentiment:
  💚 Enterprise AI Adoption for SaaS
     Sentiment: +1.00 (5↑ 0↓)
     Avg AI Score: 8.2
```

**Sentiment Scale:**
- `+1.00` = All upvotes (love it!)
- `+0.50` = 3 up, 1 down (like it)
- `0.00` = Equal votes (neutral)
- `-0.50` = 1 up, 3 down (dislike)
- `-1.00` = All downvotes (hate it)

---

### Proposed Changes
```
🎯 Proposed Weight Changes:
  📈 Enterprise AI Adoption for SaaS
     Weight: 1.2 → 1.4 (Δ +0.20)
     Based on: 5 votes, +100% sentiment
```

**Symbols:**
- 📈 = Weight increasing (more content)
- 📉 = Weight decreasing (less content)
- Δ = Delta (change amount)

---

## 💡 Best Practices

### 1. Rate Consistently
- Rate articles as you read them
- Don't wait until you have 100 articles
- **Sweet spot:** Export and learn after every 5-10 ratings

### 2. Be Honest
- Don't just upvote everything
- Downvotes are valuable feedback!
- The AI needs both to learn properly

### 3. Iterate Gradually
- Start with default learning rate (0.2)
- Run pipeline after each learning session
- See if results improve before rating more

### 4. Review Changes
- Always run `--dry-run` first
- Check if adjustments make sense
- Restore from backup if needed

---

## 🛠 Troubleshooting

### "No ratings found"
**Problem:** Haven't rated any articles yet  
**Solution:** Rate 5+ articles on TechPulse first

---

### "No matching topics found to adjust"
**Problem:** Categories in ratings don't match topics in `taste_profile.yaml`  
**Solution:** This is normal! The script uses fuzzy matching. If you rated "AI News" but profile has "Enterprise AI", they won't match. Either:
- Update category names in profile to match
- Or just rate more articles - some will match

---

### "Invalid JSON"
**Problem:** `ratings.json` is malformed  
**Solution:** Re-export using `export_ratings.html`

---

### Weights seem extreme (0.5 or 1.5)
**Problem:** Too aggressive learning  
**Solution:** Use lower learning rate: `--learning-rate 0.1`

---

## 📋 Workflow Examples

### Daily User
```bash
# Every morning:
1. Rate yesterday's articles (5-10 ratings)
2. Export ratings when you hit 10+ total
3. Run learning script monthly
4. Enjoy increasingly personalized content!
```

---

### Power User
```bash
# Weekly ritual:
1. Rate 20-30 articles throughout the week
2. Friday: Export ratings
3. Run: python3 learn_from_ratings.py ratings.json --dry-run
4. Review changes
5. Run: python3 learn_from_ratings.py ratings.json
6. Run: python3 run_pipeline.py
7. Next week: Even better content!
```

---

### First-Time Setup
```bash
# Initial calibration:
1. Run pipeline with default profile
2. Rate ALL articles (15-20 ratings)
3. Export immediately
4. Run learning script (aggressive): --learning-rate 0.3
5. Run pipeline again
6. Compare before/after
7. Adjust from there
```

---

## 🎯 Success Metrics

### After 10 Ratings
- ✅ Script runs successfully
- ✅ 1-2 categories adjusted
- ✅ Noticeable difference in next run

### After 25 Ratings
- ✅ 3-5 categories adjusted
- ✅ 80%+ articles you want to read
- ✅ Clear personalization evident

### After 50+ Ratings
- ✅ All categories tuned
- ✅ 90%+ relevance
- ✅ Feels like it "gets you"

---

## 🔐 Privacy & Data

### Where Ratings Are Stored

**Browser:** `localStorage` (local only, never sent anywhere)
**File:** `ratings.json` (your computer, never uploaded)
**Profile:** `taste_profile.yaml` (your computer)

**Bottom line:** All data stays on YOUR machine. Zero cloud, zero tracking!

---

## 🚀 Future Enhancements

### Coming Soon
- [ ] Auto-export on every X ratings
- [ ] Visual dashboard of preferences
- [ ] A/B testing of profiles
- [ ] Click tracking (not just ratings)
- [ ] Time-spent-reading tracking
- [ ] Export to different formats

### Possible
- [ ] Share profiles with others
- [ ] Import community profiles
- [ ] Profile versioning
- [ ] Regression testing

---

## 📚 Technical Details

### Rating Format
```json
{
  "url": "https://example.com/article",
  "category": "Enterprise AI",
  "score": 8.2,
  "rating": "up",
  "timestamp": "2025-11-26T22:00:00Z"
}
```

### Sentiment Calculation
```python
sentiment = (upvotes - downvotes) / total_votes
# Range: -1.0 (all down) to +1.0 (all up)
```

### Weight Adjustment
```python
adjustment = sentiment × learning_rate × 1.5 × confidence
# Where confidence = min(votes / 10, 1.0)
```

### Weight Bounds
```python
new_weight = max(0.5, min(1.5, old_weight + adjustment))
# Always between 0.5 and 1.5
```

---

## 🎉 Summary

You now have a **self-learning AI curation system**!

**What you built:**
1. ✅ Rating UI on every article
2. ✅ localStorage persistence
3. ✅ One-click export
4. ✅ Python learning script
5. ✅ Auto-weight adjustment
6. ✅ Backup & restore
7. ✅ Detailed analytics

**What this means:**
- System gets **smarter every day**
- Content becomes **more relevant over time**
- **Zero manual tuning** required
- **You're in control** of what you see

---

**Start rating articles now and watch TechPulse learn!** 🚀

---

*Built: November 26, 2025*  
*The future is personalized, and it runs on your machine.*
