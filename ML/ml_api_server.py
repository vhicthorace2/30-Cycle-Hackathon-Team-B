# """
# FastAPI server exposing ML endpoints.
# Backend calls these endpoints to access ML scoring, recommendations, and sentiment analysis.

# Install: pip install fastapi uvicorn pydantic
# Run: python ml_api_server.py
# Or: uvicorn ml_api_server:app --reload --port 8001
# """
# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel
# from datetime import datetime
# from typing import List, Optional, Dict, Any
# import traceback

# from ml_orchestrator import MLOrchestratorService
# from dto.scoring_input import (
#     MLScoringRequest, RecommendationRequest, ChannelMetricsInput,
#     AudienceMetricsInput, VideoMetricsInput, CommentMetadata,
#     BrandProfileInput
# )

# # Initialize FastAPI app
# app = FastAPI(
#     title="CIAP ML Scoring API",
#     description="Machine Learning scoring, recommendations, and sentiment analysis for CIAP backend",
#     version="1.0.0",
# )

# # Initialize ML service
# ml_service = MLOrchestratorService()


# # ──────────────────────────────────────────────────────────────────────────────
# # Pydantic Models for Request/Response (for API documentation)
# # ──────────────────────────────────────────────────────────────────────────────

# class CommentInput(BaseModel):
#     """Comment for sentiment analysis."""
#     comment_id: str
#     text: str
#     author_id: str
#     author_name: str
#     published_at: datetime
#     like_count: int = 0
#     reply_count: int = 0
#     is_from_subscriber: bool = False
#     is_pinned: bool = False


# class VideoMetricsInputModel(BaseModel):
#     """Per-video metrics."""
#     video_id: str
#     title: str
#     description: str
#     published_at: datetime
#     view_count: int
#     like_count: int
#     comment_count: int
#     average_view_duration_seconds: int
#     impressions: int
#     ctr: float
#     video_duration_seconds: int
#     category_id: str
#     thumbnail_url: Optional[str] = None
#     comments_sample: List[CommentInput] = []


# class ChannelMetricsInputModel(BaseModel):
#     """Channel metrics."""
#     channel_id: str
#     channel_name: str
#     channel_description: str
#     subscriber_count: int
#     total_view_count: int
#     video_count: int
#     account_creation_date: datetime
#     is_verified: bool
#     profile_picture_url: Optional[str] = None
#     banner_url: Optional[str] = None


# class AudienceMetricsInputModel(BaseModel):
#     """Audience metrics."""
#     window_days: int
#     views: int
#     watch_time_minutes: int
#     subscribers_gained: int
#     subscribers_lost: int
#     average_view_duration_seconds: int
#     age_13_17_pct: float
#     age_18_24_pct: float
#     age_25_34_pct: float
#     age_35_44_pct: float
#     age_45_54_pct: float
#     age_55_64_pct: float
#     age_65_plus_pct: float
#     gender_male_pct: float
#     gender_female_pct: float
#     gender_other_pct: float = 0.0
#     top_countries: List[str] = []
#     search_views: int = 0
#     suggested_views: int = 0
#     direct_views: int = 0
#     playlist_views: int = 0
#     mobile_views_pct: float = 0.0
#     desktop_views_pct: float = 0.0
#     tablet_views_pct: float = 0.0


# class CreatorScoringRequestModel(BaseModel):
#     """Request body for creator scoring endpoint."""
#     request_id: str
#     creator_id: str
#     channel: ChannelMetricsInputModel
#     audience: AudienceMetricsInputModel
#     videos: List[VideoMetricsInputModel]


# class BrandProfileInputModel(BaseModel):
#     """Brand profile for recommendations."""
#     brand_id: str
#     brand_name: str
#     brand_description: str
#     target_audience_age_min: int
#     target_audience_age_max: int
#     target_audience_gender: str
#     target_countries: List[str] = []
#     target_interests: List[str] = []
#     budget_min_usd: float
#     budget_max_usd: float
#     industry: str
#     previous_collaborations: int = 0


# class RecommendationRequestModel(BaseModel):
#     """Request body for recommendation endpoint."""
#     request_id: str
#     brand: BrandProfileInputModel
#     candidate_creators: List[CreatorScoringRequestModel]
#     num_recommendations: int = 5


# class SentimentAnalysisRequestModel(BaseModel):
#     """Request body for sentiment analysis endpoint."""
#     comments: List[Dict[str, Any]]


# # ──────────────────────────────────────────────────────────────────────────────
# # Health Check
# # ──────────────────────────────────────────────────────────────────────────────

# @app.get("/health", tags=["System"])
# def health_check():
#     """Health check endpoint."""
#     return {
#         "status": "healthy",
#         "service": "CIAP ML API",
#         "timestamp": datetime.utcnow().isoformat(),
#     }


# # ──────────────────────────────────────────────────────────────────────────────
# # Creator Scoring Endpoint
# # ──────────────────────────────────────────────────────────────────────────────

# @app.post("/score/creator", tags=["Scoring"])
# def score_creator(request_model: CreatorScoringRequestModel):
#     """
#     Score a creator's influence, engagement, growth, and audience quality.
    
#     **Request Body:**
#     - `request_id`: Unique request identifier
#     - `creator_id`: Creator's unique ID
#     - `channel`: Channel metrics (name, subs, etc.)
#     - `audience`: Audience analytics (demographics, watch time, growth)
#     - `videos`: List of video metrics with comment samples
    
#     **Response:**
#     Complete scoring breakdown including:
#     - Overall influence score (0-100)
#     - Engagement quality score
#     - Growth and consistency metrics
#     - Audience quality and loyalty
#     - Per-video performance scores
#     - Sentiment analysis of comments
#     - Key strengths and improvement areas
#     """
#     try:
#         # Convert Pydantic models to internal DTO objects
#         request = MLScoringRequest(
#             request_id=request_model.request_id,
#             creator_id=request_model.creator_id,
#             channel=ChannelMetricsInput(**request_model.channel.dict()),
#             audience=AudienceMetricsInput(**request_model.audience.dict()),
#             videos=[
#                 VideoMetricsInput(
#                     **v.dict(exclude={"comments_sample"}),
#                     comments_sample=[
#                         CommentMetadata(**c.dict())
#                         for c in v.comments_sample
#                     ]
#                 )
#                 for v in request_model.videos
#             ],
#         )
        
#         # Run ML scoring
#         response = ml_service.score_creator(request)
        
#         # Convert to dict for JSON serialization
#         response_dict = ml_service.response_to_dict(response)
        
#         return JSONResponse(status_code=200, content=response_dict)
        
#     except Exception as e:
#         print(f"Error scoring creator: {e}")
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))


# # ──────────────────────────────────────────────────────────────────────────────
# # Recommendation Endpoint
# # ──────────────────────────────────────────────────────────────────────────────

# @app.post("/recommend/creators", tags=["Recommendations"])
# def recommend_creators(request_model: RecommendationRequestModel):
#     """
#     Get creator recommendations for a brand.
    
#     **Request Body:**
#     - `request_id`: Unique request identifier
#     - `brand`: Brand profile (target audience, budget, interests)
#     - `candidate_creators`: List of creators to evaluate
#     - `num_recommendations`: Top N to return (default: 5)
    
#     **Response:**
#     Ranked list of creators with:
#     - Audience fit score
#     - Engagement fit score
#     - Niche fit score
#     - Overall recommendation score
#     - Estimated reach and engagement
#     - Price tier compatibility
#     - Explanation for recommendation
#     """
#     try:
#         # Convert Pydantic models to internal DTO objects
#         request = RecommendationRequest(
#             request_id=request_model.request_id,
#             brand=BrandProfileInput(**request_model.brand.dict()),
#             candidate_creators=[
#                 MLScoringRequest(
#                     request_id=c.request_id,
#                     creator_id=c.creator_id,
#                     channel=ChannelMetricsInput(**c.channel.dict()),
#                     audience=AudienceMetricsInput(**c.audience.dict()),
#                     videos=[
#                         VideoMetricsInput(
#                             **v.dict(exclude={"comments_sample"}),
#                             comments_sample=[
#                                 CommentMetadata(**com.dict())
#                                 for com in v.comments_sample
#                             ]
#                         )
#                         for v in c.videos
#                     ],
#                 )
#                 for c in request_model.candidate_creators
#             ],
#             num_recommendations=request_model.num_recommendations,
#         )
        
#         # Run recommendation engine
#         response = ml_service.recommend_creators(request)
        
#         # Convert to dict
#         from dataclasses import asdict
#         import json
        
#         def datetime_handler(obj):
#             if isinstance(obj, datetime):
#                 return obj.isoformat()
#             raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
#         response_dict = json.loads(json.dumps(asdict(response), default=datetime_handler))
        
#         return JSONResponse(status_code=200, content=response_dict)
        
#     except Exception as e:
#         print(f"Error recommending creators: {e}")
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))


# # ──────────────────────────────────────────────────────────────────────────────
# # Sentiment Analysis Endpoint
# # ──────────────────────────────────────────────────────────────────────────────

# @app.post("/analyze/sentiment", tags=["Sentiment"])
# def analyze_sentiment(request_model: SentimentAnalysisRequestModel):
#     """
#     Analyze sentiment of comments.
    
#     **Request Body:**
#     - `comments`: List of comment objects with `text` and other metadata
    
#     **Response:**
#     - Total comments analyzed
#     - Sentiment distribution (positive, negative, neutral percentages)
#     - Average sentiment score (-1.0 to 1.0)
#     - Top emotions detected
#     - Sentiment trend (improving, declining, stable)
#     """
#     try:
#         sentiment_result = ml_service.analyze_sentiment(request_model.comments)
        
#         return JSONResponse(status_code=200, content=sentiment_result)
        
#     except Exception as e:
#         print(f"Error analyzing sentiment: {e}")
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=str(e))


# # ──────────────────────────────────────────────────────────────────────────────
# # Info Endpoint
# # ──────────────────────────────────────────────────────────────────────────────

# @app.get("/info", tags=["System"])
# def api_info():
#     """Get API information and available endpoints."""
#     return {
#         "service": "CIAP ML Scoring API",
#         "version": "1.0.0",
#         "endpoints": {
#             "health": "GET /health",
#             "creator_scoring": "POST /score/creator",
#             "recommendations": "POST /recommend/creators",
#             "sentiment_analysis": "POST /analyze/sentiment",
#             "info": "GET /info",
#             "docs": "GET /docs (Swagger UI)",
#         },
#         "description": "Machine learning scoring, recommendations, and sentiment analysis for creator analytics",
#     }


# # ──────────────────────────────────────────────────────────────────────────────
# # Running the Server
# # ──────────────────────────────────────────────────────────────────────────────

# if __name__ == "__main__":
#     import uvicorn
    
#     print("Starting CIAP ML API Server...")
#     print("API Documentation: http://localhost:8001/docs")
#     print("Alternate Docs: http://localhost:8001/redoc")
    
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8001,
#         reload=True,
#     )


"""
FastAPI server exposing ML endpoints.
OPTIMIZED for minimal YouTube Data API usage (no Analytics API required).
Backend calls these endpoints to access ML scoring, recommendations, and sentiment analysis.

Install: pip install fastapi uvicorn pydantic
Run: python ml_api_server.py
Or: uvicorn ml_api_server:app --reload --port 8001
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
import traceback
import json

from ml_orchestrator import MLOrchestratorService
from dto.scoring_input import (
    MLScoringRequest, 
    RecommendationRequest, 
    ChannelMetricsInput,
    BrandProfileInput,
    MinimalAudienceSignal,
    CreatorScore
)
from dto.scoring_output import (
    DashboardCreatorSummary,
    PredictiveForecast,
    ComparisonResult
)

# Initialize FastAPI app
app = FastAPI(
    title="CIAP ML Scoring API (Optimized - Minimal YouTube API)",
    description="ML scoring, recommendations, and sentiment analysis using only YouTube Data API",
    version="2.0.0",
)

# Initialize ML service
ml_service = MLOrchestratorService()


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Models for Request/Response (Minimal Data Version)
# ──────────────────────────────────────────────────────────────────────────────

class CommentInput(BaseModel):
    """Comment for sentiment analysis (simplified)."""
    comment_id: str
    text: str
    like_count: int = 0
    published_at: datetime
    author_subscriber_count: int = 0  # Key loyalty indicator
    is_reply: bool = False


class VideoMetricsInputModel(BaseModel):
    """Per-video metrics from YouTube Data API only."""
    video_id: str
    title: str
    published_at: datetime
    view_count: int
    like_count: int
    comment_count: int
    favorite_count: int = 0  # Underrated engagement signal
    tags: List[str] = Field(default_factory=list)  # For content categorization
    comments_sample: List[CommentInput] = Field(default_factory=list)  # Max 5 comments


class ChannelMetricsInputModel(BaseModel):
    """Channel metrics from YouTube Data API only."""
    channel_id: str
    channel_name: str
    subscriber_count: int
    total_view_count: int
    video_count: int
    account_creation_date: datetime
    is_verified: bool
    country: str = ""  # For local relevance (NG, KE, GH, etc.)
    custom_url: Optional[str] = None  # Indicates established creator
    hidden_subscriber_count: bool = False  # Red flag indicator


class PlaylistMetricsInputModel(BaseModel):
    """Playlist data for content consistency."""
    playlist_id: str
    title: str
    video_count: int
    created_at: datetime
    is_collaboration_playlist: bool = False


class BrandProfileInputModel(BaseModel):
    """Brand profile for recommendations (simplified for African market)."""
    brand_id: str
    brand_name: str
    industry: str  # "fashion", "tech", "beauty", "finance", etc.
    target_age_range: str = "all"  # "13-24", "25-34", "35+", "all"
    target_gender: str = "all"  # "all", "male", "female"
    target_countries: List[str] = Field(default_factory=list)  # "NG", "KE", "GH", etc.
    budget_range_usd: tuple = (0, 1000)  # (min, max)
    preferred_content_categories: List[str] = Field(default_factory=list)
    language_preference: str = "en"  # "en", "pcm"(Nigerian Pidgin)
    minimum_subscriber_count: int = 0
    maximum_subscriber_count: int = 0  # 0 means no limit
    minimum_engagement_rate: float = 0.0  # 0-100


class CreatorScoringRequestModel(BaseModel):
    """
    Request body for creator scoring endpoint.
    OPTIMIZED - uses only Data API metrics.
    """
    request_id: str
    creator_id: str
    channel: ChannelMetricsInputModel
    videos: List[VideoMetricsInputModel]  # Last 8-10 videos only
    playlists: List[PlaylistMetricsInputModel] = Field(default_factory=list)  # Max 5


class RecommendationRequestModel(BaseModel):
    """Request body for recommendation endpoint (simplified)."""
    request_id: str
    brand: BrandProfileInputModel
    candidate_creators: List[CreatorScoringRequestModel]
    num_recommendations: int = 5
    prefer_local_creators: bool = True  # Prioritize Nigerian/African creators
    prefer_pidgin_english: bool = True  # Nigerian market specific


class SentimentAnalysisRequestModel(BaseModel):
    """Request body for sentiment analysis endpoint."""
    comments: List[CommentInput]
    include_emotions: bool = True  # Enable emotion detection


class PredictiveForecastRequestModel(BaseModel):
    """Request for predictive forecasting."""
    creator_id: str
    creator_name: str
    channel: ChannelMetricsInputModel
    videos: List[VideoMetricsInputModel]
    campaign_budget_usd: float = 500.0
    campaign_duration_days: int = 30


class ComparisonRequestModel(BaseModel):
    """Request for comparing multiple creators."""
    creator_ids: List[str]
    creator_scores: List[Dict[str, Any]]  # Pre-scored creators


# ──────────────────────────────────────────────────────────────────────────────
# Health Check
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "CIAP ML API (Minimal YouTube API)",
        "version": "2.0.0",
        "api_type": "Optimized - No Analytics API Required",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Creator Scoring Endpoint (Simplified)
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/score/creator", tags=["Scoring"])
def score_creator(request_model: CreatorScoringRequestModel):
    """
    Score a creator's influence using simplified formula:
    Score = (Engagement Rate × 40%) + (Growth Rate × 30%) + 
            (Post Consistency × 20%) + (Audience Quality × 10%)
    
    **Request Body:**
    - `request_id`: Unique request identifier
    - `creator_id`: Creator's unique ID
    - `channel`: Channel metrics (subscribers, verification, country)
    - `videos`: List of videos with engagement metrics (min 8-10)
    - `playlists`: Optional playlist data for consistency
    
    **Response:**
    - CreatorScore with total score and breakdown
    """
    try:
        # Convert Pydantic models to internal DTO objects
        request = MLScoringRequest(
            request_id=request_model.request_id,
            creator_id=request_model.creator_id,
            channel=ChannelMetricsInput(**request_model.channel.dict()),
            videos=[
                VideoMetricsInput(
                    **v.dict(exclude={"comments_sample"}),
                    comments_sample=[
                        CommentInput(**c.dict())
                        for c in v.comments_sample
                    ]
                )
                for v in request_model.videos
            ],
            playlists=[
                PlaylistMetricsInput(**p.dict())
                for p in request_model.playlists
            ],
            timestamp=datetime.utcnow()
        )
        
        # Run ML scoring
        creator_score = ml_service.score_creator_minimal(request)
        
        # Convert to dict for JSON serialization
        response_dict = {
            "request_id": request_model.request_id,
            "creator_id": creator_score.creator_id,
            "channel_name": creator_score.channel_name,
            "engagement_rate": creator_score.engagement_rate,
            "growth_rate": creator_score.growth_rate,
            "post_consistency": creator_score.post_consistency,
            "audience_quality": creator_score.audience_quality,
            "total_score": creator_score.total_score,
            "local_relevance_score": creator_score.local_relevance_score,
            "sentiment_score": creator_score.sentiment_score,
            "predicted_roi_category": creator_score.predicted_roi_category,
            "tier": creator_score.tier,
            "video_sample_count": creator_score.video_sample_count,
            "analyzed_comment_count": creator_score.analyzed_comment_count,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(status_code=200, content=response_dict)
        
    except Exception as e:
        print(f"Error scoring creator: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Recommendation Endpoint (Simplified)
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/recommend/creators", tags=["Recommendations"])
def recommend_creators(request_model: RecommendationRequestModel):
    """
    Get creator recommendations for a brand.
    Prioritizes local Nigerian/African creators when prefer_local_creators=true.
    
    **Request Body:**
    - `request_id`: Unique request identifier
    - `brand`: Brand profile (target audience, budget, industry)
    - `candidate_creators`: List of creators to evaluate
    - `num_recommendations`: Top N to return (default: 5)
    - `prefer_local_creators`: Prioritize Nigerian/African creators
    - `prefer_pidgin_english`: Boost creators using Pidgin English
    
    **Response:**
    Ranked list of creators with fit scores and predicted ROI
    """
    try:
        # Score all candidates first
        candidate_scores = []
        for creator_request in request_model.candidate_creators:
            # Convert to internal DTO
            ml_request = MLScoringRequest(
                request_id=creator_request.request_id,
                creator_id=creator_request.creator_id,
                channel=ChannelMetricsInput(**creator_request.channel.dict()),
                videos=[
                    VideoMetricsInput(
                        **v.dict(exclude={"comments_sample"}),
                        comments_sample=[
                            CommentInput(**c.dict())
                            for c in v.comments_sample
                        ]
                    )
                    for v in creator_request.videos
                ],
                playlists=[
                    PlaylistMetricsInput(**p.dict())
                    for p in creator_request.playlists
                ],
                timestamp=datetime.utcnow()
            )
            
            # Score individual creator
            creator_score = ml_service.score_creator_minimal(ml_request)
            candidate_scores.append(creator_score)
        
        # Build recommendation request
        brand = BrandProfileInput(
            brand_id=request_model.brand.brand_id,
            brand_name=request_model.brand.brand_name,
            industry=request_model.brand.industry,
            target_age_range=request_model.brand.target_age_range,
            target_gender=request_model.brand.target_gender,
            target_countries=request_model.brand.target_countries,
            budget_range_usd=request_model.brand.budget_range_usd,
            preferred_content_categories=request_model.brand.preferred_content_categories,
            language_preference=request_model.brand.language_preference,
            minimum_subscriber_count=request_model.brand.minimum_subscriber_count,
            maximum_subscriber_count=request_model.brand.maximum_subscriber_count,
            minimum_engagement_rate=request_model.brand.minimum_engagement_rate
        )
        
        rec_request = RecommendationRequest(
            request_id=request_model.request_id,
            brand=brand,
            candidate_scores=candidate_scores,
            num_recommendations=request_model.num_recommendations,
            prefer_local_creators=request_model.prefer_local_creators,
            prefer_pidgin_english=request_model.prefer_pidgin_english,
            timestamp=datetime.utcnow()
        )
        
        # Run recommendation engine
        response = ml_service.recommend_creators_minimal(rec_request)
        
        # Convert to dict for JSON serialization
        response_dict = {
            "request_id": response.request_id,
            "brand_id": response.brand_id,
            "brand_name": response.brand_name,
            "created_at": response.created_at.isoformat(),
            "total_candidates_evaluated": response.total_candidates_evaluated,
            "average_match_score": response.average_match_score,
            "top_performing_categories": response.top_performing_categories,
            "local_creators_prioritized": response.local_creators_prioritized,
            "target_markets": response.target_markets,
            "recommendations": [
                {
                    "creator_id": rec.creator_id,
                    "creator_name": rec.creator_name,
                    "channel_url": rec.channel_url,
                    "subscriber_count": rec.subscriber_count,
                    "engagement_fit_score": rec.engagement_fit_score,
                    "niche_fit_score": rec.niche_fit_score,
                    "local_relevance_score": rec.local_relevance_score,
                    "overall_recommendation_score": rec.overall_recommendation_score,
                    "estimated_reach_for_campaign": rec.estimated_reach_for_campaign,
                    "estimated_engagement_count": rec.estimated_engagement_count,
                    "price_tier_compatibility": rec.price_tier_compatibility,
                    "predicted_roi_category": rec.predicted_roi_category,
                    "recommendation_reason": rec.recommendation_reason,
                    "match_breakdown": rec.match_breakdown
                }
                for rec in response.recommendations
            ]
        }
        
        if response.top_match:
            response_dict["top_match"] = {
                "creator_id": response.top_match.creator_id,
                "creator_name": response.top_match.creator_name,
                "overall_score": response.top_match.overall_recommendation_score
            }
        
        return JSONResponse(status_code=200, content=response_dict)
        
    except Exception as e:
        print(f"Error recommending creators: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Sentiment Analysis Endpoint (Optimized for Pidgin English)
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/analyze/sentiment", tags=["Sentiment"])
def analyze_sentiment(
    comments: List[CommentInput],
    include_emotions: bool = Query(True, description="Include emotion detection")
):
    """
    Analyze sentiment of comments with support for Nigerian Pidgin English.
    
    **Request Body:**
    - List of comment objects with text and metadata
    
    **Response:**
    - Total comments analyzed
    - Sentiment distribution (positive, negative, neutral)
    - Average sentiment score (-1.0 to 1.0)
    - Top emotions (if include_emotions=true)
    - Sentiment quality score (0-100)
    """
    try:
        sentiment_result = ml_service.analyze_comments_batch(
            comments, 
            include_emotions=include_emotions
        )
        
        response_dict = {
            "total_comments_analyzed": sentiment_result.total_comments_analyzed,
            "positive_pct": sentiment_result.positive_pct,
            "negative_pct": sentiment_result.negative_pct,
            "neutral_pct": sentiment_result.neutral_pct,
            "average_sentiment_score": sentiment_result.average_sentiment_score,
            "average_confidence": sentiment_result.average_confidence,
            "top_emotions": sentiment_result.top_emotions,
            "sentiment_trend": sentiment_result.sentiment_trend,
            "sentiment_quality_score": sentiment_result.sentiment_quality_score,
            "sample_positive": [
                {
                    "comment_id": s.comment_id,
                    "text_sample": s.text_sample,
                    "sentiment_score": s.sentiment_score
                }
                for s in sentiment_result.sample_positive[:3]
            ],
            "sample_negative": [
                {
                    "comment_id": s.comment_id,
                    "text_sample": s.text_sample,
                    "sentiment_score": s.sentiment_score
                }
                for s in sentiment_result.sample_negative[:3]
            ]
        }
        
        return JSONResponse(status_code=200, content=response_dict)
        
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Predictive Forecasting Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/predict/forecast", tags=["Predictions"])
def predict_forecast(request_model: PredictiveForecastRequestModel):
    """
    Predict creator performance for upcoming campaigns.
    
    **Request Body:**
    - Creator metrics (channel + videos)
    - Campaign budget and duration
    
    **Response:**
    - Predicted subscriber growth
    - Predicted reach and engagement
    - Estimated ROI and CPM
    - Risk assessment
    """
    try:
        # Create ML request from input
        ml_request = MLScoringRequest(
            request_id=f"forecast_{request_model.creator_id}",
            creator_id=request_model.creator_id,
            channel=ChannelMetricsInput(**request_model.channel.dict()),
            videos=[
                VideoMetricsInput(
                    **v.dict(exclude={"comments_sample"}),
                    comments_sample=[
                        CommentInput(**c.dict())
                        for c in v.comments_sample
                    ]
                )
                for v in request_model.videos
            ],
            timestamp=datetime.utcnow()
        )
        
        # Get creator score first
        creator_score = ml_service.score_creator_minimal(ml_request)
        
        # Generate forecast
        forecast = ml_service.generate_forecast(
            creator_score,
            ml_request,
            request_model.campaign_budget_usd,
            request_model.campaign_duration_days
        )
        
        response_dict = {
            "creator_id": forecast.creator_id,
            "creator_name": forecast.creator_name,
            "predicted_subscriber_growth": forecast.predicted_subscriber_growth,
            "predicted_views_next_30d": forecast.predicted_views_next_30d,
            "predicted_engagement_rate": forecast.predicted_engagement_rate,
            "predicted_reach_for_sponsored": forecast.predicted_reach_for_sponsored,
            "predicted_engagement_for_sponsored": forecast.predicted_engagement_for_sponsored,
            "estimated_cpm": forecast.estimated_cpm,
            "estimated_roi_percentage": forecast.estimated_roi_percentage,
            "estimated_cpm_local_currency": forecast.estimated_cpm_local_currency,
            "prediction_confidence": forecast.prediction_confidence,
            "roi_confidence": forecast.roi_confidence,
            "local_market_confidence": forecast.local_market_confidence,
            "risk_level": forecast.risk_level,
            "risk_factors": forecast.risk_factors
        }
        
        return JSONResponse(status_code=200, content=response_dict)
        
    except Exception as e:
        print(f"Error generating forecast: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Compare Creators Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/compare/creators", tags=["Comparison"])
def compare_creators(request_model: ComparisonRequestModel):
    """
    Compare multiple creators side-by-side.
    
    **Request Body:**
    - List of creator IDs and their scores
    
    **Response:**
    - Best in each category (engagement, growth, consistency, local relevance)
    - Highest ROI potential
    - Comparison insights
    """
    try:
        # Convert creator scores to DashboardCreatorSummary
        summaries = []
        for score_data in request_model.creator_scores:
            summary = DashboardCreatorSummary(
                creator_id=score_data.get("creator_id", ""),
                creator_name=score_data.get("channel_name", ""),
                influence_score=score_data.get("total_score", 0),
                engagement_rate=score_data.get("engagement_rate", 0),
                growth_rate=score_data.get("growth_rate", 0),
                consistency_score=score_data.get("post_consistency", 0),
                local_relevance_score=score_data.get("local_relevance_score", 0),
                predicted_roi_category=score_data.get("predicted_roi_category", "medium"),
                tier=score_data.get("tier", "standard")
            )
            summaries.append(summary)
        
        # Generate comparison
        comparison = ml_service.compare_creators(summaries)
        
        response_dict = {
            "compared_creators": [
                {
                    "creator_id": c.creator_id,
                    "creator_name": c.creator_name,
                    "influence_score": c.influence_score,
                    "engagement_rate": c.engagement_rate,
                    "growth_rate": c.growth_rate,
                    "consistency_score": c.consistency_score,
                    "local_relevance_score": c.local_relevance_score,
                    "tier": c.tier
                }
                for c in comparison.compared_creators
            ],
            "best_in_engagement": {
                "creator_name": comparison.best_in_engagement.creator_name,
                "score": comparison.best_in_engagement.engagement_rate
            } if comparison.best_in_engagement else None,
            "best_in_growth": {
                "creator_name": comparison.best_in_growth.creator_name,
                "score": comparison.best_in_growth.growth_rate
            } if comparison.best_in_growth else None,
            "best_in_consistency": {
                "creator_name": comparison.best_in_consistency.creator_name,
                "score": comparison.best_in_consistency.consistency_score
            } if comparison.best_in_consistency else None,
            "best_in_local_relevance": {
                "creator_name": comparison.best_in_local_relevance.creator_name,
                "score": comparison.best_in_local_relevance.local_relevance_score
            } if comparison.best_in_local_relevance else None,
            "highest_roi_potential": {
                "creator_name": comparison.highest_roi_potential.creator_name,
                "roi_category": comparison.highest_roi_potential.predicted_roi_category
            } if comparison.highest_roi_potential else None,
            "comparison_insights": comparison.comparison_insights,
            "compared_at": comparison.compared_at.isoformat()
        }
        
        return JSONResponse(status_code=200, content=response_dict)
        
    except Exception as e:
        print(f"Error comparing creators: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Batch Scoring Endpoint (for multiple creators)
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/score/batch", tags=["Scoring"])
def batch_score_creators(creators: List[CreatorScoringRequestModel]):
    """
    Score multiple creators in batch.
    Efficient for processing many creators at once.
    
    **Request Body:**
    - List of creator scoring requests
    
    **Response:**
    - List of creator scores
    """
    try:
        batch_results = []
        
        for creator_request in creators:
            request = MLScoringRequest(
                request_id=creator_request.request_id,
                creator_id=creator_request.creator_id,
                channel=ChannelMetricsInput(**creator_request.channel.dict()),
                videos=[
                    VideoMetricsInput(
                        **v.dict(exclude={"comments_sample"}),
                        comments_sample=[
                            CommentInput(**c.dict())
                            for c in v.comments_sample
                        ]
                    )
                    for v in creator_request.videos
                ],
                playlists=[
                    PlaylistMetricsInput(**p.dict())
                    for p in creator_request.playlists
                ],
                timestamp=datetime.utcnow()
            )
            
            creator_score = ml_service.score_creator_minimal(request)
            batch_results.append(creator_score)
        
        # Sort by total score
        batch_results.sort(key=lambda x: x.total_score, reverse=True)
        
        response_dict = {
            "total_processed": len(batch_results),
            "results": [
                {
                    "creator_id": cs.creator_id,
                    "creator_name": cs.channel_name,
                    "total_score": cs.total_score,
                    "engagement_rate": cs.engagement_rate,
                    "growth_rate": cs.growth_rate,
                    "tier": cs.tier,
                    "predicted_roi_category": cs.predicted_roi_category
                }
                for cs in batch_results
            ]
        }
        
        return JSONResponse(status_code=200, content=response_dict)
        
    except Exception as e:
        print(f"Error batch scoring creators: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────────────
# Info Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/info", tags=["System"])
def api_info():
    """Get API information and available endpoints."""
    return {
        "service": "CIAP ML Scoring API",
        "version": "2.0.0",
        "api_type": "Optimized - Minimal YouTube Data API Only",
        "features": [
            "Simplified influence scoring (Engagement 40% + Growth 30% + Consistency 20% + Audience 10%)",
            "Nigerian Pidgin English sentiment analysis",
            "Local market prioritization (NG, KE, GH, ZA, etc.)",
            "Predictive ROI forecasting",
            "Creator comparison tools",
            "Batch processing support"
        ],
        "endpoints": {
            "health": "GET /health",
            "creator_scoring": "POST /score/creator",
            "batch_scoring": "POST /score/batch",
            "recommendations": "POST /recommend/creators",
            "sentiment_analysis": "POST /analyze/sentiment",
            "predictive_forecast": "POST /predict/forecast",
            "compare_creators": "POST /compare/creators",
            "info": "GET /info",
            "docs": "GET /docs (Swagger UI)",
        },
        "data_requirements": {
            "required": [
                "Channel metrics (subscribers, verification, country)",
                "Video metrics (views, likes, comments) from last 8-10 videos",
                "Comment samples (3-5 per video)"
            ],
            "optional": [
                "Playlist data",
                "Video tags for categorization"
            ],
            "not_required": [
                "YouTube Analytics API",
                "Watch time metrics",
                "Demographic data",
                "Traffic sources"
            ]
        },
        "african_market_features": [
            "Nigerian Pidgin English (pcm) support",
            "Local relevance scoring for NG, KE, GH, ZA, TZ, UG",
            "Local currency CPM estimates",
            "Mobile-first optimization",
            "Low bandwidth API design"
        ]
    }


# ──────────────────────────────────────────────────────────────────────────────
# Running the Server
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
    )