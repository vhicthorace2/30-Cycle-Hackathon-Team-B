# """
# Output DTOs that ML module returns to backend after scoring.
# """
# from dataclasses import dataclass, field
# from datetime import datetime
# from typing import Optional, List, Dict


# @dataclass
# class SentimentAnalysisResult:
#     """Sentiment analysis for a single comment or aggregated."""
#     text_sample: str
#     sentiment_label: str  # "positive", "negative", "neutral"
#     sentiment_score: float  # -1.0 to 1.0, where 1.0 is most positive
#     confidence: float  # 0.0 to 1.0
#     emotion_tags: List[str] = field(default_factory=list)  # ["love", "support", "anger", etc.]


# @dataclass
# class CommentSentimentBreakdown:
#     """Aggregated sentiment analysis for all comments."""
#     total_comments_analyzed: int
#     positive_pct: float  # Percentage of positive comments
#     negative_pct: float  # Percentage of negative comments
#     neutral_pct: float  # Percentage of neutral comments
#     average_sentiment_score: float  # Mean sentiment score
#     top_emotions: List[str] = field(default_factory=list)  # Most common emotions
#     sentiment_trend: str = "stable"  # "improving", "declining", "stable"
#     sample_positive: List[SentimentAnalysisResult] = field(default_factory=list)
#     sample_negative: List[SentimentAnalysisResult] = field(default_factory=list)


# @dataclass
# class EngagementQualityScore:
#     """Detailed engagement quality breakdown."""
#     engagement_rate: float  # (likes + comments) / views
#     comment_to_like_ratio: float
#     reply_rate: float  # replies / total comments
#     genuine_comment_ratio: float  # non-spam comments %
#     average_comment_length: float  # Characters
#     sentiment_quality_score: float  # 0-100, based on comment sentiment
#     overall_quality_score: float  # 0-100, weighted composite


# @dataclass
# class GrowthAndConsistencyScore:
#     """Growth metrics and upload consistency."""
#     daily_growth_rate: float  # % daily subscriber change
#     weekly_growth_rate: float  # % weekly subscriber change
#     monthly_growth_rate: float  # % monthly subscriber change
#     growth_momentum_7d: float  # % change this week vs last week
#     growth_momentum_30d: float  # % change this month vs last month
#     churn_rate: float  # % subscribers lost / gained
#     net_subscriber_change: int  # subs_gained - subs_lost
    
#     upload_frequency_per_week: float  # Videos per week
#     consistency_score: float  # 0-100, based on upload regularity
#     days_since_recent_upload: int


# @dataclass
# class AudienceQualityAndLoyalty:
#     """Audience quality indicators."""
#     watch_time_per_subscriber: float  # Minutes watched / subscriber count
#     average_view_duration_ratio: float  # View duration vs video length
#     subscriber_retention_rate: float  # % (subs_gained - subs_lost) / subs_gained
#     repeat_viewer_ratio_estimated: float  # 0-1, estimated from patterns
#     audience_loyalty_score: float  # 0-100, composite loyalty metric
    
#     # Demographics quality
#     audience_age_concentration: float  # 0-1, concentration in target age (if known)
#     audience_geographic_diversity: float  # 0-1, spread across countries
    
#     # Engagement quality
#     viewer_expansion_rate: float  # % views from non-subscribers
#     organic_reach_score: float  # % views from search/suggested (not direct)
#     end_screen_ctr: float  # % of views that clicked end screens
#     card_ctr: float  # % of impressions that clicked cards


# @dataclass
# class InfluenceScore:
#     """Comprehensive influence scoring."""
#     overall_influence_score: float  # 0-100, main KPI
    
#     # Component scores (each 0-100)
#     engagement_quality_weight: float = 0.4
#     engagement_quality_score: float = 0.0
    
#     growth_rate_weight: float = 0.3
#     growth_rate_score: float = 0.0
    
#     consistency_weight: float = 0.2
#     consistency_score: float = 0.0
    
#     audience_quality_weight: float = 0.1
#     audience_quality_score: float = 0.0
    
#     # Risk indicators
#     risk_factors: List[str] = field(default_factory=list)  # ["low-retention", "inconsistent-uploads", etc.]
#     risk_score: float = 0.0  # 0-1, where 1 is high risk
    
#     # Tier classification
#     tier: str = "standard"  # "diamond", "gold", "silver", "bronze", "standard"
    
    
# @dataclass
# class VideoPerformanceScore:
#     """Per-video scoring breakdown."""
#     video_id: str
#     title: str
    
#     engagement_rate: float
#     engagement_percentile: float  # Percentile within creator's own videos
#     performance_rank: int  # Rank within this creator's content
    
#     estimated_reach: float  # Views beyond immediate subscriber base
#     viral_potential_score: float  # 0-100, likelihood to go viral
#     conversion_potential_score: float  # 0-100, likelihood to drive conversions
    
#     content_category_performance: str  # How this category performs


# @dataclass
# class RecommendationMatch:
#     """Creator recommendation for a brand."""
#     creator_id: str
#     creator_name: str
#     channel_url: str
#     subscriber_count: int
    
#     # Matching scores
#     audience_fit_score: float  # 0-100, how well audience matches brand target
#     engagement_fit_score: float  # 0-100, if engagement aligns with expectations
#     niche_fit_score: float  # 0-100, content relevance to brand
#     overall_recommendation_score: float  # 0-100, final score
    
#     # Supporting metrics
#     estimated_reach_for_campaign: int  # Potential viewers
#     estimated_engagement_count: int  # Expected engagement
#     price_tier_compatibility: str  # "perfect", "good", "borderline", "unlikely"
#     match_breakdown: Dict[str, float] = field(default_factory=dict)  # Detailed scoring
    
#     recommendation_reason: str  # Human-readable explanation


# @dataclass
# class MLScoringResponse:
#     """Complete ML scoring response to backend."""
#     request_id: str
#     creator_id: str
#     creator_name: str
#     processed_at: datetime
    
#     # Sentiment analysis
#     comment_sentiment: CommentSentimentBreakdown
    
#     # Engagement scoring
#     engagement_quality: EngagementQualityScore
    
#     # Growth & consistency
#     growth_consistency: GrowthAndConsistencyScore
    
#     # Audience metrics
#     audience_quality: AudienceQualityAndLoyalty
    
#     # Overall influence score
#     influence_score: InfluenceScore
    
#     # Per-video breakdown
#     video_scores: List[VideoPerformanceScore] = field(default_factory=list)
    
#     # Top insights
#     key_strengths: List[str] = field(default_factory=list)
#     improvement_areas: List[str] = field(default_factory=list)


# @dataclass
# class RecommendationResponse:
#     """Response from recommendation engine."""
#     request_id: str
#     brand_id: str
#     brand_name: str
#     created_at: datetime
    
#     recommendations: List[RecommendationMatch] = field(default_factory=list)
#     total_candidates_evaluated: int = 0
#     top_match: Optional[RecommendationMatch] = None


"""
Output DTOs that ML module returns to backend after scoring.
OPTIMIZED for minimal YouTube Data API usage.
Removed fields that require Analytics API or are not available with minimal data.
Added African market specific fields and simplified scoring outputs.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class SentimentAnalysisResult:
    """Sentiment analysis for a single comment or aggregated."""
    comment_id: str  # Added to track which comment
    text_sample: str
    sentiment_label: str  # "positive", "negative", "neutral"
    sentiment_score: float  # -1.0 to 1.0, where 1.0 is most positive
    confidence: float  # 0.0 to 1.0
    emotion_tags: List[str] = field(default_factory=list)  # ["excitement", "support", "criticism", etc.]


@dataclass
class CommentSentimentBreakdown:
    """Aggregated sentiment analysis for all comments (simplified)."""
    total_comments_analyzed: int
    positive_pct: float  # Percentage of positive comments
    negative_pct: float  # Percentage of negative comments
    neutral_pct: float  # Percentage of neutral comments
    average_sentiment_score: float  # Mean sentiment score
    
    # Optional fields (available with minimal data)
    average_confidence: float = 0.0  # Average confidence across comments
    top_emotions: List[str] = field(default_factory=list)  # Most common emotions
    sentiment_trend: str = "stable"  # "improving", "declining", "stable"
    sentiment_quality_score: float = 50.0  # 0-100, overall sentiment health
    
    # Samples (limited to save bandwidth)
    sample_positive: List[SentimentAnalysisResult] = field(default_factory=list)
    sample_negative: List[SentimentAnalysisResult] = field(default_factory=list)


@dataclass
class EngagementQualityScore:
    """
    Detailed engagement quality breakdown.
    Optimized - only fields available with Data API.
    """
    engagement_rate: float  # (likes + comments) / views (as percentage)
    comment_to_like_ratio: float  # Comments per like
    reply_rate: float  # replies / total comments (if available)
    genuine_comment_ratio: float  # non-spam comments % (estimated)
    average_comment_length: float  # Characters
    sentiment_quality_score: float  # 0-100, based on comment sentiment
    overall_quality_score: float  # 0-100, weighted composite


@dataclass
class GrowthAndConsistencyScore:
    """
    Growth metrics and upload consistency.
    No analytics API required - derived from timestamps and video data.
    """
    # Growth metrics (estimated from channel age and video patterns)
    daily_growth_rate: float = 0.0  # % daily subscriber change (estimated)
    weekly_growth_rate: float = 0.0  # % weekly subscriber change (estimated)
    monthly_growth_rate: float = 0.0  # % monthly subscriber change (estimated)
    growth_momentum_7d: float = 0.0  # Estimated momentum
    growth_momentum_30d: float = 0.0  # Estimated momentum
    
    # Simplified - churn not available without analytics API
    churn_rate: float = 0.0  # Placeholder (not available with minimal data)
    net_subscriber_change: int = 0  # Estimated monthly change
    
    # Consistency metrics (from video timestamps)
    upload_frequency_per_week: float = 0.0  # Videos per week
    consistency_score: float = 0.0  # 0-100, based on upload regularity
    days_since_recent_upload: int = 999  # Days since last video


@dataclass
class AudienceQualityAndLoyalty:
    """
    Audience quality indicators.
    Simplified - using only metrics available from Data API.
    """
    # Loyalty metrics (inferred from comments and engagement)
    subscriber_retention_rate: float = 0.0  # Proxy from commenter subscriptions
    repeat_viewer_ratio_estimated: float = 0.0  # 0-1, estimated from patterns
    audience_loyalty_score: float = 0.0  # 0-100, composite loyalty metric
    
    # Removed: watch_time_per_subscriber, average_view_duration_ratio
    # (not available without YouTube Analytics API)
    
    # Simplified demographics quality (inferred where possible)
    audience_age_concentration: float = 0.5  # Default neutral (not available)
    audience_geographic_diversity: float = 0.5  # Default neutral (limited data)
    
    # Simplified engagement quality
    viewer_expansion_rate: float = 0.0  # Estimated from view/subscriber ratio
    organic_reach_score: float = 0.0  # Estimated (not directly available)
    
    # Removed: end_screen_ctr, card_ctr (not available without analytics)


@dataclass
class InfluenceScore:
    """
    Comprehensive influence scoring using simplified formula from tasks:
    Score = (Engagement Rate × 40%) + (Growth Rate × 30%) + 
            (Post Consistency × 20%) + (Audience Quality × 10%)
    """
    overall_influence_score: float  # 0-100, main KPI
    
    # Component scores (each 0-100)
    engagement_quality_score: float = 0.0
    growth_rate_score: float = 0.0
    consistency_score: float = 0.0
    audience_quality_score: float = 0.0
    
    # Weights (from tasks)
    engagement_weight: float = 0.4
    growth_weight: float = 0.3
    consistency_weight: float = 0.2
    audience_weight: float = 0.1
    
    # Risk indicators (simplified)
    risk_factors: List[str] = field(default_factory=list)  # ["low-engagement", "inconsistent-uploads", etc.]
    risk_score: float = 0.0  # 0-1, where 1 is high risk
    
    # Tier classification (adjusted for African market)
    tier: str = "standard"  # "diamond", "gold", "silver", "bronze", "standard"
    
    # African market specific
    local_relevance_bonus: float = 0.0  # Extra points for local creators


@dataclass
class VideoPerformanceScore:
    """
    Per-video scoring breakdown.
    Optimized - only fields available with Data API.
    """
    video_id: str
    title: str
    
    engagement_rate: float  # Percentage
    engagement_percentile: float  # Percentile within creator's own videos
    performance_rank: int  # Rank within this creator's content
    
    estimated_reach: float  # Views beyond immediate subscriber base
    viral_potential_score: float  # 0-100, likelihood to go viral
    conversion_potential_score: float  # 0-100, likelihood to drive conversions
    
    # Content categorization (from tags/title)
    content_category: str = "general"  # "gaming", "tech", "beauty", "fashion", etc.


@dataclass
class RecommendationMatch:
    """
    Creator recommendation for a brand.
    Optimized for minimal data and African market.
    """
    creator_id: str
    creator_name: str
    channel_url: str
    subscriber_count: int  # Estimated from influence score if not directly available
    
    # Matching scores
    audience_fit_score: float = 0.0  # 0-100 (simplified, based on local relevance)
    engagement_fit_score: float = 0.0  # 0-100, based on engagement rate
    niche_fit_score: float = 0.0  # 0-100, content relevance to brand
    overall_recommendation_score: float = 0.0  # 0-100, final score
    
    # Supporting metrics
    estimated_reach_for_campaign: int = 0  # Potential viewers
    estimated_engagement_count: int = 0  # Expected engagement
    price_tier_compatibility: str = "good"  # "perfect", "good", "borderline", "unlikely"
    match_breakdown: Dict[str, float] = field(default_factory=dict)  # Detailed scoring
    
    recommendation_reason: str = ""  # Human-readable explanation
    
    # African market specific
    local_relevance_score: float = 0.0  # 0-100, how relevant to local market
    predicted_roi_category: str = "medium"  # "high", "medium", "low"


@dataclass
class MLScoringResponse:
    """
    Complete ML scoring response to backend.
    Simplified - only includes data from minimal API usage.
    """
    request_id: str
    creator_id: str
    creator_name: str
    processed_at: datetime
    
    # Sentiment analysis (from comments)
    comment_sentiment: Optional[CommentSentimentBreakdown] = None
    
    # Engagement scoring
    engagement_quality: Optional[EngagementQualityScore] = None
    
    # Growth & consistency
    growth_consistency: Optional[GrowthAndConsistencyScore] = None
    
    # Audience metrics (simplified)
    audience_quality: Optional[AudienceQualityAndLoyalty] = None
    
    # Overall influence score (main KPI)
    influence_score: Optional[InfluenceScore] = None
    
    # Per-video breakdown
    video_scores: List[VideoPerformanceScore] = field(default_factory=list)
    
    # Top insights (simplified)
    key_strengths: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    
    # African market specific
    local_market_score: float = 0.0  # 0-100, suitability for Nigerian/African market
    estimated_cpm_local: float = 0.0  # Estimated CPM in local currency


@dataclass
class RecommendationResponse:
    """
    Response from recommendation engine.
    Optimized for brand/SME dashboard display.
    """
    request_id: str
    brand_id: str
    brand_name: str
    created_at: datetime
    
    recommendations: List[RecommendationMatch] = field(default_factory=list)
    total_candidates_evaluated: int = 0
    top_match: Optional[RecommendationMatch] = None
    
    # Aggregated insights (for dashboard)
    average_match_score: float = 0.0
    top_performing_categories: List[str] = field(default_factory=list)
    
    # African market filters summary
    local_creators_prioritized: bool = True
    target_markets: List[str] = field(default_factory=list)


@dataclass
class CreatorScore:
    """
    Simplified creator score for ranking and recommendations.
    Used internally and for dashboard display.
    """
    creator_id: str
    channel_name: str
    
    # Individual metrics (from simplified formula)
    engagement_rate: float  # Percentage
    growth_rate: float  # Monthly percentage
    post_consistency: float  # 0-100
    audience_quality: float  # 0-100
    
    # Final score (0-100)
    total_score: float
    
    # Local relevance (African market)
    local_relevance_score: float = 0.0
    
    # Sentiment (from comment analysis)
    sentiment_score: float = 0.0  # -1 to +1
    
    # Predicted ROI category
    predicted_roi_category: str = "medium"  # "low", "medium", "high"
    
    # For debugging/dashboard display
    video_sample_count: int = 0
    analyzed_comment_count: int = 0
    
    # Tier
    tier: str = "standard"  # "diamond", "gold", "silver", "bronze", "standard"


@dataclass
class DashboardCreatorSummary:
    """
    Simplified creator summary for SME/Agency dashboard.
    Optimized for quick display and filtering.
    """
    creator_id: str
    creator_name: str
    profile_picture_url: Optional[str] = None
    subscriber_count: int = 0
    video_count: int = 0
    
    # Key metrics (for sorting/filtering)
    influence_score: float = 0.0  # 0-100
    engagement_rate: float = 0.0  # Percentage
    growth_rate: float = 0.0  # Monthly percentage
    consistency_score: float = 0.0  # 0-100
    
    # African market specific
    country: str = ""  # NG, KE, GH, etc.
    is_local: bool = False
    local_relevance_score: float = 0.0
    
    # Sentiment summary
    sentiment_score: float = 0.0  # -1 to +1
    audience_sentiment: str = "neutral"  # "positive", "neutral", "negative"
    
    # Tier
    tier: str = "standard"
    
    # Predicted ROI (for brand matching)
    predicted_roi_category: str = "medium"


@dataclass
class PredictiveForecast:
    """
    Predictive forecasting for creator performance.
    Used in SME/Agency dashboard for ROI prediction.
    """
    creator_id: str
    creator_name: str
    
    # Next 30-day predictions
    predicted_subscriber_growth: int = 0
    predicted_views_next_30d: int = 0
    predicted_engagement_rate: float = 0.0  # Percentage
    
    # Campaign predictions (for 1 sponsored video)
    predicted_reach_for_sponsored: int = 0
    predicted_engagement_for_sponsored: int = 0
    estimated_cpm: float = 0.0  # USD
    estimated_roi_percentage: float = 0.0  # Return on investment %
    
    # Confidence scores (0-100)
    prediction_confidence: float = 70.0
    roi_confidence: float = 65.0
    
    # African market specific
    estimated_cpm_local_currency: float = 0.0  # NGN, KES, etc.
    local_market_confidence: float = 75.0  # Higher confidence for local market
    
    # Risk assessment
    risk_level: str = "medium"  # "low", "medium", "high"
    risk_factors: List[str] = field(default_factory=list)


@dataclass
class ComparisonResult:
    """
    Creator comparison result for agency dashboard.
    Allows side-by-side creator comparison.
    """
    compared_creators: List[DashboardCreatorSummary] = field(default_factory=list)
    best_in_engagement: Optional[DashboardCreatorSummary] = None
    best_in_growth: Optional[DashboardCreatorSummary] = None
    best_in_consistency: Optional[DashboardCreatorSummary] = None
    best_in_local_relevance: Optional[DashboardCreatorSummary] = None
    highest_roi_potential: Optional[DashboardCreatorSummary] = None
    
    comparison_insights: str = ""  # Human-readable summary
    
    # Timestamp
    compared_at: datetime = field(default_factory=datetime.utcnow)