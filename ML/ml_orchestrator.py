# """
# ML Orchestrator Service
# Coordinates all ML modules (scoring, sentiment, recommendations).
# Provides the main API interface that the backend calls into.
# """
# from datetime import datetime
# import json
# from typing import Dict, Any, Optional

# from dto.scoring_input import MLScoringRequest, RecommendationRequest
# from dto.scoring_output import MLScoringResponse
# from core.scoring_engine import ScoringEngine
# from core.sentiment_analyzer import SentimentAnalyzer
# from core.recommendation_engine import RecommendationEngine


# class MLOrchestratorService:
#     """
#     Main service orchestrating all ML operations.
#     Backend calls this service to get scores, recommendations, and sentiment analysis.
#     """
    
#     def __init__(self):
#         """Initialize all ML modules."""
#         self.scoring_engine = ScoringEngine()
#         self.sentiment_analyzer = SentimentAnalyzer()
#         self.recommendation_engine = RecommendationEngine()
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Main ML Scoring Endpoint
#     # ──────────────────────────────────────────────────────────────────────
    
#     def score_creator(self, request: MLScoringRequest) -> MLScoringResponse:
#         """
#         Main entry point for creator scoring.
#         Combines engagement, growth, audience quality, and sentiment analysis.
        
#         Args:
#             request: MLScoringRequest with all creator data from backend
            
#         Returns:
#             MLScoringResponse with complete scoring breakdown
#         """
#         try:
#             # Run scoring engine
#             (
#                 engagement_quality,
#                 growth_consistency,
#                 audience_quality,
#                 influence_score,
#                 video_scores,
#             ) = self.scoring_engine.score_creator(request)
            
#             # Run sentiment analysis on comments
#             all_comments = []
#             for video in request.videos:
#                 all_comments.extend(video.comments_sample)
            
#             comment_sentiment = self.sentiment_analyzer.analyze_comments(all_comments)
            
#             # Update engagement quality with sentiment
#             engagement_quality.sentiment_quality_score = comment_sentiment.average_sentiment_score * 100 if comment_sentiment.average_sentiment_score >= 0 else 50 + (comment_sentiment.average_sentiment_score * 50)
            
#             # Identify key strengths and improvement areas
#             strengths = self._identify_strengths(
#                 engagement_quality,
#                 growth_consistency,
#                 audience_quality,
#                 influence_score,
#             )
            
#             improvements = self._identify_improvements(
#                 engagement_quality,
#                 growth_consistency,
#                 audience_quality,
#                 influence_score,
#             )
            
#             # Build response
#             response = MLScoringResponse(
#                 request_id=request.request_id,
#                 creator_id=request.creator_id,
#                 creator_name=request.channel.channel_name,
#                 processed_at=datetime.utcnow(),
#                 comment_sentiment=comment_sentiment,
#                 engagement_quality=engagement_quality,
#                 growth_consistency=growth_consistency,
#                 audience_quality=audience_quality,
#                 influence_score=influence_score,
#                 video_scores=video_scores,
#                 key_strengths=strengths,
#                 improvement_areas=improvements,
#             )
            
#             return response
            
#         except Exception as e:
#             print(f"Error in score_creator: {e}")
#             raise
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Recommendation Endpoint
#     # ──────────────────────────────────────────────────────────────────────
    
#     def recommend_creators(self, request: RecommendationRequest):
#         """
#         Main entry point for brand-creator recommendations.
        
#         Args:
#             request: RecommendationRequest with brand and candidate creators
            
#         Returns:
#             RecommendationResponse with ranked recommendations
#         """
#         try:
#             response = self.recommendation_engine.recommend(request)
#             return response
#         except Exception as e:
#             print(f"Error in recommend_creators: {e}")
#             raise
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Sentiment Analysis Endpoint (standalone)
#     # ──────────────────────────────────────────────────────────────────────
    
#     def analyze_sentiment(self, comments_data: list):
#         """
#         Standalone sentiment analysis endpoint.
        
#         Args:
#             comments_data: List of comment dictionaries with 'text' field
            
#         Returns:
#             Dict with aggregated sentiment statistics
#         """
#         from dto.scoring_input import CommentMetadata
        
#         # Convert dict to CommentMetadata objects
#         comments = [
#             CommentMetadata(
#                 comment_id=c.get("id", "unknown"),
#                 text=c.get("text", ""),
#                 author_id=c.get("author_id", "unknown"),
#                 author_name=c.get("author_name", "Anonymous"),
#                 published_at=datetime.fromisoformat(c.get("published_at", datetime.utcnow().isoformat())),
#                 like_count=c.get("like_count", 0),
#                 reply_count=c.get("reply_count", 0),
#                 is_from_subscriber=c.get("is_from_subscriber", False),
#                 is_pinned=c.get("is_pinned", False),
#             )
#             for c in comments_data
#         ]
        
#         sentiment_result = self.sentiment_analyzer.analyze_comments(comments)
        
#         return {
#             "total_comments": sentiment_result.total_comments_analyzed,
#             "sentiment_distribution": {
#                 "positive_pct": sentiment_result.positive_pct,
#                 "negative_pct": sentiment_result.negative_pct,
#                 "neutral_pct": sentiment_result.neutral_pct,
#             },
#             "average_sentiment_score": sentiment_result.average_sentiment_score,
#             "top_emotions": sentiment_result.top_emotions,
#             "sentiment_trend": sentiment_result.sentiment_trend,
#         }
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Utility Methods for Response Building
#     # ──────────────────────────────────────────────────────────────────────
    
#     @staticmethod
#     def _identify_strengths(engagement, growth, audience, influence):
#         """Identify top strengths from scoring results."""
#         strengths = []
        
#         if engagement.overall_quality_score >= 80:
#             strengths.append("Exceptional engagement quality with highly engaged audience")
#         elif engagement.overall_quality_score >= 60:
#             strengths.append("Strong engagement metrics")
        
#         if growth.monthly_growth_rate >= 10:
#             strengths.append(f"Impressive {growth.monthly_growth_rate:.1f}% monthly subscriber growth")
#         elif growth.monthly_growth_rate >= 5:
#             strengths.append("Solid subscriber growth trajectory")
        
#         if growth.consistency_score >= 75:
#             strengths.append("Highly consistent upload schedule")
        
#         if audience.subscriber_retention_rate >= 60:
#             strengths.append("Excellent audience retention and loyalty")
        
#         if audience.organic_reach_score >= 60:
#             strengths.append("Strong organic reach - viewers discovering content naturally")
        
#         if influence.tier in ["diamond", "gold"]:
#             strengths.append(f"Top-tier influence ({influence.tier.title()} rank)")
        
#         return strengths[:5]  # Top 5 strengths
    
#     @staticmethod
#     def _identify_improvements(engagement, growth, audience, influence):
#         """Identify areas for improvement."""
#         improvements = []
        
#         if engagement.engagement_rate < 0.02:
#             improvements.append("Increase audience engagement through more interactive content")
        
#         if engagement.comment_to_like_ratio < 0.1:
#             improvements.append("Encourage more comments and discussions in video descriptions")
        
#         if growth.churn_rate > 40:
#             improvements.append("Focus on subscriber retention - high churn rate indicates audience drop-off")
        
#         if growth.consistency_score < 60:
#             improvements.append("Establish more consistent upload schedule for better algorithm favoring")
        
#         if audience.subscriber_retention_rate < 50:
#             improvements.append("Review content strategy - subscribers are canceling frequently")
        
#         if audience.viewer_expansion_rate < 0.5:
#             improvements.append("Optimize for search & recommendations to reach new viewers")
        
#         if influence.risk_score > 0.4:
#             improvements.append(f"Address risk factors: {', '.join(influence.risk_factors)}")
        
#         return improvements[:5]  # Top 5 improvements
    
#     # ──────────────────────────────────────────────────────────────────────
#     # JSON Serialization (for API responses)
#     # ──────────────────────────────────────────────────────────────────────
    
#     @staticmethod
#     def response_to_dict(response: MLScoringResponse) -> Dict[str, Any]:
#         """Convert MLScoringResponse to JSON-serializable dict."""
#         from dataclasses import asdict
        
#         # Convert dataclasses to dicts
#         data = asdict(response)
        
#         # Convert datetime to ISO format
#         def datetime_handler(obj):
#             if isinstance(obj, datetime):
#                 return obj.isoformat()
#             raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
#         # Use custom encoder for datetime
#         return json.loads(json.dumps(data, default=datetime_handler))


"""
ML Orchestrator Service
Optimized for minimal YouTube Data API usage (no Analytics API required).
Coordinates all ML modules (scoring, sentiment, recommendations).

Key Features:
- Simplified scoring using only Data API metrics
- Nigerian Pidgin English sentiment analysis
- Local market prioritization for African creators
- Predictive ROI forecasting
- Batch processing support
"""

from datetime import datetime
import json
from typing import Dict, Any, Optional, List
from dataclasses import asdict

from dto.scoring_input import (
    MLScoringRequest, 
    RecommendationRequest, 
    CommentMetadata,
    BrandProfileInput,
    CreatorScore
)
from dto.scoring_output import (
    MLScoringResponse,
    CommentSentimentBreakdown,
    DashboardCreatorSummary,
    PredictiveForecast,
    ComparisonResult,
    RecommendationResponse,
    RecommendationMatch
)
from core.scoring_engine import ScoringEngine
from core.sentiment_analyzer import SentimentAnalyzer
from core.recommendation_engine import RecommendationEngine


class MLOrchestratorService:
    """
    Main service orchestrating all ML operations.
    Backend calls this service to get scores, recommendations, and sentiment analysis.
    Optimized for minimal API usage and African market focus.
    """
    
    def __init__(self):
        """Initialize all ML modules with minimal data support."""
        self.scoring_engine = ScoringEngine()
        self.sentiment_analyzer = SentimentAnalyzer(model_size="light")
        self.recommendation_engine = RecommendationEngine()
        
        # African country codes for local relevance
        self.african_countries = {
            'NG', 'KE', 'GH', 'ZA', 'TZ', 'UG', 'RW', 'ZM', 'ZW', 
            'SN', 'CI', 'BJ', 'TG', 'ET', 'SO', 'MW', 'MZ', 'AO'
        }
    
    # ──────────────────────────────────────────────────────────────────────
    # Main ML Scoring Endpoint (Minimal Data Version)
    # ──────────────────────────────────────────────────────────────────────
    
    def score_creator_minimal(self, request: MLScoringRequest) -> CreatorScore:
        """
        Main entry point for creator scoring using minimal data.
        Uses only metrics available from YouTube Data API.
        
        Args:
            request: MLScoringRequest with minimal creator data
            
        Returns:
            CreatorScore with simplified scoring breakdown
        """
        try:
            # Run scoring engine with minimal data
            (
                engagement_quality,
                growth_consistency,
                audience_quality,
                influence_score,
                video_scores,
            ) = self.scoring_engine.score_creator(request)
            
            # Run sentiment analysis on comments (limited sample)
            all_comments = []
            for video in request.videos:
                all_comments.extend(video.comments_sample)
            
            comment_sentiment = None
            sentiment_score = 0.0
            if all_comments:
                comment_sentiment = self.sentiment_analyzer.analyze_comments(all_comments)
                # Convert sentiment quality to -1 to 1 scale
                sentiment_score = (comment_sentiment.average_sentiment_score / 50) - 1 if comment_sentiment.average_sentiment_score else 0.0
            
            # Calculate local relevance score
            local_relevance_score = self._calculate_local_relevance(request.channel)
            
            # Determine predicted ROI category
            predicted_roi = self._predict_roi_category(
                influence_score.overall_influence_score,
                engagement_quality.engagement_rate,
                growth_consistency.monthly_growth_rate,
                local_relevance_score
            )
            
            # Build creator score
            creator_score = CreatorScore(
                creator_id=request.creator_id,
                channel_name=request.channel.channel_name,
                engagement_rate=engagement_quality.engagement_rate,
                growth_rate=growth_consistency.monthly_growth_rate,
                post_consistency=growth_consistency.consistency_score,
                audience_quality=audience_quality.audience_loyalty_score,
                total_score=influence_score.overall_influence_score,
                local_relevance_score=local_relevance_score,
                sentiment_score=sentiment_score,
                predicted_roi_category=predicted_roi,
                video_sample_count=len(request.videos),
                analyzed_comment_count=len(all_comments),
                tier=influence_score.tier
            )
            
            return creator_score
            
        except Exception as e:
            print(f"Error in score_creator_minimal: {e}")
            raise
    
    # ──────────────────────────────────────────────────────────────────────
    # Recommendation Endpoint (Minimal Data Version)
    # ──────────────────────────────────────────────────────────────────────
    
    def recommend_creators_minimal(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Main entry point for brand-creator recommendations.
        Prioritizes local African creators when specified.
        
        Args:
            request: RecommendationRequest with brand and candidate creator scores
            
        Returns:
            RecommendationResponse with ranked recommendations
        """
        try:
            # Use recommendation engine
            response = self.recommendation_engine.recommend(request)
            return response
        except Exception as e:
            print(f"Error in recommend_creators_minimal: {e}")
            raise
    
    # ──────────────────────────────────────────────────────────────────────
    # Sentiment Analysis Endpoint (with Pidgin English Support)
    # ──────────────────────────────────────────────────────────────────────
    
    def analyze_comments_batch(
        self, 
        comments_data: list, 
        include_emotions: bool = True
    ) -> CommentSentimentBreakdown:
        """
        Standalone sentiment analysis endpoint with Pidgin English support.
        
        Args:
            comments_data: List of comment dictionaries or CommentMetadata objects
            include_emotions: Whether to include emotion detection
            
        Returns:
            CommentSentimentBreakdown with aggregated sentiment statistics
        """
        # Convert to CommentMetadata objects if needed
        comments = []
        for c in comments_data:
            if isinstance(c, dict):
                comment = CommentMetadata(
                    comment_id=c.get("comment_id", c.get("id", "unknown")),
                    text=c.get("text", ""),
                    author_id=c.get("author_id", "unknown"),
                    author_name=c.get("author_name", "Anonymous"),
                    published_at=datetime.fromisoformat(c.get("published_at", datetime.utcnow().isoformat())) if isinstance(c.get("published_at"), str) else c.get("published_at", datetime.utcnow()),
                    like_count=c.get("like_count", 0),
                    reply_count=c.get("reply_count", 0),
                    is_from_subscriber=c.get("is_from_subscriber", False),
                    is_pinned=c.get("is_pinned", False),
                )
            else:
                comment = c
            comments.append(comment)
        
        # Analyze sentiments
        sentiment_result = self.sentiment_analyzer.analyze_comments(comments)
        
        return sentiment_result
    
    # ──────────────────────────────────────────────────────────────────────
    # Predictive Forecasting Endpoint
    # ──────────────────────────────────────────────────────────────────────
    
    def generate_forecast(
        self,
        creator_score: CreatorScore,
        ml_request: MLScoringRequest,
        campaign_budget_usd: float,
        campaign_duration_days: int = 30
    ) -> PredictiveForecast:
        """
        Generate predictive forecast for creator performance.
        
        Args:
            creator_score: Pre-calculated creator score
            ml_request: Original ML scoring request
            campaign_budget_usd: Budget for campaign
            campaign_duration_days: Campaign duration in days
            
        Returns:
            PredictiveForecast with predictions and ROI estimates
        """
        channel = ml_request.channel
        videos = ml_request.videos
        
        # Predict subscriber growth (based on current growth rate)
        predicted_growth = int(
            channel.subscriber_count * (creator_score.growth_rate / 100) 
            if creator_score.growth_rate > 0 else 0
        )
        
        # Predict views (based on average views per video)
        avg_views = sum(v.view_count for v in videos) / len(videos) if videos else 0
        predicted_views = int(avg_views * (1 + creator_score.growth_rate / 100))
        
        # Predicted engagement rate (slightly lower than organic for sponsored)
        predicted_engagement_rate = creator_score.engagement_rate * 0.7  # 30% drop for sponsored
        
        # Predicted reach for sponsored (30-50% of subscribers for typical campaign)
        predicted_reach = int(channel.subscriber_count * 0.4)
        
        # Predicted engagement count
        predicted_engagement = int(predicted_reach * (predicted_engagement_rate / 100))
        
        # Estimate CPM based on tier and local market
        estimated_cpm = self._estimate_cpm(creator_score.tier, channel.country)
        
        # ROI calculation
        estimated_revenue = (predicted_reach / 1000) * estimated_cpm
        estimated_roi = ((estimated_revenue - campaign_budget_usd) / campaign_budget_usd) * 100
        
        # Confidence scores
        prediction_confidence = min(70 + (creator_score.post_consistency * 0.3), 95)
        roi_confidence = min(65 + (creator_score.total_score * 0.2), 90)
        
        # Risk assessment
        risk_level, risk_factors = self._assess_risk(creator_score, channel)
        
        # Local currency conversion (simplified - would use real exchange rates)
        exchange_rates = {"NG": 1500, "KE": 130, "GH": 12, "ZA": 18}
        local_currency_rate = exchange_rates.get(channel.country, 1)
        estimated_cpm_local = estimated_cpm * local_currency_rate
        
        return PredictiveForecast(
            creator_id=creator_score.creator_id,
            creator_name=creator_score.channel_name,
            predicted_subscriber_growth=predicted_growth,
            predicted_views_next_30d=predicted_views,
            predicted_engagement_rate=predicted_engagement_rate,
            predicted_reach_for_sponsored=predicted_reach,
            predicted_engagement_for_sponsored=predicted_engagement,
            estimated_cpm=estimated_cpm,
            estimated_roi_percentage=estimated_roi,
            estimated_cpm_local_currency=estimated_cpm_local,
            prediction_confidence=prediction_confidence,
            roi_confidence=roi_confidence,
            local_market_confidence=85.0 if channel.country in self.african_countries else 50.0,
            risk_level=risk_level,
            risk_factors=risk_factors
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Creator Comparison Endpoint
    # ──────────────────────────────────────────────────────────────────────
    
    def compare_creators(self, creators: List[DashboardCreatorSummary]) -> ComparisonResult:
        """
        Compare multiple creators side-by-side.
        
        Args:
            creators: List of DashboardCreatorSummary objects
            
        Returns:
            ComparisonResult with best performers in each category
        """
        if not creators:
            return ComparisonResult(compared_creators=[])
        
        # Find best in each category
        best_engagement = max(creators, key=lambda c: c.engagement_rate)
        best_growth = max(creators, key=lambda c: c.growth_rate)
        best_consistency = max(creators, key=lambda c: c.consistency_score)
        best_local = max(creators, key=lambda c: c.local_relevance_score)
        best_roi = max(creators, key=lambda c: 1 if c.predicted_roi_category == "high" else (0.5 if c.predicted_roi_category == "medium" else 0))
        
        # Generate insights
        insights = self._generate_comparison_insights(
            creators, best_engagement, best_growth, best_consistency, best_local
        )
        
        return ComparisonResult(
            compared_creators=creators,
            best_in_engagement=best_engagement,
            best_in_growth=best_growth,
            best_in_consistency=best_consistency,
            best_in_local_relevance=best_local,
            highest_roi_potential=best_roi,
            comparison_insights=insights,
            compared_at=datetime.utcnow()
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Batch Scoring Endpoint
    # ──────────────────────────────────────────────────────────────────────
    
    def batch_score_creators(self, requests: List[MLScoringRequest]) -> List[CreatorScore]:
        """
        Score multiple creators in batch.
        
        Args:
            requests: List of MLScoringRequest objects
            
        Returns:
            List of CreatorScore objects (sorted by total score descending)
        """
        scores = []
        for request in requests:
            try:
                score = self.score_creator_minimal(request)
                scores.append(score)
            except Exception as e:
                print(f"Error scoring creator {request.creator_id}: {e}")
                # Create a minimal score for failed requests
                scores.append(CreatorScore(
                    creator_id=request.creator_id,
                    channel_name=request.channel.channel_name,
                    engagement_rate=0.0,
                    growth_rate=0.0,
                    post_consistency=0.0,
                    audience_quality=0.0,
                    total_score=0.0,
                    tier="standard"
                ))
        
        # Sort by total score descending
        scores.sort(key=lambda x: x.total_score, reverse=True)
        return scores
    
    # ──────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ──────────────────────────────────────────────────────────────────────
    
    @staticmethod
    def _calculate_local_relevance(channel) -> float:
        """
        Calculate local relevance score for African market.
        """
        score = 50.0  # Base score
        
        # Country bonus (Nigeria gets highest)
        if channel.country == 'NG':
            score += 30
        elif channel.country in ['KE', 'GH', 'ZA']:
            score += 20
        elif channel.country in ['TZ', 'UG', 'RW']:
            score += 15
        
        # Custom URL indicates established creator
        if channel.custom_url:
            score += 10
        
        # Verified badge increases trust
        if channel.is_verified:
            score += 10
        
        # Penalty for hidden subscriber count (suspicious)
        if channel.hidden_subscriber_count:
            score -= 30
        
        return min(max(score, 0), 100)
    
    @staticmethod
    def _predict_roi_category(
        influence_score: float,
        engagement_rate: float,
        growth_rate: float,
        local_relevance: float
    ) -> str:
        """
        Predict ROI category based on key metrics.
        """
        roi_score = 0
        
        # Influence score factor (40%)
        if influence_score >= 70:
            roi_score += 40
        elif influence_score >= 50:
            roi_score += 25
        else:
            roi_score += 10
        
        # Engagement rate factor (30%)
        if engagement_rate >= 3.0:
            roi_score += 30
        elif engagement_rate >= 1.5:
            roi_score += 18
        else:
            roi_score += 6
        
        # Growth rate factor (20%)
        if growth_rate >= 5.0:
            roi_score += 20
        elif growth_rate >= 2.0:
            roi_score += 12
        else:
            roi_score += 4
        
        # Local relevance factor (10%)
        roi_score += local_relevance * 0.1
        
        # Categorize
        if roi_score >= 75:
            return "high"
        elif roi_score >= 45:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _estimate_cpm(tier: str, country: str) -> float:
        """
        Estimate CPM based on creator tier and country.
        """
        base_cpm = {
            "diamond": 15.0,
            "gold": 10.0,
            "silver": 7.0,
            "bronze": 5.0,
            "standard": 3.0
        }.get(tier, 5.0)
        
        # Local market adjustment (lower for African markets)
        local_multiplier = 0.7 if country in ['NG', 'KE', 'GH', 'ZA'] else 1.0
        
        return base_cpm * local_multiplier
    
    @staticmethod
    def _assess_risk(creator_score: CreatorScore, channel) -> tuple:
        """
        Assess risk level and identify risk factors.
        """
        risk_factors = []
        risk_score = 0
        
        # Check engagement risk
        if creator_score.engagement_rate < 1.0:
            risk_factors.append("low engagement rate")
            risk_score += 30
        
        # Check growth risk
        if creator_score.growth_rate < 1.0:
            risk_factors.append("slow subscriber growth")
            risk_score += 25
        
        # Check consistency risk
        if creator_score.post_consistency < 40:
            risk_factors.append("inconsistent upload schedule")
            risk_score += 20
        
        # Check audience quality risk
        if creator_score.audience_quality < 40:
            risk_factors.append("poor audience loyalty")
            risk_score += 15
        
        # Check sentiment risk
        if creator_score.sentiment_score < -0.3:
            risk_factors.append("negative audience sentiment")
            risk_score += 20
        
        # Check verification risk
        if not channel.is_verified and channel.subscriber_count > 10000:
            risk_factors.append("unverified channel with large following")
            risk_score += 10
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level, risk_factors
    
    @staticmethod
    def _generate_comparison_insights(creators, best_engagement, best_growth, best_consistency, best_local) -> str:
        """
        Generate human-readable comparison insights.
        """
        insights = []
        
        if best_engagement:
            insights.append(
                f"{best_engagement.creator_name} leads in engagement at {best_engagement.engagement_rate:.1f}%"
            )
        
        if best_growth and best_growth.growth_rate > 0:
            insights.append(
                f"{best_growth.creator_name} shows strongest growth at {best_growth.growth_rate:.1f}% monthly"
            )
        
        if best_consistency and best_consistency.consistency_score > 70:
            insights.append(
                f"{best_consistency.creator_name} is most consistent with {best_consistency.consistency_score:.0f}/100 score"
            )
        
        if best_local and best_local.local_relevance_score > 70:
            insights.append(
                f"{best_local.creator_name} has strongest local market relevance"
            )
        
        # Average performance insight
        avg_score = sum(c.influence_score for c in creators) / len(creators)
        if avg_score >= 70:
            insights.append(f"Overall strong group with {avg_score:.0f}/100 average influence score")
        elif avg_score >= 50:
            insights.append(f"Solid group with {avg_score:.0f}/100 average influence score")
        else:
            insights.append(f"Room for improvement with {avg_score:.0f}/100 average influence score")
        
        return " | ".join(insights)
    
    # ──────────────────────────────────────────────────────────────────────
    # Legacy/Sync Methods (for backward compatibility)
    # ──────────────────────────────────────────────────────────────────────
    
    def score_creator(self, request: MLScoringRequest) -> MLScoringResponse:
        """
        Legacy method for backward compatibility.
        Use score_creator_minimal instead for optimal performance.
        """
        creator_score = self.score_creator_minimal(request)
        
        # Convert CreatorScore to MLScoringResponse for compatibility
        return MLScoringResponse(
            request_id=request.request_id,
            creator_id=request.creator_id,
            creator_name=request.channel.channel_name,
            processed_at=datetime.utcnow(),
            comment_sentiment=CommentSentimentBreakdown(
                total_comments_analyzed=creator_score.analyzed_comment_count,
                positive_pct=0.0,
                negative_pct=0.0,
                neutral_pct=100.0,
                average_sentiment_score=creator_score.sentiment_score,
                sentiment_quality_score=50.0
            ),
            engagement_quality=None,
            growth_consistency=None,
            audience_quality=None,
            influence_score=None,
            video_scores=[],
            key_strengths=[],
            improvement_areas=[],
            local_market_score=creator_score.local_relevance_score,
            estimated_cpm_local=0.0
        )
    
    def recommend_creators(self, request: RecommendationRequest):
        """Legacy method for backward compatibility."""
        return self.recommend_creators_minimal(request)
    
    def analyze_sentiment(self, comments_data: list):
        """Legacy method for backward compatibility."""
        result = self.analyze_comments_batch(comments_data)
        return {
            "total_comments": result.total_comments_analyzed,
            "sentiment_distribution": {
                "positive_pct": result.positive_pct,
                "negative_pct": result.negative_pct,
                "neutral_pct": result.neutral_pct,
            },
            "average_sentiment_score": result.average_sentiment_score,
            "top_emotions": result.top_emotions,
            "sentiment_trend": result.sentiment_trend,
        }
    
    @staticmethod
    def response_to_dict(response: MLScoringResponse) -> Dict[str, Any]:
        """Convert MLScoringResponse to JSON-serializable dict."""
        data = asdict(response)
        
        def datetime_handler(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.loads(json.dumps(data, default=datetime_handler))