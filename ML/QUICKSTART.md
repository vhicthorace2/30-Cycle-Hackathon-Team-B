# Quick Start: ML Phase 2 Implementation

## 🎯 What Was Created

Complete Machine Learning module for creator scoring, recommendations, and sentiment analysis.

```
ML/
├── core/
│   ├── sentiment_analyzer.py      # NLP sentiment analysis
│   ├── scoring_engine.py          # Influence/engagement/growth scoring
│   ├── recommendation_engine.py   # Creator-brand matching
│   ├── base_adapter.py            # [existing]
│   ├── engine.py                  # [existing]
│   ├── models.py                  # [existing]
│
├── dto/
│   ├── __init__.py
│   ├── scoring_input.py           # Input DTOs from backend
│   └── scoring_output.py          # Output DTOs to backend
│
├── ml_orchestrator.py             # Main service coordinator
├── ml_api_server.py               # FastAPI HTTP server
├── ml_demo.py                     # Example demonstrations
├── ML_INTEGRATION_GUIDE.md        # Complete integration docs
└── requirements.txt               # Python dependencies
```

## ⚡ Quick Setup

### 1. Install Dependencies
```bash
cd ciap-mvp-b/ML
pip install -r requirements.txt
```

### 2. Run the ML API Server
```bash
# Start API server (listens on http://localhost:8001)
python ml_api_server.py
```

The API will be available at:
- Interactive Docs: `http://localhost:8001/docs` (Swagger UI)
- Alternative Docs: `http://localhost:8001/redoc`

### 3. Test Locally (No HTTP)
```bash
# Run demo without API server
python ml_demo.py
```

## 📊 Three Main Endpoints

### 1. Score a Creator
```bash
curl -X POST http://localhost:8001/score/creator \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_1",
    "creator_id": "creator_1",
    "channel": {...},
    "audience": {...},
    "videos": [...]
  }'
```

**Returns:**
- Influence score (0-100)
- Engagement quality metrics
- Growth & consistency analysis
- Audience loyalty & quality
- Per-video performance scores
- Comment sentiment breakdown
- Key strengths & improvements

### 2. Get Creator Recommendations
```bash
curl -X POST http://localhost:8001/recommend/creators \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "rec_1",
    "brand": {...},
    "candidate_creators": [...],
    "num_recommendations": 5
  }'
```

**Returns:**
- Ranked list of best-fit creators
- Audience fit scores
- Engagement & niche fit
- Estimated reach & engagement
- Price tier compatibility

### 3. Analyze Sentiment
```bash
curl -X POST http://localhost:8001/analyze/sentiment \
  -H "Content-Type: application/json" \
  -d '{
    "comments": [
      {"id": "c1", "text": "Great video!", "author_id": "u1", ...}
    ]
  }'
```

**Returns:**
- Sentiment distribution (positive/negative/neutral %)
- Average sentiment score
- Detected emotions
- Trend (improving/declining/stable)

## 📝 What Data Backend Needs to Provide

### Required Fields

**Channel Info:**
- Channel ID, name, description
- Subscriber count, total views, video count
- Account creation date, verified status

**Audience Analytics (30-day window):**
- Views, watch time, subscribers gained/lost
- Average view duration
- Demographics: age groups, gender, countries
- Traffic sources: search, suggested, direct
- Device breakdown: mobile, desktop, tablet

**Videos (recent 10-20):**
- Video ID, title, description
- Views, likes, comments
- Duration, category, publish date
- Average view duration, impressions, CTR

**Comments (sample):**
- Comment text, author
- Like count, reply count
- Subscriber status

## 🔄 Integration Flow

```
Backend reads YouTube data
         ↓
Format as MLScoringRequest
         ↓
POST to /score/creator
         ↓
ML Module processes:
  - Scoring Engine: calculates metrics
  - Sentiment Analyzer: analyzes comments
  - Orchestrator: combines results
         ↓
Returns MLScoringResponse
         ↓
Backend stores in database
```

## 📈 Scoring Formulas

### Influence Score
```
Influence = (Engagement Quality × 0.4) 
          + (Growth Rate × 0.3) 
          + (Consistency × 0.2) 
          + (Audience Quality × 0.1)
```

### Tier Classification
- **Diamond:** 90+ influence score
- **Gold:** 75-89 influence score
- **Silver:** 60-74 influence score
- **Bronze:** 40-59 influence score  
- **Standard:** < 40 influence score

## 🛠️ Customization

All scoring weights are configurable in `core/scoring_engine.py`:

```python
class ScoringEngine:
    ENGAGEMENT_QUALITY_WEIGHT = 0.4  # Adjust here
    GROWTH_RATE_WEIGHT = 0.3
    CONSISTENCY_WEIGHT = 0.2
    AUDIENCE_QUALITY_WEIGHT = 0.1
```

## 🚀 Production Deployment

For production:

1. **Use Gunicorn:**
```bash
pip install gunicorn
gunicorn ml_api_server:app --workers 4 --bind 0.0.0.0:8001
```

2. **Set environment variables:**
```bash
export HF_HOME=/path/to/model/cache
export LOG_LEVEL=INFO
```

3. **Configure backend .env:**
```env
ML_API_URL=http://ml-service:8001
ML_API_TIMEOUT=60000
```

## 📚 Documentation

See `ML_INTEGRATION_GUIDE.md` for:
- Complete request/response schemas
- Backend integration examples (NestJS)
- Data requirements checklist
- Troubleshooting guide

## ✅ Testing

Run the demo to verify everything works:
```bash
python ml_demo.py
```

This will:
- Score a sample creator
- Generate recommendations
- Analyze sentiment
- Display results

## 🔧 Troubleshooting

**Sentiment models not downloading:**
```bash
export HF_HOME=/tmp/hf_cache
python ml_api_server.py
```

**Memory issues:**
- Run on machine with 8GB+ RAM
- Reduce comment batch size

**Port already in use:**
```bash
# Use different port
uvicorn ml_api_server:app --port 8002
```

## 📊 Performance

- **Model startup:** ~10-15 seconds (first run)
- **Creator scoring:** ~2-5 seconds
- **Comment analysis (100 comments):** ~5-10 seconds
- **Recommendations (10 creators):** ~3-5 seconds

## 🎓 Key Metrics Calculated

✅ **Engagement Quality**
- Engagement rate, comment authenticity, sentiment

✅ **Growth Analysis**
- Daily/weekly/monthly rates, momentum, churn

✅ **Audience Quality**
- Retention, loyalty, watch time, demographics

✅ **Influence Score**
- Weighted composite of all metrics

✅ **Per-Video Performance**
- Engagement percentile, viral/conversion potential

✅ **Sentiment Analysis**
- Comment sentiment, emotions, trends

✅ **Recommendations**
- Audience fit, engagement fit, niche fit

---

**Need help?** Check `ML_INTEGRATION_GUIDE.md` for detailed documentation.
