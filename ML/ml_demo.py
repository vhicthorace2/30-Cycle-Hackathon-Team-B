"""
Example usage of ML module.
Demonstrates how to use the ML module programmatically (without HTTP).
"""
from datetime import datetime, timedelta
from dto.scoring_input import (
    MLScoringRequest, 
    ChannelMetricsInput, 
    AudienceMetricsInput,
    VideoMetricsInput,
    CommentMetadata,
    RecommendationRequest,
    BrandProfileInput,
)
from ml_orchestrator import MLOrchestratorService


def create_sample_creator_data():
    """Create sample creator data for demonstration."""
    
    # Sample comments
    comments = [
        CommentMetadata(
            comment_id="c1",
            text="This is amazing! Love your content",
            author_id="user1",
            author_name="Fan 1",
            published_at=datetime.utcnow() - timedelta(days=1),
            like_count=50,
            reply_count=2,
            is_from_subscriber=True,
        ),
        CommentMetadata(
            comment_id="c2",
            text="Great video, very helpful",
            author_id="user2",
            author_name="Fan 2",
            published_at=datetime.utcnow() - timedelta(days=2),
            like_count=30,
            reply_count=1,
            is_from_subscriber=True,
        ),
        CommentMetadata(
            comment_id="c3",
            text="Not your best work",
            author_id="user3",
            author_name="Critic",
            published_at=datetime.utcnow() - timedelta(days=2),
            like_count=5,
            reply_count=0,
            is_from_subscriber=False,
        ),
    ]
    
    # Sample videos
    videos = [
        VideoMetricsInput(
            video_id="v1",
            title="How to Get Started with Python",
            description="Learn the basics of Python programming",
            published_at=datetime.utcnow() - timedelta(days=5),
            view_count=50000,
            like_count=2000,
            comment_count=500,
            average_view_duration_seconds=300,
            impressions=100000,
            ctr=5.0,
            video_duration_seconds=600,
            category_id="27",  # Education
            comments_sample=comments,
        ),
        VideoMetricsInput(
            video_id="v2",
            title="Advanced Python Tips",
            description="Pro tips for Python developers",
            published_at=datetime.utcnow() - timedelta(days=10),
            view_count=35000,
            like_count=1400,
            comment_count=350,
            average_view_duration_seconds=250,
            impressions=70000,
            ctr=4.8,
            video_duration_seconds=500,
            category_id="27",
            comments_sample=comments[:2],
        ),
    ]
    
    # Sample channel
    channel = ChannelMetricsInput(
        channel_id="UCExample123",
        channel_name="Code Mastery",
        channel_description="Learn programming with expert tutorials. Python, JavaScript, and more.",
        subscriber_count=50000,
        total_view_count=2000000,
        video_count=120,
        account_creation_date=datetime(2020, 1, 15),
        is_verified=True,
    )
    
    # Sample audience metrics
    audience = AudienceMetricsInput(
        window_days=30,
        views=500000,
        watch_time_minutes=250000,
        subscribers_gained=1000,
        subscribers_lost=200,
        average_view_duration_seconds=280,
        age_13_17_pct=5.0,
        age_18_24_pct=25.0,
        age_25_34_pct=45.0,
        age_35_44_pct=15.0,
        age_45_54_pct=7.0,
        age_55_64_pct=2.0,
        age_65_plus_pct=1.0,
        gender_male_pct=70.0,
        gender_female_pct=28.0,
        gender_other_pct=2.0,
        top_countries=["US", "GB", "CA", "AU", "DE"],
        search_views=200000,
        suggested_views=250000,
        direct_views=50000,
        playlist_views=0,
        mobile_views_pct=75.0,
        desktop_views_pct=20.0,
        tablet_views_pct=5.0,
    )
    
    return MLScoringRequest(
        request_id="demo_req_001",
        creator_id="creator_001",
        channel=channel,
        audience=audience,
        videos=videos,
    )


def create_sample_brand_data():
    """Create sample brand data for recommendations."""
    return BrandProfileInput(
        brand_id="brand_001",
        brand_name="TechLearn Inc",
        brand_description="Online learning platform for programming and tech skills",
        target_audience_age_min=18,
        target_audience_age_max=40,
        target_audience_gender="all",
        target_countries=["US", "GB", "CA"],
        target_interests=["programming", "learning", "technology", "python"],
        budget_min_usd=5000,
        budget_max_usd=50000,
        industry="education",
        previous_collaborations=3,
    )


def demo_creator_scoring():
    """Demonstrate creator scoring."""
    print("\n" + "="*70)
    print("DEMO: Creator Influence Scoring")
    print("="*70)
    
    service = MLOrchestratorService()
    creator_request = create_sample_creator_data()
    
    print("\n📊 Scoring creator: Code Mastery")
    print(f"   Subscribers: {creator_request.channel.subscriber_count:,}")
    print(f"   Videos: {creator_request.channel.video_count}")
    print(f"   Audience window: {creator_request.audience.window_days} days")
    
    # Score creator
    response = service.score_creator(creator_request)
    
    # Display results
    print("\n✅ SCORING RESULTS:")
    print(f"\n🎯 Overall Influence Score: {response.influence_score.overall_influence_score:.1f}/100")
    print(f"   Tier: {response.influence_score.tier.upper()}")
    
    print(f"\n📈 Component Scores:")
    print(f"   • Engagement Quality: {response.engagement_quality.overall_quality_score:.1f}/100")
    print(f"   • Growth & Consistency: {response.growth_consistency.consistency_score:.1f}/100")
    print(f"   • Audience Quality: {response.audience_quality.audience_loyalty_score:.1f}/100")
    
    print(f"\n💬 Engagement Metrics:")
    print(f"   • Engagement Rate: {response.engagement_quality.engagement_rate*100:.2f}%")
    print(f"   • Comment/Like Ratio: {response.engagement_quality.comment_to_like_ratio:.2f}")
    print(f"   • Genuine Comments: {response.engagement_quality.genuine_comment_ratio*100:.1f}%")
    
    print(f"\n📊 Growth Metrics:")
    print(f"   • Monthly Growth: {response.growth_consistency.monthly_growth_rate:.2f}%")
    print(f"   • Churn Rate: {response.growth_consistency.churn_rate:.1f}%")
    print(f"   • Upload Frequency: {response.growth_consistency.upload_frequency_per_week:.1f} videos/week")
    
    print(f"\n😊 Sentiment Analysis:")
    print(f"   • Positive: {response.comment_sentiment.positive_pct:.1f}%")
    print(f"   • Negative: {response.comment_sentiment.negative_pct:.1f}%")
    print(f"   • Neutral: {response.comment_sentiment.neutral_pct:.1f}%")
    print(f"   • Avg Sentiment: {response.comment_sentiment.average_sentiment_score:.2f}")
    
    print(f"\n💪 Strengths:")
    for i, strength in enumerate(response.key_strengths, 1):
        print(f"   {i}. {strength}")
    
    print(f"\n⚠️  Areas for Improvement:")
    for i, improvement in enumerate(response.improvement_areas, 1):
        print(f"   {i}. {improvement}")
    
    print(f"\n📹 Top Video Performance:")
    if response.video_scores:
        top_video = response.video_scores[0]
        print(f"   Title: {top_video.title}")
        print(f"   Engagement: {top_video.engagement_rate*100:.2f}%")
        print(f"   Viral Potential: {top_video.viral_potential_score:.1f}/100")
        print(f"   Conversion Potential: {top_video.conversion_potential_score:.1f}/100")


def demo_recommendations():
    """Demonstrate creator recommendations."""
    print("\n" + "="*70)
    print("DEMO: Brand-Creator Recommendations")
    print("="*70)
    
    service = MLOrchestratorService()
    creator_request = create_sample_creator_data()
    brand = create_sample_brand_data()
    
    # Create recommendation request with multiple creators (for demo, use same creator twice)
    rec_request = RecommendationRequest(
        request_id="rec_demo_001",
        brand=brand,
        candidate_creators=[creator_request] * 3,  # Simulate 3 candidates
        num_recommendations=2,
    )
    
    print(f"\n🏢 Brand: {brand.brand_name}")
    print(f"   Industry: {brand.industry}")
    print(f"   Budget: ${brand.budget_min_usd:,} - ${brand.budget_max_usd:,}")
    print(f"   Target Audience: {brand.target_audience_age_min}-{brand.target_audience_age_max} years")
    print(f"   Interests: {', '.join(brand.target_interests)}")
    
    print(f"\n🔍 Evaluating {len(rec_request.candidate_creators)} candidate creators...")
    
    # Get recommendations
    response = service.recommend_creators(rec_request)
    
    print(f"\n✅ TOP RECOMMENDATIONS:")
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.creator_name}")
        print(f"   📊 Overall Score: {rec.overall_recommendation_score:.1f}/100")
        print(f"   👥 Subscribers: {rec.subscriber_count:,}")
        print(f"   ✅ Audience Fit: {rec.audience_fit_score:.1f}/100")
        print(f"   📈 Engagement Fit: {rec.engagement_fit_score:.1f}/100")
        print(f"   🎯 Niche Fit: {rec.niche_fit_score:.1f}/100")
        print(f"   💰 Price Tier: {rec.price_tier_compatibility}")
        print(f"   📢 Est. Reach: {rec.estimated_reach_for_campaign:,} views")
        print(f"   💬 Est. Engagement: {rec.estimated_engagement_count:,} interactions")
        print(f"   💡 Reason: {rec.recommendation_reason}")


def demo_sentiment_analysis():
    """Demonstrate sentiment analysis."""
    print("\n" + "="*70)
    print("DEMO: Comment Sentiment Analysis")
    print("="*70)
    
    service = MLOrchestratorService()
    
    sample_comments = [
        {
            "id": "c1",
            "text": "This is absolutely amazing! Love your content so much!",
            "author_id": "u1",
            "author_name": "Happy Fan",
            "published_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "c2",
            "text": "Great tutorial! Very helpful and well explained.",
            "author_id": "u2",
            "author_name": "Appreciative Viewer",
            "published_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "c3",
            "text": "I didn't like this video. Not what I was looking for.",
            "author_id": "u3",
            "author_name": "Critical Viewer",
            "published_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "c4",
            "text": "Okay video, nothing special.",
            "author_id": "u4",
            "author_name": "Neutral Watcher",
            "published_at": datetime.utcnow().isoformat(),
        },
    ]
    
    print(f"\n💬 Analyzing {len(sample_comments)} comments...")
    result = service.analyze_sentiment(sample_comments)
    
    print(f"\n✅ SENTIMENT RESULTS:")
    print(f"   Total Analyzed: {result['total_comments']}")
    print(f"\n   Distribution:")
    print(f"   • Positive: {result['sentiment_distribution']['positive_pct']:.1f}%")
    print(f"   • Negative: {result['sentiment_distribution']['negative_pct']:.1f}%")
    print(f"   • Neutral: {result['sentiment_distribution']['neutral_pct']:.1f}%")
    print(f"\n   Average Score: {result['average_sentiment_score']:.2f}")
    print(f"   Trend: {result['sentiment_trend'].upper()}")
    print(f"   Top Emotions: {', '.join(result['top_emotions'])}")


if __name__ == "__main__":
    print("\n🎯 CIAP ML Module - Feature Demonstrations")
    print("\nThis script demonstrates the ML module capabilities without requiring")
    print("the FastAPI server to be running.\n")
    
    try:
        # Run demos
        demo_creator_scoring()
        demo_recommendations()
        demo_sentiment_analysis()
        
        print("\n" + "="*70)
        print("✅ All demonstrations completed successfully!")
        print("="*70)
        print("\n📚 To access the ML module via HTTP endpoints:")
        print("   1. Start the server: python ml_api_server.py")
        print("   2. API docs: http://localhost:8001/docs")
        print("   3. See ML_INTEGRATION_GUIDE.md for backend integration\n")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
