# ML Module Integration Guide

Backend integration with Python ML scoring, recommendations, and sentiment analysis.

## Overview

The CIAP ML module provides three main capabilities:

1. **Creator Influence Scoring** - Calculate engagement, growth, audience quality, and influence scores
2. **Brand-Creator Recommendations** - Match creators to brands based on audience fit, engagement, and niche
3. **Sentiment Analysis** - Analyze comment sentiment using NLP

## Architecture

```
Backend (NestJS)
    │
    ├──> Fetch creator data from YouTube API
    ├──> Format as MLScoringRequest JSON
    │
    └──> Call ML Endpoints
            │
            ├──> POST /score/creator
            ├──> POST /recommend/creators
            └──> POST /analyze/sentiment
                    │
                    ▼
            ML API Server (FastAPI)
                    │
                    ├──> ScoringEngine
                    ├──> SentimentAnalyzer
                    ├──> RecommendationEngine
                    │
                    └──> Return JSON responses
```

## Setup

### 1. Install Dependencies

```bash
cd ML
pip install -r requirements.txt
```

### 2. Start ML API Server

```bash
# Development (with auto-reload)
python ml_api_server.py

# Or using uvicorn
uvicorn ml_api_server:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at `http://localhost:8001`
- Interactive docs: `http://localhost:8001/docs`
- Alternative docs: `http://localhost:8001/redoc`

### 3. Configure Backend to Call ML Endpoints

Update your backend environment variables:

```env
# .env
ML_API_URL=http://localhost:8001
ML_API_TIMEOUT=60000
```

## API Endpoints

### 1. POST `/score/creator`

**Purpose:** Score a single creator across all metrics.

**Request Body:**
```json
{
  "request_id": "req_abc123",
  "creator_id": "creator_123",
  "channel": {
    "channel_id": "UCxxxxx",
    "channel_name": "My Channel",
    "channel_description": "About my channel...",
    "subscriber_count": 50000,
    "total_view_count": 1000000,
    "video_count": 120,
    "account_creation_date": "2020-01-15T00:00:00Z",
    "is_verified": true,
    "profile_picture_url": "https://...",
    "banner_url": "https://..."
  },
  "audience": {
    "window_days": 30,
    "views": 500000,
    "watch_time_minutes": 250000,
    "subscribers_gained": 1000,
    "subscribers_lost": 200,
    "average_view_duration_seconds": 300,
    "age_13_17_pct": 5.0,
    "age_18_24_pct": 15.0,
    "age_25_34_pct": 35.0,
    "age_35_44_pct": 25.0,
    "age_45_54_pct": 12.0,
    "age_55_64_pct": 7.0,
    "age_65_plus_pct": 1.0,
    "gender_male_pct": 60.0,
    "gender_female_pct": 39.0,
    "gender_other_pct": 1.0,
    "top_countries": ["US", "GB", "CA", "AU"],
    "search_views": 150000,
    "suggested_views": 250000,
    "direct_views": 100000,
    "playlist_views": 0,
    "mobile_views_pct": 70.0,
    "desktop_views_pct": 25.0,
    "tablet_views_pct": 5.0
  },
  "videos": [
    {
      "video_id": "video_123",
      "title": "Video Title",
      "description": "Video description...",
      "published_at": "2024-01-15T10:00:00Z",
      "view_count": 50000,
      "like_count": 2000,
      "comment_count": 500,
      "average_view_duration_seconds": 300,
      "impressions": 100000,
      "ctr": 5.0,
      "video_duration_seconds": 600,
      "category_id": "1",
      "thumbnail_url": "https://...",
      "comments_sample": [
        {
          "comment_id": "comment_1",
          "text": "Great video!",
          "author_id": "user_123",
          "author_name": "User",
          "published_at": "2024-01-15T11:00:00Z",
          "like_count": 10,
          "reply_count": 2,
          "is_from_subscriber": true,
          "is_pinned": false
        }
      ]
    }
  ]
}
```

**Response Body:**
```json
{
  "request_id": "req_abc123",
  "creator_id": "creator_123",
  "creator_name": "My Channel",
  "processed_at": "2024-01-15T12:00:00Z",
  "comment_sentiment": {
    "total_comments_analyzed": 500,
    "positive_pct": 75.0,
    "negative_pct": 10.0,
    "neutral_pct": 15.0,
    "average_sentiment_score": 0.65,
    "top_emotions": ["love", "support", "excited"],
    "sentiment_trend": "improving",
    "sample_positive": [...],
    "sample_negative": [...]
  },
  "engagement_quality": {
    "engagement_rate": 0.05,
    "comment_to_like_ratio": 0.25,
    "reply_rate": 15.0,
    "genuine_comment_ratio": 0.95,
    "average_comment_length": 45.0,
    "sentiment_quality_score": 75.0,
    "overall_quality_score": 82.5
  },
  "growth_consistency": {
    "daily_growth_rate": 0.067,
    "weekly_growth_rate": 0.47,
    "monthly_growth_rate": 2.0,
    "growth_momentum_7d": 0.47,
    "growth_momentum_30d": 2.0,
    "churn_rate": 20.0,
    "net_subscriber_change": 800,
    "upload_frequency_per_week": 2.5,
    "consistency_score": 85.0,
    "days_since_recent_upload": 3
  },
  "audience_quality": {
    "watch_time_per_subscriber": 5.0,
    "average_view_duration_ratio": 0.83,
    "subscriber_retention_rate": 80.0,
    "repeat_viewer_ratio_estimated": 0.8,
    "audience_loyalty_score": 78.5,
    "audience_age_concentration": 0.6,
    "audience_geographic_diversity": 0.8,
    "viewer_expansion_rate": 1.0,
    "organic_reach_score": 80.0,
    "end_screen_ctr": 5000.0,
    "card_ctr": 5.0
  },
  "influence_score": {
    "overall_influence_score": 81.2,
    "engagement_quality_score": 82.5,
    "engagement_quality_weight": 0.4,
    "growth_rate_score": 75.0,
    "growth_rate_weight": 0.3,
    "consistency_score": 85.0,
    "consistency_weight": 0.2,
    "audience_quality_score": 78.5,
    "audience_quality_weight": 0.1,
    "risk_factors": [],
    "risk_score": 0.0,
    "tier": "gold"
  },
  "video_scores": [
    {
      "video_id": "video_123",
      "title": "Video Title",
      "engagement_rate": 0.05,
      "engagement_percentile": 100.0,
      "performance_rank": 1,
      "estimated_reach": 40000,
      "viral_potential_score": 72.5,
      "conversion_potential_score": 68.0,
      "content_category_performance": "average"
    }
  ],
  "key_strengths": [
    "Top-tier influence (Gold rank)",
    "Strong engagement metrics",
    "Excellent audience retention and loyalty",
    "Highly consistent upload schedule"
  ],
  "improvement_areas": [
    "Increase video output frequency",
    "Optimize for search & recommendations to reach new viewers"
  ]
}
```

### 2. POST `/recommend/creators`

**Purpose:** Get ranked creator recommendations for a brand.

**Request Body:**
```json
{
  "request_id": "rec_123",
  "brand": {
    "brand_id": "brand_123",
    "brand_name": "Tech Brand Co",
    "brand_description": "We build innovative tech products...",
    "target_audience_age_min": 18,
    "target_audience_age_max": 35,
    "target_audience_gender": "all",
    "target_countries": ["US", "GB", "CA"],
    "target_interests": ["technology", "productivity", "innovation"],
    "budget_min_usd": 10000,
    "budget_max_usd": 100000,
    "industry": "technology",
    "previous_collaborations": 5
  },
  "candidate_creators": [
    {
      "request_id": "req_1",
      "creator_id": "creator_1",
      "channel": {...},
      "audience": {...},
      "videos": [...]
    }
  ],
  "num_recommendations": 5
}
```

**Response Body:**
```json
{
  "request_id": "rec_123",
  "brand_id": "brand_123",
  "brand_name": "Tech Brand Co",
  "created_at": "2024-01-15T12:00:00Z",
  "recommendations": [
    {
      "creator_id": "creator_1",
      "creator_name": "Tech Channel",
      "channel_url": "https://youtube.com/channel/...",
      "subscriber_count": 150000,
      "audience_fit_score": 88.5,
      "engagement_fit_score": 82.0,
      "niche_fit_score": 95.0,
      "overall_recommendation_score": 88.1,
      "estimated_reach_for_campaign": 75000,
      "estimated_engagement_count": 3750,
      "price_tier_compatibility": "perfect",
      "match_breakdown": {
        "audience_fit": 88.5,
        "engagement_fit": 82.0,
        "niche_fit": 95.0,
        "influence": 65.0
      },
      "recommendation_reason": "Perfect niche fit for technology - strong audience alignment with target 18-35 demographic"
    }
  ],
  "total_candidates_evaluated": 10,
  "top_match": {...}
}
```

### 3. POST `/analyze/sentiment`

**Purpose:** Standalone sentiment analysis of comments.

**Request Body:**
```json
{
  "comments": [
    {
      "id": "comment_1",
      "text": "This is amazing!",
      "author_id": "user_1",
      "author_name": "User",
      "published_at": "2024-01-15T10:00:00Z",
      "like_count": 50,
      "reply_count": 5,
      "is_from_subscriber": true,
      "is_pinned": false
    }
  ]
}
```

**Response Body:**
```json
{
  "total_comments": 1,
  "sentiment_distribution": {
    "positive_pct": 100.0,
    "negative_pct": 0.0,
    "neutral_pct": 0.0
  },
  "average_sentiment_score": 1.0,
  "top_emotions": ["love", "excited"],
  "sentiment_trend": "improving"
}
```

## Data Requirements from Backend

For the ML module to work, the backend needs to collect the following data from YouTube APIs:

### Channel Data (youtube.channels.list)
- Channel ID, name, description
- Subscriber count, total view count, video count
- Account creation date, verified status
- Profile picture & banner URLs

### Video Data (youtube.videos.list)
- Video ID, title, description
- View, like, comment counts
- Duration, category, publication date
- Thumbnail URL

### Analytics Data (youtubeAnalytics.reports)
- Daily/periodic views, watch time, subscriber gains/losses
- Audience demographics (age, gender, location)
- Traffic source breakdown
- Device type breakdown
- Click-through rates

### Comments Data (youtube.commentThreads.list)
- Comment text, author info
- Comment likes, reply counts
- Publication date
- Subscriber status

## Backend Integration Example (NestJS)

```typescript
// ml.service.ts
import { Injectable, HttpService } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class MLService {
  private mlApiUrl: string;
  
  constructor(
    private http: HttpService,
    private config: ConfigService,
  ) {
    this.mlApiUrl = this.config.get('ML_API_URL') || 'http://localhost:8001';
  }
  
  async scoreCreator(creatorData: any) {
    const response = await this.http.post(
      `${this.mlApiUrl}/score/creator`,
      creatorData,
    ).toPromise();
    return response.data;
  }
  
  async getRecommendations(brandData: any) {
    const response = await this.http.post(
      `${this.mlApiUrl}/recommend/creators`,
      brandData,
    ).toPromise();
    return response.data;
  }
  
  async analyzeSentiment(comments: any[]) {
    const response = await this.http.post(
      `${this.mlApiUrl}/analyze/sentiment`,
      { comments },
    ).toPromise();
    return response.data;
  }
}
```

```typescript
// ml.controller.ts
@Controller('ml')
export class MLController {
  constructor(private mlService: MLService) {}
  
  @Post('score/creator')
  async scoreCreator(@Body() creatorData: any) {
    return await this.mlService.scoreCreator(creatorData);
  }
  
  @Post('recommend')
  async recommendCreators(@Body() brandData: any) {
    return await this.mlService.getRecommendations(brandData);
  }
}
```

## Scoring Formulas

### Influence Score
```
Influence = (Engagement × 0.4) + (Growth × 0.3) + (Consistency × 0.2) + (Audience Quality × 0.1)
```

### Engagement Quality Score
```
Engagement Quality = (Engagement Rate × 0.4) + (Reply Rate × 0.2) 
                     + (Comment Authenticity × 0.2) + (Sentiment × 0.2)
```

### Audience Loyalty Score
```
Loyalty = (Retention Rate × 0.5) + (Repeat Viewer Ratio × 0.3) 
          + (Watch Time per Sub × 0.2)
```

## Performance Considerations

- **Model Loading:** Sentiment analysis models (~500MB) are loaded once at server startup
- **Comment Analysis:** Processing 100+ comments may take 5-10 seconds
- **Batch Processing:** Consider batching creator requests if analyzing many at once
- **Caching:** Backend should cache scoring results (24 hours recommended)

## Troubleshooting

### Model Download Errors
If transformers models fail to download:
```bash
# Set cache directory
export HF_HOME=/path/to/cache
python ml_api_server.py
```

### Memory Issues
- Reduce batch sizes for sentiment analysis
- Run on machine with 8GB+ RAM
- Consider GPU acceleration (CUDA) for production

### Connection Issues
- Verify ML server is running on correct port
- Check firewall rules
- Ensure backend can reach ML endpoint

## Future Enhancements

- [ ] GPU support for faster NLP processing
- [ ] Model fine-tuning on platform-specific data
- [ ] Real-time trending analysis
- [ ] Predictive ROI modeling
- [ ] Audience growth forecasting
- [ ] Content recommendation engine
