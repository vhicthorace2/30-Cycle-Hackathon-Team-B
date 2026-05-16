# """
# ML Scoring Engine for influence scores, engagement quality, growth metrics, and audience analysis.
# All scoring logic and metric calculations are here.
# """
# import statistics
# from typing import List, Optional
# from datetime import datetime

# from core.models import FullAnalyticsSnapshot, ContentItem, TimeSeriesPoint
# from dto.scoring_input import (
#     MLScoringRequest, VideoMetricsInput, AudienceMetricsInput, ChannelMetricsInput
# )
# from dto.scoring_output import (
#     EngagementQualityScore, GrowthAndConsistencyScore, AudienceQualityAndLoyalty,
#     InfluenceScore, VideoPerformanceScore,
# )


# class ScoringEngine:
#     """
#     Comprehensive ML scoring engine.
#     Calculates all derived metrics: engagement quality, growth, loyalty, influence scores.
#     """
    
#     # Influence score component weights
#     ENGAGEMENT_QUALITY_WEIGHT = 0.4
#     GROWTH_RATE_WEIGHT = 0.3
#     CONSISTENCY_WEIGHT = 0.2
#     AUDIENCE_QUALITY_WEIGHT = 0.1
    
#     # Risk thresholds
#     LOW_ENGAGEMENT_THRESHOLD = 0.02  # 2% engagement rate is low
#     HIGH_CHURN_THRESHOLD = 0.4  # 40% churn is high
#     LOW_UPLOAD_FREQUENCY = 0.5  # Less than 1 video per 2 weeks
    
#     def __init__(self):
#         """Initialize scoring engine."""
#         pass
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Main entry point
#     # ──────────────────────────────────────────────────────────────────────
    
#     def score_creator(self, request: MLScoringRequest) -> tuple:
#         """
#         Main scoring method for a creator.
        
#         Returns:
#             Tuple of (
#                 engagement_quality_score,
#                 growth_consistency_score,
#                 audience_quality_score,
#                 influence_score,
#                 video_scores
#             )
#         """
#         # Calculate component scores
#         engagement_quality = self._calculate_engagement_quality(request)
#         growth_consistency = self._calculate_growth_consistency(request)
#         audience_quality = self._calculate_audience_quality(request)
#         video_scores = self._calculate_video_scores(request)
        
#         # Calculate overall influence score
#         influence = self._calculate_influence_score(
#             engagement_quality,
#             growth_consistency,
#             audience_quality,
#         )
        
#         return (
#             engagement_quality,
#             growth_consistency,
#             audience_quality,
#             influence,
#             video_scores,
#         )
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Engagement Quality Scoring
#     # ──────────────────────────────────────────────────────────────────────
    
#     def _calculate_engagement_quality(self, request: MLScoringRequest) -> EngagementQualityScore:
#         """Calculate engagement quality metrics."""
#         videos = request.videos
        
#         if not videos:
#             return EngagementQualityScore(
#                 engagement_rate=0.0,
#                 comment_to_like_ratio=0.0,
#                 reply_rate=0.0,
#                 genuine_comment_ratio=1.0,
#                 average_comment_length=0.0,
#                 sentiment_quality_score=50.0,
#                 overall_quality_score=0.0,
#             )
        
#         # Calculate per-video metrics
#         engagement_rates = []
#         comment_to_like_ratios = []
#         comment_lengths = []
        
#         total_comments = 0
#         total_replies = 0
#         total_genuine_comments = 0
        
#         for video in videos:
#             # Engagement rate: (likes + comments) / views
#             if video.view_count > 0:
#                 eng_rate = (video.like_count + video.comment_count) / video.view_count
#                 engagement_rates.append(eng_rate)
            
#             # Comment to like ratio (inverted to normalize)
#             if video.like_count > 0:
#                 ratio = video.comment_count / video.like_count
#                 comment_to_like_ratios.append(ratio)
            
#             # Comment length analysis
#             for comment in video.comments_sample:
#                 total_comments += 1
#                 total_replies += comment.reply_count
#                 # Spam detection: very short comments (< 5 chars) or duplicates
#                 if len(comment.text) > 5:
#                     total_genuine_comments += 1
#                     comment_lengths.append(len(comment.text))
        
#         # Aggregate metrics
#         avg_engagement = statistics.mean(engagement_rates) if engagement_rates else 0.0
#         avg_comment_like_ratio = statistics.mean(comment_to_like_ratios) if comment_to_like_ratios else 0.0
        
#         reply_rate = (total_replies / total_comments * 100) if total_comments > 0 else 0.0
#         genuine_ratio = (total_genuine_comments / total_comments) if total_comments > 0 else 0.0
#         avg_comment_len = statistics.mean(comment_lengths) if comment_lengths else 0.0
        
#         # Sentiment quality (placeholder: would be filled by sentiment analyzer)
#         sentiment_quality = 75.0  # Default; will be overridden with actual analysis
        
#         # Overall quality score: weighted composite (0-100)
#         quality_score = (
#             self._normalize_to_100(avg_engagement, 0.05) * 0.4 +  # Engagement rate
#             (reply_rate / 100 * 100) * 0.2 +  # Reply engagement
#             (genuine_ratio * 100) * 0.2 +  # Comment authenticity
#             sentiment_quality * 0.2  # Sentiment positivity
#         )
        
#         return EngagementQualityScore(
#             engagement_rate=avg_engagement,
#             comment_to_like_ratio=avg_comment_like_ratio,
#             reply_rate=reply_rate,
#             genuine_comment_ratio=genuine_ratio,
#             average_comment_length=avg_comment_len,
#             sentiment_quality_score=sentiment_quality,
#             overall_quality_score=min(quality_score, 100.0),
#         )
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Growth & Consistency Scoring
#     # ──────────────────────────────────────────────────────────────────────
    
#     def _calculate_growth_consistency(self, request: MLScoringRequest) -> GrowthAndConsistencyScore:
#         """Calculate growth rates, momentum, and upload consistency."""
#         audience = request.audience
#         videos = request.videos
        
#         # Growth rates (percentage change)
#         current_subs = request.channel.subscriber_count
        
#         daily_growth = (audience.subscribers_gained - audience.subscribers_lost) / current_subs * 100 if current_subs > 0 else 0.0
        
#         # Extrapolate to weekly/monthly based on window_days
#         if audience.window_days == 7:
#             weekly_growth = daily_growth * 7
#             monthly_growth = daily_growth * 30
#         elif audience.window_days == 30:
#             daily_growth = daily_growth / 30
#             weekly_growth = daily_growth * 7
#             monthly_growth = daily_growth * 30
#         else:
#             weekly_growth = daily_growth * 7
#             monthly_growth = daily_growth * 30
        
#         # Churn rate
#         churn = (
#             (audience.subscribers_lost / audience.subscribers_gained * 100)
#             if audience.subscribers_gained > 0 else 0.0
#         )
        
#         net_change = audience.subscribers_gained - audience.subscribers_lost
        
#         # Upload consistency
#         if len(videos) > 1:
#             # Calculate days between uploads (reverse chronological)
#             sorted_videos = sorted(videos, key=lambda v: v.published_at, reverse=True)
#             days_between = []
            
#             for i in range(len(sorted_videos) - 1):
#                 delta = (sorted_videos[i].published_at - sorted_videos[i + 1].published_at).days
#                 if delta > 0:
#                     days_between.append(delta)
            
#             if days_between:
#                 avg_days_between = statistics.mean(days_between)
#                 std_dev = statistics.stdev(days_between) if len(days_between) > 1 else 0
#                 # Consistency score: lower std dev = more consistent
#                 consistency_score = max(0, 100 - (std_dev / avg_days_between * 100)) if avg_days_between > 0 else 50.0
                
#                 # Upload frequency: videos per week
#                 upload_freq = (7.0 / avg_days_between) if avg_days_between > 0 else 0.0
                
#                 # Days since recent upload
#                 days_since = (datetime.utcnow() - sorted_videos[0].published_at).days
#             else:
#                 consistency_score = 50.0
#                 upload_freq = 0.0
#                 days_since = 999
#         else:
#             consistency_score = 50.0
#             upload_freq = 0.0
#             days_since = 999
        
#         return GrowthAndConsistencyScore(
#             daily_growth_rate=daily_growth,
#             weekly_growth_rate=weekly_growth,
#             monthly_growth_rate=monthly_growth,
#             growth_momentum_7d=weekly_growth,  # In real impl, compare week-to-week
#             growth_momentum_30d=monthly_growth,  # Compare month-to-month
#             churn_rate=churn,
#             net_subscriber_change=net_change,
#             upload_frequency_per_week=upload_freq,
#             consistency_score=min(consistency_score, 100.0),
#             days_since_recent_upload=days_since,
#         )
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Audience Quality & Loyalty Scoring
#     # ──────────────────────────────────────────────────────────────────────
    
#     def _calculate_audience_quality(self, request: MLScoringRequest) -> AudienceQualityAndLoyalty:
#         """Calculate audience quality, loyalty, and demographics indicators."""
#         audience = request.audience
#         channel = request.channel
#         videos = request.videos
        
#         # Watch time per subscriber
#         watch_min_per_sub = (
#             (audience.watch_time_minutes / channel.subscriber_count)
#             if channel.subscriber_count > 0 else 0.0
#         )
        
#         # Average view duration ratio (vs average video length)
#         avg_video_length = (
#             statistics.mean([v.video_duration_seconds for v in videos]) / 60
#             if videos else 1.0
#         )
#         view_duration_ratio = (
#             (audience.average_view_duration_seconds / 60) / avg_video_length
#             if avg_video_length > 0 else 0.0
#         )
        
#         # Subscriber retention rate: (subs_gained - subs_lost) / subs_gained
#         retention = (
#             ((audience.subscribers_gained - audience.subscribers_lost) / audience.subscribers_gained * 100)
#             if audience.subscribers_gained > 0 else 0.0
#         )
        
#         # Estimated repeat viewer ratio (based on view patterns - simplified)
#         # In practice, would require more granular data
#         repeat_viewer_est = min(1.0, retention / 100.0)
        
#         # Composite loyalty score (0-100)
#         loyalty_score = (
#             retention * 0.5 +  # Retention is primary
#             (repeat_viewer_est * 100) * 0.3 +
#             (watch_min_per_sub * 10) * 0.2  # More watch time = more loyal
#         )
        
#         # Demographics aggregate
#         # Age concentration: how concentrated in target age (assume 25-44 is prime)
#         prime_age_pct = audience.age_25_34_pct + audience.age_35_44_pct
#         age_concentration = prime_age_pct / 100.0
        
#         # Geographic diversity: number of countries (normalized)
#         geographic_diversity = min(1.0, len(audience.top_countries) / 5.0)  # 5+ countries = max diversity
        
#         # Viewer expansion (percentage of views from non-subscribers)
#         total_views = audience.views
#         # Rough estimate: if subs is X and total views is > X*10, many non-subs
#         expansion_rate = min(1.0, (total_views / (channel.subscriber_count * 10)))
        
#         # Organic reach (search + suggested / total)
#         organic_views = audience.search_views + audience.suggested_views
#         organic_reach = (organic_views / total_views * 100) if total_views > 0 else 0.0
        
#         # CTR metrics
#         end_screen_ctr = (
#             (audience.views * 0.1) if videos else 0.0  # Placeholder
#         )
#         card_ctr = audience.ctr if audience else 0.0
        
#         return AudienceQualityAndLoyalty(
#             watch_time_per_subscriber=watch_min_per_sub,
#             average_view_duration_ratio=view_duration_ratio,
#             subscriber_retention_rate=retention,
#             repeat_viewer_ratio_estimated=repeat_viewer_est,
#             audience_loyalty_score=min(loyalty_score, 100.0),
#             audience_age_concentration=age_concentration,
#             audience_geographic_diversity=geographic_diversity,
#             viewer_expansion_rate=expansion_rate,
#             organic_reach_score=organic_reach,
#             end_screen_ctr=end_screen_ctr,
#             card_ctr=card_ctr,
#         )
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Influence Score (Composite)
#     # ──────────────────────────────────────────────────────────────────────
    
#     def _calculate_influence_score(
#         self,
#         engagement: EngagementQualityScore,
#         growth: GrowthAndConsistencyScore,
#         audience: AudienceQualityAndLoyalty,
#     ) -> InfluenceScore:
#         """
#         Calculate overall influence score combining all components.
        
#         Formula:
#         Influence = (Engagement × 0.4) + (Growth × 0.3) + (Consistency × 0.2) + (Audience Quality × 0.1)
#         """
        
#         # Normalize component scores to 0-100 if needed
#         engagement_score = engagement.overall_quality_score
#         growth_score = self._normalize_to_100(growth.monthly_growth_rate, 0.05)
#         consistency_score = growth.consistency_score
#         audience_quality_score = audience.audience_loyalty_score
        
#         # Calculate weighted composite
#         overall_score = (
#             engagement_score * self.ENGAGEMENT_QUALITY_WEIGHT +
#             growth_score * self.GROWTH_RATE_WEIGHT +
#             consistency_score * self.CONSISTENCY_WEIGHT +
#             audience_quality_score * self.AUDIENCE_QUALITY_WEIGHT
#         )
        
#         # Detect risk factors
#         risk_factors = []
#         if engagement.engagement_rate < self.LOW_ENGAGEMENT_THRESHOLD:
#             risk_factors.append("low-engagement")
#         if growth.churn_rate > self.HIGH_CHURN_THRESHOLD:
#             risk_factors.append("high-churn")
#         if growth.upload_frequency_per_week < self.LOW_UPLOAD_FREQUENCY:
#             risk_factors.append("inconsistent-uploads")
#         if audience.subscriber_retention_rate < 50:
#             risk_factors.append("low-retention")
        
#         # Risk score: 0-1 where 1 is high risk
#         risk_score = len(risk_factors) * 0.2  # Each risk factor adds 0.2
        
#         # Tier classification based on score
#         if overall_score >= 90:
#             tier = "diamond"
#         elif overall_score >= 75:
#             tier = "gold"
#         elif overall_score >= 60:
#             tier = "silver"
#         elif overall_score >= 40:
#             tier = "bronze"
#         else:
#             tier = "standard"
        
#         return InfluenceScore(
#             overall_influence_score=min(overall_score, 100.0),
#             engagement_quality_score=engagement_score,
#             growth_rate_score=growth_score,
#             consistency_score=consistency_score,
#             audience_quality_score=audience_quality_score,
#             risk_factors=risk_factors,
#             risk_score=min(risk_score, 1.0),
#             tier=tier,
#         )
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Per-Video Scoring
#     # ──────────────────────────────────────────────────────────────────────
    
#     def _calculate_video_scores(self, request: MLScoringRequest) -> List[VideoPerformanceScore]:
#         """
#         Calculate performance score for each video.
#         """
#         videos = request.videos
        
#         if not videos:
#             return []
        
#         scores = []
        
#         # Calculate percentiles for ranking
#         engagement_rates = [
#             (v.like_count + v.comment_count) / v.view_count
#             if v.view_count > 0 else 0.0
#             for v in videos
#         ]
        
#         if engagement_rates:
#             max_engagement = max(engagement_rates)
#         else:
#             max_engagement = 0.0
        
#         for idx, video in enumerate(videos):
#             # Engagement rate
#             eng_rate = (
#                 (video.like_count + video.comment_count) / video.view_count
#                 if video.view_count > 0 else 0.0
#             )
#             eng_percentile = (eng_rate / max_engagement * 100) if max_engagement > 0 else 0.0
            
#             # Performance rank (1 = best)
#             rank = sorted(
#                 [(i, engagement_rates[i]) for i in range(len(engagement_rates))],
#                 key=lambda x: x[1],
#                 reverse=True
#             )
#             rank_map = {pair[0]: idx + 1 for idx, pair in enumerate(rank)}
#             performance_rank = rank_map[idx]
            
#             # Estimated reach (views beyond subs)
#             estimated_reach = video.view_count - request.channel.subscriber_count
            
#             # Viral potential (high views + high engagement + high CTR)
#             viral_potential = (
#                 self._normalize_to_100(eng_rate * 100, 2.0) * 0.5 +  # Engagement
#                 (video.ctr * 10) * 0.3 +  # CTR
#                 self._normalize_to_100(video.impressions / 1000, 0.5) * 0.2  # Reach
#             )
            
#             # Conversion potential
#             conversion_potential = (
#                 self._normalize_to_100(video.ctr, 5.0) * 0.4 +  # CTR is primary
#                 (eng_rate * 100) * 0.3 +  # Engagement drives conversions
#                 (video.average_view_duration_seconds / video.video_duration_seconds * 100) * 0.3
#             )
            
#             scores.append(VideoPerformanceScore(
#                 video_id=video.video_id,
#                 title=video.title,
#                 engagement_rate=eng_rate,
#                 engagement_percentile=eng_percentile,
#                 performance_rank=performance_rank,
#                 estimated_reach=max(0, estimated_reach),
#                 viral_potential_score=min(viral_potential, 100.0),
#                 conversion_potential_score=min(conversion_potential, 100.0),
#                 content_category_performance="average",  # Would be derived from category analysis
#             ))
        
#         return scores
    
#     # ──────────────────────────────────────────────────────────────────────
#     # Utility Methods
#     # ──────────────────────────────────────────────────────────────────────
    
#     @staticmethod
#     def _normalize_to_100(value: float, target: float) -> float:
#         """
#         Normalize a value to 0-100 scale using a target value.
#         If value == target, returns 100.
#         """
#         if target == 0:
#             return 0.0
#         score = (value / target) * 100
#         return min(score, 100.0)  # Cap at 100


"""
ML Scoring Engine for influence scores, engagement quality, and audience analysis.
OPTIMIZED for minimal YouTube Data API usage (no Analytics API required).
All scoring uses only available metrics from videos.list, channels.list, and commentThreads.list.
"""
import statistics
import math
from typing import List, Optional
from datetime import datetime

from dto.scoring_input import (
    MLScoringRequest, 
    VideoMetricsInput, 
    ChannelMetricsInput,
    CommentMetadata,
    MinimalAudienceSignal
)
from dto.scoring_output import (
    EngagementQualityScore, 
    GrowthAndConsistencyScore,
    AudienceQualityAndLoyalty,
    InfluenceScore, 
    VideoPerformanceScore,
)


class ScoringEngine:
    """
    Optimized ML scoring engine using only YouTube Data API metrics.
    Follows the simplified formula from project tasks:
    Score = (Engagement Rate × 0.4) + (Growth Rate × 0.3) + 
            (Post Consistency × 0.2) + (Audience Quality × 0.1)
    """
    
    # Influence score component weights (from tasks)
    ENGAGEMENT_QUALITY_WEIGHT = 0.4
    GROWTH_RATE_WEIGHT = 0.3
    CONSISTENCY_WEIGHT = 0.2
    AUDIENCE_QUALITY_WEIGHT = 0.1
    
    # Local relevance bonus for Nigerian/African market
    LOCAL_RELEVANCE_BONUS = 5.0  # Extra points for local creators
    
    # Risk thresholds (adjusted for African market patterns)
    LOW_ENGAGEMENT_THRESHOLD = 0.01  # 1% engagement rate (lower barrier for new markets)
    LOW_GROWTH_THRESHOLD = 0.5  # 0.5% monthly growth is concerning
    INCONSISTENT_UPLOAD_THRESHOLD = 25  # >25 days variance = inconsistent
    
    def __init__(self):
        """Initialize scoring engine."""
        pass
    
    # ──────────────────────────────────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────────────────────────────────
    
    def score_creator(self, request: MLScoringRequest) -> tuple:
        """
        Main scoring method for a creator using minimal API data.
        
        Returns:
            Tuple of (
                engagement_quality_score,
                growth_consistency_score,
                audience_quality_score,
                influence_score,
                video_scores
            )
        """
        # Calculate component scores (simplified for minimal data)
        engagement_quality = self._calculate_engagement_quality(request)
        growth_consistency = self._calculate_growth_consistency(request)
        audience_quality = self._calculate_audience_quality(request)
        video_scores = self._calculate_video_scores(request)
        
        # Calculate overall influence score using task formula
        influence = self._calculate_influence_score(
            engagement_quality,
            growth_consistency,
            audience_quality,
            request.channel  # Pass channel for local relevance
        )
        
        return (
            engagement_quality,
            growth_consistency,
            audience_quality,
            influence,
            video_scores,
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Engagement Quality Scoring (40% of final score)
    # ──────────────────────────────────────────────────────────────────────
    
    def _calculate_engagement_quality(self, request: MLScoringRequest) -> EngagementQualityScore:
        """
        Calculate engagement quality metrics.
        Available data: likes, comments, views from videos.
        """
        videos = request.videos
        channel = request.channel
        
        if not videos:
            return EngagementQualityScore(
                engagement_rate=0.0,
                comment_to_like_ratio=0.0,
                reply_rate=0.0,
                genuine_comment_ratio=1.0,
                average_comment_length=0.0,
                sentiment_quality_score=50.0,
                overall_quality_score=0.0,
            )
        
        # Calculate per-video metrics
        engagement_rates = []
        comment_to_like_ratios = []
        comment_lengths = []
        
        total_comments = 0
        total_replies = 0
        total_genuine_comments = 0
        total_likes = 0
        
        for video in videos:
            # Engagement rate: (likes + comments) / views
            if video.view_count > 0:
                eng_rate = (video.like_count + video.comment_count) / video.view_count
                engagement_rates.append(eng_rate)
                total_likes += video.like_count
            
            # Comment to like ratio
            if video.like_count > 0:
                ratio = video.comment_count / video.like_count
                comment_to_like_ratios.append(min(ratio, 2.0))  # Cap at 2.0
            
            # Comment analysis (from limited samples)
            for comment in video.comments_sample:
                total_comments += 1
                total_replies += comment.reply_count
                # Simple spam detection: comments > 10 chars or with likes
                if len(comment.text) > 10 or comment.like_count > 0:
                    total_genuine_comments += 1
                    comment_lengths.append(min(len(comment.text), 500))  # Cap length
        
        # Aggregate metrics
        avg_engagement = statistics.mean(engagement_rates) if engagement_rates else 0.0
        avg_comment_like_ratio = statistics.mean(comment_to_like_ratios) if comment_to_like_ratios else 0.0
        
        reply_rate = (total_replies / total_comments * 100) if total_comments > 0 else 0.0
        genuine_ratio = (total_genuine_comments / total_comments) if total_comments > 0 else 1.0
        avg_comment_len = statistics.mean(comment_lengths) if comment_lengths else 0.0
        
        # Sentiment placeholder (would use spaCy/HuggingFace in production)
        sentiment_quality = 75.0  # Default neutral-positive
        
        # Overall quality score (0-100) - simplified for minimal data
        # Engagement rate normalized: 5% = 100 points
        engagement_score = min((avg_engagement / 0.05) * 100, 100)
        
        quality_score = (
            engagement_score * 0.6 +  # Engagement rate is primary
            (genuine_ratio * 100) * 0.2 +  # Authenticity
            (reply_rate / 100 * 100) * 0.1 +  # Reply rate (if available)
            sentiment_quality * 0.1  # Sentiment
        )
        
        return EngagementQualityScore(
            engagement_rate=avg_engagement * 100,  # Convert to percentage
            comment_to_like_ratio=avg_comment_like_ratio,
            reply_rate=reply_rate,
            genuine_comment_ratio=genuine_ratio,
            average_comment_length=avg_comment_len,
            sentiment_quality_score=sentiment_quality,
            overall_quality_score=min(quality_score, 100.0),
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Growth & Consistency Scoring (30% + 20% = 50% combined)
    # ──────────────────────────────────────────────────────────────────────
    
    def _calculate_growth_consistency(self, request: MLScoringRequest) -> GrowthAndConsistencyScore:
        """
        Calculate growth rates and upload consistency.
        Growth rate is 30% of final score, consistency is 20%.
        """
        channel = request.channel
        videos = request.videos
        growth = request.growth
        
        # Use pre-calculated growth if available, otherwise estimate from timestamps
        if growth:
            monthly_growth = growth.subscriber_growth_rate * 30 if growth.subscriber_growth_rate else 0.0
            daily_growth = growth.subscriber_growth_rate if growth.subscriber_growth_rate else 0.0
            weekly_growth = daily_growth * 7
            net_change = int(channel.subscriber_count * (monthly_growth / 100)) if monthly_growth else 0
            churn_rate = 0.0  # Can't calculate churn without analytics API
        else:
            # Estimate growth from video timestamps and subscriber count
            # This is a rough estimate: newer channels with consistent uploads likely grow faster
            if videos and channel.account_creation_date:
                days_active = (datetime.utcnow() - channel.account_creation_date).days
                if days_active > 0:
                    # Rough daily growth estimate
                    daily_growth = channel.subscriber_count / max(days_active, 1)
                    monthly_growth = daily_growth * 30
                    weekly_growth = daily_growth * 7
                    net_change = int(daily_growth * 30)  # Approximate monthly gain
                else:
                    daily_growth = monthly_growth = weekly_growth = 0.0
                    net_change = 0
            else:
                daily_growth = monthly_growth = weekly_growth = 0.0
                net_change = 0
            churn_rate = 0.0  # Cannot calculate without analytics API
        
        # Upload consistency calculation (20% of final score)
        upload_freq = 0.0
        consistency_score = 0.0
        days_since = 999
        
        if len(videos) >= 3:  # Need at least 3 videos for consistency
            # Sort by publish date (oldest to newest)
            sorted_videos = sorted(videos, key=lambda v: v.published_at)
            
            # Calculate intervals between uploads
            intervals = []
            for i in range(1, len(sorted_videos)):
                delta = (sorted_videos[i].published_at - sorted_videos[i-1].published_at).days
                if delta > 0 and delta < 60:  # Ignore gaps > 60 days
                    intervals.append(delta)
            
            if intervals:
                avg_interval = statistics.mean(intervals)
                upload_freq = 7.0 / avg_interval if avg_interval > 0 else 0.0  # Videos per week
                
                # Consistency score: lower variance = more consistent
                if len(intervals) > 1:
                    std_dev = statistics.stdev(intervals)
                    # Perfect consistency (0 variance) = 100, high variance = 0
                    consistency_score = max(0, 100 - (std_dev / avg_interval * 50))
                else:
                    consistency_score = 75.0  # Single interval, assume consistent
                
                # Penalize very infrequent uploads
                if avg_interval > 14:  # Less than bi-weekly
                    consistency_score *= 0.7
                elif avg_interval > 7:  # Weekly but not more
                    consistency_score *= 0.9
            else:
                upload_freq = 0.0
                consistency_score = 30.0  # Inconsistent or insufficient data
        
        elif len(videos) == 2:
            # Only 2 videos, simple calculation
            delta = (videos[1].published_at - videos[0].published_at).days
            if 0 < delta < 30:
                upload_freq = 7.0 / delta
                consistency_score = 50.0  # Neutral for small sample
            else:
                upload_freq = 0.0
                consistency_score = 25.0
        
        # Days since last upload
        if videos:
            latest_video = max(videos, key=lambda v: v.published_at)
            days_since = (datetime.utcnow() - latest_video.published_at).days
        
        # Normalize growth score: 10% monthly growth = 100 points
        growth_score = min((monthly_growth / 10.0) * 100, 100) if monthly_growth > 0 else 0
        
        return GrowthAndConsistencyScore(
            daily_growth_rate=daily_growth,
            weekly_growth_rate=weekly_growth,
            monthly_growth_rate=monthly_growth,
            growth_momentum_7d=weekly_growth,
            growth_momentum_30d=monthly_growth,
            churn_rate=churn_rate,
            net_subscriber_change=net_change,
            upload_frequency_per_week=upload_freq,
            consistency_score=consistency_score,
            days_since_recent_upload=days_since,
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Audience Quality & Loyalty Scoring (10% of final score)
    # ──────────────────────────────────────────────────────────────────────
    
    def _calculate_audience_quality(self, request: MLScoringRequest) -> AudienceQualityAndLoyalty:
        """
        Calculate audience quality from available data.
        Now uses inferred signals instead of analytics API.
        """
        channel = request.channel
        videos = request.videos
        
        # Calculate engagement-based loyalty signals
        total_views = sum(v.view_count for v in videos) if videos else 0
        total_likes = sum(v.like_count for v in videos) if videos else 0
        total_comments = sum(v.comment_count for v in videos) if videos else 0
        
        # Estimate subscriber loyalty from commenter subscriptions
        commenter_subscribers = 0
        total_commenters = 0
        
        for video in videos:
            for comment in video.comments_sample:
                total_commenters += 1
                if comment.author_subscriber_count > 0:
                    commenter_subscribers += 1
        
        estimated_subscriber_loyalty = (commenter_subscribers / total_commenters) if total_commenters > 0 else 0.5
        
        # Engagement ratios (proxy for audience quality)
        like_view_ratio = total_likes / total_views if total_views > 0 else 0
        comment_view_ratio = total_comments / total_views if total_views > 0 else 0
        
        # Quality score (0-100)
        # Higher ratios = more engaged audience
        loyalty_score = (
            (estimated_subscriber_loyalty * 100) * 0.4 +
            (min(like_view_ratio * 100, 10) / 10 * 100) * 0.3 +  # Normalize 10% like rate = 100
            (min(comment_view_ratio * 1000, 5) / 5 * 100) * 0.3   # Normalize 0.5% comment rate = 100
        )
        
        # Bonus for verified channels (trust signal)
        if channel.is_verified:
            loyalty_score += 10
        
        # Geographic diversity (from channel country & custom URL signals)
        has_local_relevance = channel.country in ['NG', 'KE', 'GH', 'ZA', 'TZ', 'UG'] if channel.country else False
        
        # Organic reach proxy: channels with custom URLs often have better discovery
        organic_reach_score = 50.0
        if channel.custom_url:
            organic_reach_score = 65.0
        if channel.is_verified:
            organic_reach_score = 75.0
        
        return AudienceQualityAndLoyalty(
            watch_time_per_subscriber=0.0,  # Not available without analytics API
            average_view_duration_ratio=0.0,  # Not available without analytics API
            subscriber_retention_rate=loyalty_score,  # Use loyalty as retention proxy
            repeat_viewer_ratio_estimated=estimated_subscriber_loyalty,
            audience_loyalty_score=min(loyalty_score, 100.0),
            audience_age_concentration=0.5,  # Not available without analytics
            audience_geographic_diversity=0.5,  # Limited data
            viewer_expansion_rate=like_view_ratio * 10,  # Proxy for new viewer interest
            organic_reach_score=organic_reach_score,
            end_screen_ctr=0.0,  # Not available
            card_ctr=0.0,  # Not available
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Influence Score (Composite) - Using Task Formula
    # ──────────────────────────────────────────────────────────────────────
    
    def _calculate_influence_score(
        self,
        engagement: EngagementQualityScore,
        growth: GrowthAndConsistencyScore,
        audience: AudienceQualityAndLoyalty,
        channel: ChannelMetricsInput,
    ) -> InfluenceScore:
        """
        Calculate overall influence score using the formula from tasks:
        Score = (Engagement Rate × 0.4) + (Growth Rate × 0.3) + 
                (Post Consistency × 0.2) + (Audience Quality × 0.1)
        """
        
        # Extract raw component scores
        engagement_rate = engagement.engagement_rate  # Already percentage
        growth_rate = growth.monthly_growth_rate
        consistency_score = growth.consistency_score
        audience_quality_score = audience.audience_loyalty_score
        
        # Normalize to 0-100 scale
        # Engagement: 5% = 100 points
        eng_normalized = min(engagement_rate / 5.0 * 100, 100)
        
        # Growth: 10% monthly = 100 points
        growth_normalized = min(growth_rate / 10.0 * 100, 100) if growth_rate > 0 else 0
        
        # Consistency: already 0-100
        consistency_normalized = consistency_score
        
        # Audience quality: already 0-100
        audience_normalized = audience_quality_score
        
        # Calculate weighted composite (task formula)
        overall_score = (
            eng_normalized * self.ENGAGEMENT_QUALITY_WEIGHT +
            growth_normalized * self.GROWTH_RATE_WEIGHT +
            consistency_normalized * self.CONSISTENCY_WEIGHT +
            audience_normalized * self.AUDIENCE_QUALITY_WEIGHT
        )
        
        # Add local relevance bonus for Nigerian/African creators
        local_bonus = 0.0
        if channel.country in ['NG', 'KE', 'GH', 'ZA', 'TZ', 'UG']:
            local_bonus = self.LOCAL_RELEVANCE_BONUS
        overall_score = min(overall_score + local_bonus, 100)
        
        # Detect risk factors (simplified for minimal data)
        risk_factors = []
        if engagement.engagement_rate < self.LOW_ENGAGEMENT_THRESHOLD * 100:
            risk_factors.append("low-engagement")
        if growth_rate < self.LOW_GROWTH_THRESHOLD and growth_rate > 0:
            risk_factors.append("low-growth")
        if consistency_score < 50:
            risk_factors.append("inconsistent-uploads")
        if not channel.is_verified and channel.subscriber_count < 1000:
            risk_factors.append("unverified-small-channel")
        if audience_normalized < 40:
            risk_factors.append("low-audience-loyalty")
        
        # Risk score: 0-1
        risk_score = min(len(risk_factors) * 0.15, 1.0)
        
        # Tier classification based on score
        if overall_score >= 85:
            tier = "diamond"
        elif overall_score >= 70:
            tier = "gold"
        elif overall_score >= 55:
            tier = "silver"
        elif overall_score >= 40:
            tier = "bronze"
        else:
            tier = "standard"
        
        return InfluenceScore(
            overall_influence_score=overall_score,
            engagement_quality_score=eng_normalized,
            growth_rate_score=growth_normalized,
            consistency_score=consistency_normalized,
            audience_quality_score=audience_normalized,
            risk_factors=risk_factors,
            risk_score=risk_score,
            tier=tier,
        )
    
    # ──────────────────────────────────────────────────────────────────────
    # Per-Video Scoring
    # ──────────────────────────────────────────────────────────────────────
    
    def _calculate_video_scores(self, request: MLScoringRequest) -> List[VideoPerformanceScore]:
        """
        Calculate performance score for each video using available metrics.
        """
        videos = request.videos
        channel = request.channel
        
        if not videos:
            return []
        
        scores = []
        
        # Calculate percentiles for ranking
        engagement_rates = [
            (v.like_count + v.comment_count) / v.view_count * 100
            if v.view_count > 0 else 0.0
            for v in videos
        ]
        
        if engagement_rates:
            max_engagement = max(engagement_rates)
        else:
            max_engagement = 0.0
        
        for idx, video in enumerate(videos):
            # Engagement rate (%)
            eng_rate = (
                (video.like_count + video.comment_count) / video.view_count * 100
                if video.view_count > 0 else 0.0
            )
            eng_percentile = (eng_rate / max_engagement * 100) if max_engagement > 0 else 0.0
            
            # Performance rank (1 = best)
            ranked = sorted(
                [(i, engagement_rates[i]) for i in range(len(engagement_rates))],
                key=lambda x: x[1],
                reverse=True
            )
            rank = [i for i, (pos, _) in enumerate(ranked) if pos == idx][0] + 1
            
            # Estimated reach (views beyond subscribers - rough estimate)
            estimated_reach = max(0, video.view_count - channel.subscriber_count)
            
            # Viral potential: high engagement + high view count
            viral_potential = (
                (eng_rate / 10.0 * 100) * 0.6 +  # 10% engagement = 100
                (min(video.view_count / 100000, 1.0) * 100) * 0.4  # 100k views = 100
            )
            
            # Conversion potential (estimated from like/comment ratio)
            if video.view_count > 0:
                like_rate = video.like_count / video.view_count * 100
                conversion_potential = min(like_rate * 10, 100)  # 10% like rate = 100
            else:
                conversion_potential = 0.0
            
            # Content category from tags (simplified)
            category = "general"
            if video.tags:
                gaming_tags = ["game", "gaming", "play", "minecraft", "fortnite"]
                tech_tags = ["tech", "review", "unboxing", "gadget"]
                if any(tag.lower() in gaming_tags for tag in video.tags):
                    category = "gaming"
                elif any(tag.lower() in tech_tags for tag in video.tags):
                    category = "technology"
            
            scores.append(VideoPerformanceScore(
                video_id=video.video_id,
                title=video.title,
                engagement_rate=eng_rate,
                engagement_percentile=eng_percentile,
                performance_rank=rank,
                estimated_reach=estimated_reach,
                viral_potential_score=min(viral_potential, 100.0),
                conversion_potential_score=min(conversion_potential, 100.0),
                content_category_performance=category,
            ))
        
        return scores
    
    # ──────────────────────────────────────────────────────────────────────
    # Utility Methods
    # ──────────────────────────────────────────────────────────────────────
    
    @staticmethod
    def _normalize_to_100(value: float, target: float) -> float:
        """Normalize a value to 0-100 scale using a target value."""
        if target == 0:
            return 0.0
        score = (value / target) * 100
        return min(score, 100.0)