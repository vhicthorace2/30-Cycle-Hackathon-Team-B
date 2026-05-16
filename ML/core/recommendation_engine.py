# """
# Recommendation Engine for matching creators with brands.
# Scores creator-brand fit based on audience match, engagement, niche relevance, and ROI potential.
# """
# from typing import List
# from datetime import datetime
# from dto.scoring_input import RecommendationRequest, MLScoringRequest, BrandProfileInput
# from dto.scoring_output import RecommendationMatch, RecommendationResponse, InfluenceScore


# class RecommendationEngine:
#     """
#     Matches creators to brands based on:
#     - Audience demographics alignment (age, location, interests)
#     - Engagement quality fit
#     - Niche/content relevance
#     - Estimated ROI/reach
#     """
    
#     # Matching weights
#     AUDIENCE_FIT_WEIGHT = 0.35
#     ENGAGEMENT_FIT_WEIGHT = 0.25
#     NICHE_FIT_WEIGHT = 0.25
#     INFLUENCE_WEIGHT = 0.15
    
#     # Price tier thresholds (USD)
#     PRICE_TIERS = {
#         "micro": (0, 5000),  # < 5K
#         "mini": (5000, 50000),  # 5K-50K
#         "mid": (50000, 250000),  # 50K-250K
#         "macro": (250000, 1000000),  # 250K-1M
#         "mega": (1000000, float('inf')),  # 1M+
#     }
    
#     def __init__(self):
#         """Initialize recommendation engine."""
#         pass
    
#     def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
#         """
#         Main recommendation method.
#         Scores all candidates against brand profile and returns top N.
        
#         Args:
#             request: RecommendationRequest with brand and candidates
            
#         Returns:
#             RecommendationResponse with ranked recommendations
#         """
#         brand = request.brand
#         candidates = request.candidate_creators
#         num_recommendations = request.num_recommendations
        
#         # Score each candidate
#         scored_matches = []
#         for creator_request in candidates:
#             match = self._score_creator_brand_fit(brand, creator_request)
#             scored_matches.append(match)
        
#         # Sort by overall_recommendation_score (descending)
#         ranked_matches = sorted(
#             scored_matches,
#             key=lambda m: m.overall_recommendation_score,
#             reverse=True
#         )
        
#         # Take top N
#         top_matches = ranked_matches[:num_recommendations]
        
#         # Build response
#         return RecommendationResponse(
#             request_id=request.request_id,
#             brand_id=brand.brand_id,
#             brand_name=brand.brand_name,
#             created_at=datetime.utcnow(),
#             recommendations=top_matches,
#             total_candidates_evaluated=len(candidates),
#             top_match=top_matches[0] if top_matches else None,
#         )
    
#     def _score_creator_brand_fit(
#         self,
#         brand: BrandProfileInput,
#         creator_request: MLScoringRequest,
#     ) -> RecommendationMatch:
#         """
#         Score a single creator-brand pair.
        
#         Returns:
#             RecommendationMatch with detailed scoring breakdown
#         """
#         creator = creator_request.channel
#         audience = creator_request.audience
        
#         # Calculate component scores
#         audience_fit = self._calculate_audience_fit(brand, audience, creator)
#         engagement_fit = self._calculate_engagement_fit(brand, creator_request.videos)
#         niche_fit = self._calculate_niche_fit(brand, creator)
        
#         # Get creator's influence score (would come from scoring engine)
#         # Placeholder: assume medium tier
#         influence_score = 65.0
        
#         # Weighted composite
#         overall_score = (
#             audience_fit * self.AUDIENCE_FIT_WEIGHT +
#             engagement_fit * self.ENGAGEMENT_FIT_WEIGHT +
#             niche_fit * self.NICHE_FIT_WEIGHT +
#             influence_score * self.INFLUENCE_WEIGHT
#         )
        
#         # Estimate reach for this campaign
#         estimated_reach = min(
#             creator.subscriber_count * 0.5,  # ~50% of subs typically see content
#             sum([v.impressions for v in creator_request.videos]) // len(creator_request.videos) if creator_request.videos else 0
#         )
        
#         # Estimate engagement
#         avg_engagement_rate = sum(
#             [(v.like_count + v.comment_count) / v.view_count for v in creator_request.videos if v.view_count > 0]
#         ) / len(creator_request.videos) if creator_request.videos else 0.02
#         estimated_engagement = int(estimated_reach * avg_engagement_rate)
        
#         # Price tier compatibility
#         price_tier = self._get_price_tier(creator.subscriber_count)
        
#         budget_min = brand.budget_min_usd
#         budget_max = brand.budget_max_usd
#         tier_min, tier_max = self.PRICE_TIERS[price_tier]
        
#         if tier_max < budget_min or tier_min > budget_max:
#             compatibility = "unlikely"
#         elif (tier_min <= budget_min and tier_max >= budget_max) or \
#              (budget_min <= tier_min and budget_max >= tier_max):
#             compatibility = "perfect"
#         else:
#             compatibility = "good" if tier_min <= budget_max and tier_max >= budget_min else "borderline"
        
#         # Reason summary
#         if audience_fit > 80:
#             reason = f"Excellent audience fit (ages {brand.target_audience_age_min}-{brand.target_audience_age_max})"
#         elif engagement_fit > 75:
#             reason = f"Strong engagement quality, good brand alignment"
#         elif niche_fit > 75:
#             reason = f"Perfect niche fit for {brand.industry}"
#         else:
#             reason = f"Solid overall metrics across audience, engagement, and niche"
        
#         return RecommendationMatch(
#             creator_id=creator.channel_id,
#             creator_name=creator.channel_name,
#             channel_url=f"https://youtube.com/channel/{creator.channel_id}",
#             subscriber_count=creator.subscriber_count,
#             audience_fit_score=min(audience_fit, 100.0),
#             engagement_fit_score=min(engagement_fit, 100.0),
#             niche_fit_score=min(niche_fit, 100.0),
#             overall_recommendation_score=min(overall_score, 100.0),
#             estimated_reach_for_campaign=int(estimated_reach),
#             estimated_engagement_count=estimated_engagement,
#             price_tier_compatibility=compatibility,
#             match_breakdown={
#                 "audience_fit": audience_fit,
#                 "engagement_fit": engagement_fit,
#                 "niche_fit": niche_fit,
#                 "influence": influence_score,
#             },
#             recommendation_reason=reason,
#         )
    
#     def _calculate_audience_fit(
#         self,
#         brand: BrandProfileInput,
#         audience: any,  # AudienceMetricsInput
#         creator: any,  # ChannelMetricsInput
#     ) -> float:
#         """
#         Score audience demographic fit.
#         Considers: age range, gender, geography, interests.
#         """
#         score = 50.0  # Base score
        
#         # Age fit
#         target_age_min = brand.target_audience_age_min
#         target_age_max = brand.target_audience_age_max
        
#         # Map YouTube age brackets to brand target
#         if 13 <= target_age_min <= 17:
#             age_match = audience.age_13_17_pct
#         elif 18 <= target_age_min <= 24:
#             age_match = audience.age_18_24_pct + audience.age_13_17_pct * 0.2
#         elif 25 <= target_age_min <= 34:
#             age_match = audience.age_25_34_pct + audience.age_18_24_pct * 0.3
#         elif 35 <= target_age_min <= 44:
#             age_match = audience.age_35_44_pct + audience.age_25_34_pct * 0.3
#         else:
#             age_match = 50.0  # Generic
        
#         score += (age_match / 100) * 25  # Age fit up to +25 points
        
#         # Gender fit
#         if brand.target_audience_gender == "male":
#             gender_match = audience.gender_male_pct
#         elif brand.target_audience_gender == "female":
#             gender_match = audience.gender_female_pct
#         else:
#             gender_match = 50.0  # No preference
        
#         score += (gender_match / 100) * 10  # Gender fit up to +10 points
        
#         # Geographic fit
#         brand_country_set = set(brand.target_countries)
#         creator_country_set = set(audience.top_countries)
        
#         if creator_country_set and brand_country_set:
#             overlap = len(brand_country_set & creator_country_set)
#             overlap_pct = overlap / len(brand_country_set) * 100
#             score += overlap_pct * 0.15  # Geography up to +15 points
        
#         return min(score, 100.0)
    
#     def _calculate_engagement_fit(
#         self,
#         brand: BrandProfileInput,
#         videos: List[any],  # List[VideoMetricsInput]
#     ) -> float:
#         """
#         Score engagement quality and consistency.
#         Higher engagement = better for conversions.
#         """
#         if not videos:
#             return 50.0
        
#         # Calculate average engagement rate
#         engagement_rates = [
#             (v.like_count + v.comment_count) / v.view_count
#             if v.view_count > 0 else 0.0
#             for v in videos
#         ]
        
#         avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0
        
#         # Calculate consistency (low variance = consistent)
#         if len(engagement_rates) > 1:
#             import statistics
#             variance = statistics.variance(engagement_rates)
#             consistency = max(0, 100 - (variance * 1000))  # Normalize variance
#         else:
#             consistency = 50.0
        
#         # Engagement quality score
#         # Benchmark: 3% engagement is good, 5%+ is excellent
#         if avg_engagement >= 0.05:
#             engagement_score = 90.0
#         elif avg_engagement >= 0.03:
#             engagement_score = 70.0
#         elif avg_engagement >= 0.01:
#             engagement_score = 50.0
#         else:
#             engagement_score = 30.0
        
#         # Composite
#         fit_score = engagement_score * 0.6 + consistency * 0.4
        
#         return min(fit_score, 100.0)
    
#     def _calculate_niche_fit(
#         self,
#         brand: BrandProfileInput,
#         creator: any,  # ChannelMetricsInput
#     ) -> float:
#         """
#         Score content niche alignment.
#         Based on channel description matching with brand interests/industry.
#         """
#         brand_interests = set([i.lower() for i in brand.target_interests])
#         brand_industry = brand.industry.lower()
        
#         # Parse creator channel description
#         description = creator.channel_description.lower()
        
#         # Simple keyword matching (in production, would use NLP/embeddings)
#         matches = sum(1 for interest in brand_interests if interest in description)
#         industry_match = 1 if brand_industry in description else 0
        
#         # Scoring
#         interest_match_score = (matches / len(brand_interests) * 100) if brand_interests else 50.0
#         industry_match_score = 50.0 if industry_match else 30.0
        
#         niche_score = interest_match_score * 0.6 + industry_match_score * 0.4
        
#         # Boost if explicit category match (would require category tagging)
#         # For now, use description presence as proxy
#         if any(keyword in description for keyword in ["youtube", "creator", "content"]):
#             niche_score += 10
        
#         return min(niche_score, 100.0)
    
#     @staticmethod
#     def _get_price_tier(subscriber_count: int) -> str:
#         """
#         Estimate creator's typical collaboration price tier based on subscribers.
        
#         Rough estimates:
#         - Micro (1K-10K): $500-5K
#         - Mini (10K-50K): $5K-50K
#         - Mid (50K-250K): $50K-250K
#         - Macro (250K-1M): $250K-1M
#         - Mega (1M+): $1M+
#         """
#         if subscriber_count < 10000:
#             return "micro"
#         elif subscriber_count < 50000:
#             return "mini"
#         elif subscriber_count < 250000:
#             return "mid"
#         elif subscriber_count < 1000000:
#             return "macro"
#         else:
#             return "mega"


"""
Recommendation Engine for matching creators with brands.
OPTIMIZED for minimal YouTube Data API usage (no analytics API required).
Scores creator-brand fit based on available metrics: engagement, niche relevance, 
local relevance, and estimated ROI potential.
"""
from typing import List
from datetime import datetime
from dto.scoring_input import (
    RecommendationRequest, 
    MLScoringRequest, 
    BrandProfileInput,
    MinimalAudienceSignal
)
from dto.scoring_output import (
    RecommendationMatch, 
    RecommendationResponse, 
    InfluenceScore,
    CreatorScore
)


class RecommendationEngine:
    """
    Matches creators to brands based on available YouTube Data API metrics:
    - Audience demographic alignment (inferred from comments/engagement)
    - Engagement quality fit
    - Niche/content relevance (from titles, descriptions, tags)
    - Local relevance for Nigerian/African market
    - Estimated ROI based on simplified scoring formula
    """
    
    # Matching weights (adjusted for minimal data availability)
    ENGAGEMENT_FIT_WEIGHT = 0.35  # Most reliable signal
    NICHE_FIT_WEIGHT = 0.30        # From titles/descriptions/tags
    LOCAL_RELEVANCE_WEIGHT = 0.20  # Important for African market
    GROWTH_CONSISTENCY_WEIGHT = 0.15  # From upload patterns
    
    # Price tier thresholds (USD for African market - adjusted lower)
    PRICE_TIERS = {
        "nano": (0, 100),      # <100 USD - 0-1K subs
        "micro": (100, 500),   # 100-500 USD - 1K-5K subs
        "small": (500, 2000),  # 500-2K USD - 5K-20K subs
        "medium": (2000, 10000),  # 2K-10K USD - 20K-100K subs
        "large": (10000, 50000),  # 10K-50K USD - 100K-500K subs
        "mega": (50000, float('inf')),  # 50K+ USD - 500K+ subs
    }
    
    def __init__(self):
        """Initialize recommendation engine."""
        pass
    
    def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Main recommendation method.
        Scores all candidates against brand profile and returns top N.
        
        Args:
            request: RecommendationRequest with brand and pre-calculated creator scores
            
        Returns:
            RecommendationResponse with ranked recommendations
        """
        brand = request.brand
        candidate_scores = request.candidate_scores
        num_recommendations = request.num_recommendations
        prefer_local = request.prefer_local_creators
        
        # Score each candidate
        scored_matches = []
        for creator_score in candidate_scores:
            match = self._score_creator_brand_fit(
                brand, 
                creator_score,
                prefer_local
            )
            scored_matches.append(match)
        
        # Sort by overall_recommendation_score (descending)
        ranked_matches = sorted(
            scored_matches,
            key=lambda m: m.overall_recommendation_score,
            reverse=True
        )
        
        # Take top N
        top_matches = ranked_matches[:num_recommendations]
        
        # Build response
        return RecommendationResponse(
            request_id=request.request_id,
            brand_id=brand.brand_id,
            brand_name=brand.brand_name,
            created_at=datetime.utcnow(),
            recommendations=top_matches,
            total_candidates_evaluated=len(candidate_scores),
            top_match=top_matches[0] if top_matches else None,
        )
    
    def _score_creator_brand_fit(
        self,
        brand: BrandProfileInput,
        creator_score: CreatorScore,
        prefer_local: bool = True,
    ) -> RecommendationMatch:
        """
        Score a single creator-brand pair using minimal available data.
        
        Returns:
            RecommendationMatch with detailed scoring breakdown
        """
        # Extract available metrics from creator_score
        engagement_fit = self._calculate_engagement_fit(
            brand, 
            creator_score.engagement_rate,
            creator_score.sentiment_score
        )
        
        niche_fit = self._calculate_niche_fit(
            brand,
            creator_score.channel_name  # Use channel name as proxy for content
        )
        
        local_relevance = self._calculate_local_relevance(
            brand,
            creator_score.local_relevance_score,
            prefer_local
        )
        
        growth_consistency = self._calculate_growth_consistency_fit(
            creator_score.growth_rate,
            creator_score.post_consistency
        )
        
        # Weighted composite (adjusted for minimal data)
        overall_score = (
            engagement_fit * self.ENGAGEMENT_FIT_WEIGHT +
            niche_fit * self.NICHE_FIT_WEIGHT +
            local_relevance * self.LOCAL_RELEVANCE_WEIGHT +
            growth_consistency * self.GROWTH_CONSISTENCY_WEIGHT
        )
        
        # Estimate reach for campaign (simplified)
        # Assume 10-30% of subscribers see sponsored content typically
        base_reach = creator_score.total_score / 100  # Use influence score as multiplier
        estimated_reach = int(base_reach * 10000)  # Simplified estimation
        
        # Estimate engagement (based on engagement rate)
        estimated_engagement = int(estimated_reach * (creator_score.engagement_rate / 100))
        
        # Price tier compatibility
        price_tier = self._get_price_tier(creator_score.total_score)  # Use score as proxy for pricing
        budget_min = brand.budget_range_usd[0]
        budget_max = brand.budget_range_usd[1]
        tier_min, tier_max = self.PRICE_TIERS[price_tier]
        
        if tier_max < budget_min or tier_min > budget_max:
            compatibility = "unlikely"
        elif (tier_min <= budget_min and tier_max >= budget_max) or \
             (budget_min <= tier_min and budget_max >= tier_max):
            compatibility = "perfect"
        else:
            compatibility = "good" if tier_min <= budget_max and tier_max >= budget_min else "borderline"
        
        # Predicted ROI category from creator_score
        predicted_roi = creator_score.predicted_roi_category
        
        # Reason summary (simplified for minimal data)
        if engagement_fit > 80:
            reason = f"Excellent engagement rate at {creator_score.engagement_rate:.1f}%"
        elif niche_fit > 75:
            reason = f"Strong content alignment with {brand.industry}"
        elif local_relevance > 70:
            reason = f"Perfect local market fit for {', '.join(brand.target_countries)}"
        elif growth_consistency > 70:
            reason = f"Consistent growth and upload schedule"
        else:
            reason = f"Solid overall metrics for {brand.industry} campaign"
        
        # Add ROI note if high potential
        if predicted_roi == "high":
            reason += " with high predicted ROI potential"
        
        return RecommendationMatch(
            creator_id=creator_score.creator_id,
            creator_name=creator_score.channel_name,
            channel_url=f"https://youtube.com/channel/{creator_score.creator_id}",
            subscriber_count=int(creator_score.total_score * 1000),  # Estimate from score
            audience_fit_score=local_relevance,  # Reuse local relevance as audience fit proxy
            engagement_fit_score=engagement_fit,
            niche_fit_score=niche_fit,
            overall_recommendation_score=min(overall_score, 100.0),
            estimated_reach_for_campaign=estimated_reach,
            estimated_engagement_count=estimated_engagement,
            price_tier_compatibility=compatibility,
            match_breakdown={
                "engagement_fit": round(engagement_fit, 1),
                "niche_fit": round(niche_fit, 1),
                "local_relevance": round(local_relevance, 1),
                "growth_consistency": round(growth_consistency, 1),
                "predicted_roi": predicted_roi,
            },
            recommendation_reason=reason,
        )
    
    def _calculate_engagement_fit(
        self,
        brand: BrandProfileInput,
        engagement_rate: float,
        sentiment_score: float,
    ) -> float:
        """
        Score engagement quality from available metrics.
        Higher engagement = better for conversions.
        """
        # Engagement rate scoring (40% of this component)
        # Benchmark for African market: 2% is good, 5%+ is excellent
        if engagement_rate >= 5.0:
            eng_score = 95.0
        elif engagement_rate >= 3.0:
            eng_score = 75.0
        elif engagement_rate >= 1.5:
            eng_score = 55.0
        elif engagement_rate >= 0.5:
            eng_score = 35.0
        else:
            eng_score = 20.0
        
        # Sentiment scoring (30% of this component)
        # sentiment_score ranges -1 to +1
        sentiment_normalized = (sentiment_score + 1) / 2 * 100  # Convert to 0-100
        
        # Consistency/quality score (30% of this component)
        # Based on engagement rate consistency (default 70 if insufficient data)
        consistency_score = 70.0
        
        # Calculate weighted component
        fit_score = (eng_score * 0.4) + (sentiment_normalized * 0.3) + (consistency_score * 0.3)
        
        # Industry-specific adjustments (simplified)
        if brand.industry in ["beauty", "fashion", "gaming"]:
            # These industries value high engagement
            if engagement_rate >= 3.0:
                fit_score *= 1.05
        elif brand.industry in ["finance", "tech", "education"]:
            # These value quality over quantity
            if sentiment_score > 0.3:
                fit_score *= 1.05
        
        return min(fit_score, 100.0)
    
    def _calculate_niche_fit(
        self,
        brand: BrandProfileInput,
        channel_name: str,
    ) -> float:
        """
        Score content niche alignment.
        Uses channel name and brand interests (simplified for minimal data).
        """
        if not channel_name:
            return 50.0
        
        channel_lower = channel_name.lower()
        brand_industry = brand.industry.lower()
        
        # Direct industry keyword matching
        industry_keywords = {
            "fashion": ["fashion", "style", "outfit", "clothing", "wear", "dress"],
            "tech": ["tech", "technology", "gadget", "review", "unboxing", "device", "software"],
            "beauty": ["beauty", "makeup", "cosmetics", "skincare", "hair", "glam"],
            "gaming": ["game", "gaming", "play", "stream", "twitch", "console", "pc gaming"],
            "finance": ["finance", "money", "invest", "stock", "crypto", "trading", "wealth"],
            "health": ["health", "fitness", "workout", "exercise", "wellness", "nutrition", "gym"],
            "education": ["learn", "education", "tutorial", "course", "study", "teach", "academy"],
            "entertainment": ["entertainment", "funny", "comedy", "vlog", "lifestyle", "reaction"],
            "food": ["food", "cooking", "recipe", "kitchen", "cuisine", "meal", "restaurant"],
            "travel": ["travel", "adventure", "tour", "vacation", "trip", "wander", "explore"],
            "sports": ["sports", "sport", "athlete", "fitness", "workout", "training", "football"],
            "music": ["music", "song", "cover", "singer", "band", "instrument", "audio"],
            "business": ["business", "entrepreneur", "startup", "marketing", "sales", "brand"],
        }
        
        # Check if channel name matches brand industry
        keywords = industry_keywords.get(brand_industry, [brand_industry])
        matches = sum(1 for keyword in keywords if keyword in channel_lower)
        
        # Score based on matches
        if matches >= 2:
            niche_score = 85.0 + min((matches - 2) * 5, 15)  # Up to 100
        elif matches == 1:
            niche_score = 70.0
        else:
            # Check for partial matches
            partial_match = any(keyword[:3] in channel_lower for keyword in keywords)
            niche_score = 50.0 if partial_match else 35.0
        
        # Boost for niche-specific content signals
        if any(symbol in channel_lower for symbol in ["official", "tv", "media", "channel"]):
            niche_score += 5
        
        return min(niche_score, 100.0)
    
    def _calculate_local_relevance(
        self,
        brand: BrandProfileInput,
        creator_local_score: float,
        prefer_local: bool,
    ) -> float:
        """
        Score local market relevance (critical for Nigerian/African market).
        """
        if not prefer_local:
            return 50.0  # Neutral if local preference disabled
        
        # Base score from creator's local relevance (0-100)
        local_score = creator_local_score
        
        # Boost based on brand's target countries
        target_countries = set(brand.target_countries)
        
        # African country codes with Nigeria as primary market
        african_countries_NG = {"NG"}  # Nigeria primary
        african_countries_west = {"NG", "GH", "SN", "CI", "BJ", "TG"}
        african_countries_east = {"KE", "TZ", "UG", "RW", "ET", "SO"}
        african_countries_south = {"ZA", "ZW", "ZM", "MW", "MZ", "AO"}
        
        # Calculate country bonus
        country_bonus = 0
        if target_countries & african_countries_NG:
            country_bonus = 15  # Highest for Nigerian market
        elif target_countries & african_countries_west:
            country_bonus = 12
        elif target_countries & african_countries_east:
            country_bonus = 10
        elif target_countries & african_countries_south:
            country_bonus = 8
        
        # Language preference bonus (simplified)
        language_bonus = 0
        if brand.language_preference == "pcm":  # Nigerian Pidgin
            language_bonus = 10  # High value for Pidgin creators
        elif brand.language_preference == "en":
            language_bonus = 5
        
        # Final local relevance score
        relevance_score = (local_score * 0.6) + country_bonus + language_bonus
        
        return min(relevance_score, 100.0)
    
    def _calculate_growth_consistency_fit(
        self,
        growth_rate: float,
        consistency_score: float,
    ) -> float:
        """
        Score creator's growth and consistency for long-term partnership potential.
        """
        # Growth rate scoring (50% of this component)
        # For African market: 5% monthly growth is good
        if growth_rate >= 10.0:
            growth_score = 90.0
        elif growth_rate >= 5.0:
            growth_score = 70.0
        elif growth_rate >= 2.0:
            growth_score = 50.0
        elif growth_rate >= 0.5:
            growth_score = 30.0
        else:
            growth_score = 15.0
        
        # Consistency scoring (50% of this component)
        # consistency_score is already 0-100 from scoring engine
        consistency_normalized = consistency_score
        
        # Weighted composite
        fit_score = (growth_score * 0.5) + (consistency_normalized * 0.5)
        
        return min(fit_score, 100.0)
    
    @staticmethod
    def _get_price_tier(influence_score: float) -> str:
        """
        Estimate creator's collaboration price tier based on influence score.
        Adjusted for African market (lower rates).
        
        Influence score mapping:
        - Nano (0-30): $0-100
        - Micro (30-50): $100-500
        - Small (50-65): $500-2000
        - Medium (65-80): $2000-10000
        - Large (80-90): $10000-50000
        - Mega (90-100): $50000+
        """
        if influence_score < 30:
            return "nano"
        elif influence_score < 50:
            return "micro"
        elif influence_score < 65:
            return "small"
        elif influence_score < 80:
            return "medium"
        elif influence_score < 90:
            return "large"
        else:
            return "mega"
    
    def _estimate_roi_potential(
        self,
        creator_score: CreatorScore,
        brand: BrandProfileInput,
    ) -> str:
        """
        Estimate ROI potential based on available metrics.
        Returns: "high", "medium", or "low"
        """
        roi_score = 0
        
        # Engagement factor
        if creator_score.engagement_rate >= 3.0:
            roi_score += 40
        elif creator_score.engagement_rate >= 1.5:
            roi_score += 25
        else:
            roi_score += 10
        
        # Growth factor
        if creator_score.growth_rate >= 5.0:
            roi_score += 30
        elif creator_score.growth_rate >= 2.0:
            roi_score += 20
        else:
            roi_score += 10
        
        # Sentiment factor
        if creator_score.sentiment_score > 0.3:
            roi_score += 20
        elif creator_score.sentiment_score > 0:
            roi_score += 10
        
        # Local relevance factor (important for African market)
        if creator_score.local_relevance_score >= 70:
            roi_score += 10
        
        # Categorize
        if roi_score >= 70:
            return "high"
        elif roi_score >= 45:
            return "medium"
        else:
            return "low"