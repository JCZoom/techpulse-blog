# 📅 TechPulse Daily Workflow

Your complete morning routine to fetch, curate, and publish fresh content.

---

## ☕ Morning Publishing Routine (5-10 minutes)

### Step 1: Fetch & Curate Articles
```bash
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline
python3 run_pipeline.py
```

**What this does:**
- Fetches articles from RSS feeds (last 72 hours)
- Filters by quality (min word count, deduplication)
- Scores articles using AI embeddings + taste profile
- Generates `latest.json` with today's top stories
- Creates daily archive in `content/daily/YYYY-MM-DD.json`

**Expected output:**
```
✓ Fetched X articles from Y sources
✓ Scored articles: Z total
✓ Selected top Z articles
✓ Generated latest.json with Z articles
✓ Generated daily archive: ../content/daily/2025-11-28.json
```

**Typical results:**
- 7-50 articles depending on news volume
- Hero: 1 article (highest score)
- Headlines: 6 articles (next best)
- Runners-up: 25 articles (if 32+ total)

---

### Step 2: Review Content (Optional)
```bash
cd /Users/Jeffrey.Coy/Desktop/Website
open content/latest.json
```

**Quick checks:**
- ✅ Hero article looks compelling?
- ✅ Headlines are diverse categories?
- ✅ Dates are current?
- ✅ Images loaded correctly?

If anything looks off, you can re-run the pipeline or manually edit `latest.json`.

---

### Step 3: Push to GitHub
```bash
cd /Users/Jeffrey.Coy/Desktop/Website
git add content/
git commit -m "Daily update: $(date +%Y-%m-%d) - X articles"
git push origin main
```

**What this does:**
- Commits new `latest.json` to GitHub
- Cloudflare Pages auto-detects the push
- Triggers automatic rebuild (30-60 seconds)

---

### Step 4: Deploy to Production (Fast Method)
```bash
cd /Users/Jeffrey.Coy/Desktop/Website
wrangler pages deploy . --project-name=techpulse-blog --branch=main
```

**Why use Wrangler?**
- ⚡ **Instant deployment** (30 seconds vs 2-5 minutes)
- 🎯 **Deploys from local** (no Git wait time)
- ✅ **Guaranteed fresh content** (no cache issues)

**Expected output:**
```
✨ Success! Uploaded X files
✨ Deployment complete! Take a peek over at https://XXXXXX.techpulse-blog.pages.dev
```

---

### Step 5: Verify Live Site
```bash
# Wait 30 seconds, then:
open https://jeffcoy.net
```

**Verify checklist:**
- ✅ Date shows today (e.g., "November 28, 2025")
- ✅ Hero article is new
- ✅ Headlines refreshed
- ✅ "Show Me More" button appears (if 25+ runners-up)
- ✅ Images loading
- ✅ Rating buttons present

**If old content shows:**
- Hard refresh: `Cmd + Shift + R`
- Check browser console: Look for `✓ Dynamic content loaded successfully!`
- Wait 1-2 minutes for DNS propagation

---

## 🚀 Quick Reference Commands

### Full Morning Workflow (Copy-Paste)
```bash
# 1. Generate content
cd /Users/Jeffrey.Coy/Desktop/Website/pipeline && python3 run_pipeline.py

# 2. Commit & push
cd /Users/Jeffrey.Coy/Desktop/Website && \
git add content/ && \
git commit -m "Daily update: $(date +%Y-%m-%d)" && \
git push origin main

# 3. Deploy
wrangler pages deploy . --project-name=techpulse-blog --branch=main

# 4. Open site
sleep 30 && open https://jeffcoy.net
```

**Total time:** ~5 minutes (2 min pipeline + 3 min deploy & verify)

---

## 🔧 Troubleshooting

### Issue: "No new articles" or very few articles
**Cause:** Not many articles published in last 72 hours

**Solutions:**
1. Increase lookback window:
   ```bash
   # Edit pipeline/config.yaml
   lookback_hours: 168  # 7 days instead of 3
   ```

2. Add more RSS sources:
   ```bash
   # Edit pipeline/ingestion/sources.yaml
   # Add feeds from your favorite sites
   ```

3. Lower quality threshold:
   ```bash
   # Edit pipeline/config.yaml
   min_word_count: 50  # Lower from 100
   ```

---

### Issue: Date shows "Loading..." or wrong date
**Cause:** Browser cache or JavaScript error

**Solutions:**
1. **Hard refresh:** `Cmd + Shift + R`
2. **Clear cache:**
   - Chrome: `Cmd + Shift + Delete` → Clear browsing data
   - Safari: `Cmd + Option + E`
3. **Check console:**
   - Press `Cmd + Option + J`
   - Look for errors in red
   - Should see: `✓ Dynamic content loaded successfully!`

---

### Issue: Old hero/articles still showing
**Cause:** Cloudflare caching or deploy didn't complete

**Solutions:**
1. **Wait longer:** DNS can take 2-5 minutes to propagate
2. **Check deployment status:**
   - Go to: https://dash.cloudflare.com
   - Workers & Pages → techpulse-blog → Deployments
   - Verify latest deployment succeeded
3. **Force redeploy:**
   ```bash
   git commit --allow-empty -m "Force rebuild"
   git push origin main
   wrangler pages deploy . --project-name=techpulse-blog --branch=main
   ```

---

### Issue: "Show Me More" button not appearing
**Cause:** Not enough articles (need 32+ for runners-up)

**Expected behavior:**
- **0-7 articles:** No button (no runners-up)
- **8-31 articles:** Button shows, but < 25 runners-up
- **32+ articles:** Button shows with 25 runners-up

**Solution:** Increase article count (see "No new articles" above)

---

### Issue: Wrangler deploy fails
**Error:** "Not logged in"

**Solution:**
```bash
wrangler login
# Opens browser to authorize
# Then retry: wrangler pages deploy . --project-name=techpulse-blog --branch=main
```

**Error:** "Project not found"

**Solution:**
```bash
# Check project name in Cloudflare dashboard
wrangler pages deploy . --project-name=YOUR-ACTUAL-PROJECT-NAME --branch=main
```

---

## 📊 Understanding Article Selection

### Scoring System
- **8.0+** = Excellent (likely hero/headline material)
- **7.0-7.9** = Good (headlines or runners-up)
- **6.0-6.9** = Acceptable (runners-up or archive only)
- **<6.0** = Filtered out

### Distribution Logic
```
Sorted by AI score (highest first):

Article #1:     Hero (main feature)
Articles #2-7:  Headlines (6 cards)
Articles #8-32: Runners-up (up to 25)
Articles #33+:  Archive only (not on homepage)
```

### Taste Profile
Located in: `pipeline/scoring/taste_profile.yaml`

**What it does:**
- Defines content preferences (categories, topics, sources)
- Weights different factors (technical depth, business impact, etc.)
- Learns from your ratings over time

**To adjust:**
1. Edit `taste_profile.yaml` manually
2. Or rate articles on site (thumbs up/down)
3. Run learning system:
   ```bash
   cd /Users/Jeffrey.Coy/Desktop/Website/pipeline
   python3 learn_from_ratings.py
   ```

---

## 🎯 Best Practices

### Timing
- **Morning:** 7-9 AM (catches overnight articles)
- **Afternoon:** 2-4 PM (midday updates)
- **Evening:** 6-8 PM (end-of-day roundup)

### Frequency
- **Daily:** Recommended for fresh content
- **Twice daily:** For high-volume days
- **Weekly:** Minimum to keep site current

### Content Quality
- **Review hero:** Ensure it's compelling
- **Check diversity:** Mix of categories
- **Verify images:** All thumbnails load
- **Test links:** Spot-check a few articles

### User Engagement
- **Rate articles:** Use thumbs up/down to improve curation
- **Export ratings:** Backup your feedback
  ```bash
  open http://localhost:8080/export_ratings.html
  ```
- **Run learning:** Let AI learn from your ratings
  ```bash
  python3 pipeline/learn_from_ratings.py
  ```

---

## 🔄 Automated Daily Updates (Future)

Want to automate this? Create a GitHub Action:

**`.github/workflows/daily-update.yml`:**
```yaml
name: Daily Content Update

on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily
  workflow_dispatch:  # Manual trigger

jobs:
  update-content:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd pipeline
          pip install -r requirements.txt
      
      - name: Run pipeline
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd pipeline
          python3 run_pipeline.py
      
      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add content/
          git commit -m "Daily update: $(date +%Y-%m-%d)" || exit 0
          git push
```

**Setup:**
1. Add OpenAI API key to GitHub Secrets
2. Cloudflare will auto-deploy on push

---

## 📈 Monitoring

### Check Pipeline Health
```bash
# View last run log
tail -n 50 pipeline/pipeline.log

# Check for errors
grep ERROR pipeline/pipeline.log

# View scoring stats
grep "Top score:" pipeline/pipeline.log
```

### Site Analytics
- **Cloudflare Analytics:** Traffic, bandwidth, requests
- **Rating data:** Check `localStorage` in browser console
- **User feedback:** Export ratings regularly

---

## 🎉 Daily Checklist

```markdown
Morning Publishing Checklist:
- [ ] Run pipeline: `python3 run_pipeline.py`
- [ ] Review `latest.json` (optional)
- [ ] Commit: `git add content/ && git commit && git push`
- [ ] Deploy: `wrangler pages deploy .`
- [ ] Verify: Open jeffcoy.net and check date
- [ ] Test: Click hero, headlines, ratings
- [ ] (Optional) Rate a few articles for learning
```

---

**Happy Publishing!** 🚀

*Last updated: November 28, 2025*
