# Backend API Mapping: YouTube API → ML Module

Quick reference for transforming YouTube API responses into ML module request format.

## YouTube APIs Used

```
google-auth-library (OAuth)
  ↓
youtube-python-client (v3)
  ├── youtube.channels.list()
  ├── youtube.videos.list()
  ├── youtube.commentThreads.list()
  └── youtubeAnalytics.reports.query()
```

## Data Transformation Examples

### 1. Channel Data

**YouTube API → Channel DTO**

```python
# YouTube: youtube.channels.list(part='snippet,statistics')
youtube_response = {
  "items": [{
    "id": "UCabcdef123",
    "snippet": {
      "title": "My Channel",
      "description": "About this channel...",
      "publishedAt": "2020-01-15T00:00:00Z",
      "thumbnails": {"high": {"url": "https://..."}}
    },
    "statistics": {
      "viewCount": "2000000",
      "commentCount": "500",
      "subscriberCount": "50000",
      "videoCount": "120"
    },
    "status": {"isLinked": true}
  }]
}

# Transform to:
channel = ChannelMetricsInput(
    channel_id=response['items'][0]['id'],
    channel_name=response['items'][0]['snippet']['title'],
    channel_description=response['items'][0]['snippet']['description'],
    subscriber_count=int(response['items'][0]['statistics']['subscriberCount']),
    total_view_count=int(response['items'][0]['statistics']['viewCount']),
    video_count=int(response['items'][0]['statistics']['videoCount']),
    account_creation_date=datetime.fromisoformat(
        response['items'][0]['snippet']['publishedAt'].replace('Z', '+00:00')
    ),
    is_verified=response['items'][0]['status']['isLinked'],
    profile_picture_url=response['items'][0]['snippet']['thumbnails']['high']['url'],
)
```

### 2. Video Data

**YouTube API → Video DTOs**

```python
# YouTube: youtube.videos.list(part='snippet,statistics,contentDetails')
youtube_videos = {
  "items": [{
    "id": "video123",
    "snippet": {
      "title": "Video Title",
      "description": "...",
      "publishedAt": "2024-01-15T10:00:00Z",
      "categoryId": "1",
      "thumbnails": {"high": {"url": "https://..."}}
    },
    "statistics": {
      "viewCount": "50000",
      "likeCount": "2000",
      "commentCount": "500"
    },
    "contentDetails": {
      "duration": "PT10M30S"  # ISO 8601 format
    }
  }]
}

# Parse duration
import isodate
duration = isodate.parse_duration(
    response['contentDetails']['duration']
).total_seconds()

# Transform to:
videos = []
for item in youtube_videos['items']:
    video = VideoMetricsInput(
        video_id=item['id'],
        title=item['snippet']['title'],
        description=item['snippet']['description'],
        published_at=datetime.fromisoformat(
            item['snippet']['publishedAt'].replace('Z', '+00:00')
        ),
        view_count=int(item['statistics']['viewCount']),
        like_count=int(item['statistics'].get('likeCount', 0)),
        comment_count=int(item['statistics'].get('commentCount', 0)),
        average_view_duration_seconds=0,  # From Analytics API
        impressions=0,  # From Analytics API
        ctr=0.0,  # From Analytics API
        video_duration_seconds=int(duration),
        category_id=item['snippet']['categoryId'],
        thumbnail_url=item['snippet']['thumbnails']['high']['url'],
    )
    videos.append(video)
```

### 3. YouTube Analytics API

**Analytics API → Audience DTO**

```python
# YouTube Analytics API: youtubeAnalytics.reports.query()
# Collect data over 30-day window for a single report

from datetime import datetime, timedelta

start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
end_date = datetime.utcnow().strftime('%Y-%m-%d')

# Query with multiple dimensions for aggregated stats
analytics_response = {
  "rows": [
    [
      "2024-01-15",  # date dimension
      "500000",      # views metric
      "250000",      # estimatedMinutesWatched metric
      "1000",        # subscribersGained metric
      "200",         # subscribersLost metric
      "280",         # averageViewDuration metric
      "100000",      # impressions metric
      "5.0"          # ctr metric
    ]
  ]
}

# For demographics, make separate query with dimensions
# youtubeAnalytics.reports.query(
#   dimensions='ageGroup',
#   metrics='views'
# )
demographics_response = {
  "rows": [
    ["13-17", "25000"],
    ["18-24", "75000"],
    ["25-34", "225000"],
    ["35-44", "150000"],
    ["45-54", "20000"],
    ["55-64", "5000"],
    ["65+", "1000"]
  ]
}

# Transform to:
# Aggregate time series data
total_views = sum(int(row[1]) for row in analytics_response['rows'])
total_watch_time = sum(int(row[2]) for row in analytics_response['rows'])
total_subs_gained = sum(int(row[3]) for row in analytics_response['rows'])
total_subs_lost = sum(int(row[4]) for row in analytics_response['rows'])
avg_view_duration = sum(int(row[5]) for row in analytics_response['rows']) // len(analytics_response['rows'])

# Parse demographics (calculate percentages)
demo_total = sum(int(row[1]) for row in demographics_response['rows'])
demo_dict = {row[0]: int(row[1]) / demo_total * 100 for row in demographics_response['rows']}

audience = AudienceMetricsInput(
    window_days=30,
    views=total_views,
    watch_time_minutes=total_watch_time,
    subscribers_gained=total_subs_gained,
    subscribers_lost=total_subs_lost,
    average_view_duration_seconds=avg_view_duration,
    age_13_17_pct=demo_dict.get('13-17', 0.0),
    age_18_24_pct=demo_dict.get('18-24', 0.0),
    age_25_34_pct=demo_dict.get('25-34', 0.0),
    age_35_44_pct=demo_dict.get('35-44', 0.0),
    age_45_54_pct=demo_dict.get('45-54', 0.0),
    age_55_64_pct=demo_dict.get('55-64', 0.0),
    age_65_plus_pct=demo_dict.get('65+', 0.0),
    # ... repeat for gender breakdown from separate query
)
```

### 4. Comments Data

**YouTube API → Comment DTOs**

```python
# YouTube: youtube.commentThreads.list(
#   part='snippet',
#   videoId='xxx',
#   maxResults=100
# )
comments_response = {
  "items": [{
    "id": "comment_123",
    "snippet": {
      "textDisplay": "This is amazing!",
      "authorDisplayName": "User Name",
      "authorChannelId": {"value": "user_channel_id"},
      "publishedAt": "2024-01-15T11:00:00Z",
      "likeCount": 50,
      "replyCount": 2,
      "canReply": true,
      "authorChannelUrl": "https://...",
      "authorProfileImageUrl": "https://...",
      "updatedAt": "2024-01-15T11:00:00Z"
    }
  }]
}

# Check if comment author is subscriber (requires additional query)
# For now, assume non-verified means not subscriber
is_from_subscriber = 'authorChannelId' in response['items'][0]['snippet']

# Transform to:
comments = []
for item in comments_response['items']:
    comment = CommentMetadata(
        comment_id=item['id'],
        text=item['snippet']['textDisplay'],
        author_id=item['snippet'].get('authorChannelId', {}).get('value', 'unknown'),
        author_name=item['snippet']['authorDisplayName'],
        published_at=datetime.fromisoformat(
            item['snippet']['publishedAt'].replace('Z', '+00:00')
        ),
        like_count=item['snippet']['likeCount'],
        reply_count=item['snippet']['replyCount'],
        is_from_subscriber=is_from_subscriber,
    )
    comments.append(comment)
```

## Complete Backend Integration Example

```python
# youtube_service.py - Backend YouTube data fetcher

from google.auth.oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from dto.scoring_input import (
    MLScoringRequest, ChannelMetricsInput, AudienceMetricsInput,
    VideoMetricsInput, CommentMetadata
)

class YouTubeDataService:
    def __init__(self, credentials):
        self.youtube = build('youtube', 'v3', credentials=credentials)
        self.analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
    
    def fetch_creator_data_for_ml(self, creator_id: str) -> MLScoringRequest:
        """Fetch all data needed for ML scoring."""
        
        # Get channel info
        channel_data = self._fetch_channel(creator_id)
        channel = self._transform_channel(channel_data)
        
        # Get videos
        videos_data = self._fetch_videos(creator_id)
        videos = self._transform_videos(videos_data, creator_id)
        
        # Get audience analytics
        audience_data = self._fetch_analytics(creator_id)
        audience = self._transform_analytics(audience_data)
        
        # Get comment samples for sentiment
        for video_idx, video in enumerate(videos):
            comments_data = self._fetch_comments(video.video_id)
            videos[video_idx].comments_sample = self._transform_comments(comments_data)
        
        # Build request
        return MLScoringRequest(
            request_id=f"req_{creator_id}_{datetime.utcnow().timestamp()}",
            creator_id=creator_id,
            channel=channel,
            audience=audience,
            videos=videos,
        )
    
    def _fetch_channel(self, channel_id: str) -> dict:
        request = self.youtube.channels().list(
            part='snippet,statistics,status',
            id=channel_id
        )
        return request.execute()
    
    def _fetch_videos(self, channel_id: str, max_results: int = 20) -> dict:
        # First get list of videos
        request = self.youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            order='date',
            type='video',
            maxResults=max_results
        )
        search_response = request.execute()
        
        # Then get detailed stats for each
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        request = self.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=','.join(video_ids)
        )
        return request.execute()
    
    def _fetch_analytics(self, channel_id: str, days: int = 30) -> dict:
        end_date = datetime.utcnow().strftime('%Y-%m-%d')
        start_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Aggregate query
        request = self.analytics.reports().query(
            ids=f'channel=={channel_id}',
            start_date=start_date,
            end_date=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost,impressions,ctr',
        )
        return request.execute()
    
    def _fetch_comments(self, video_id: str, max_results: int = 100) -> dict:
        request = self.youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=max_results,
            textFormat='plainText'
        )
        return request.execute()
    
    # Transform methods...
    def _transform_channel(self, data: dict) -> ChannelMetricsInput:
        # See example above
        pass
    
    def _transform_videos(self, data: dict, channel_id: str) -> list[VideoMetricsInput]:
        # See example above
        pass
    
    def _transform_analytics(self, data: dict) -> AudienceMetricsInput:
        # See example above
        pass
    
    def _transform_comments(self, data: dict) -> list[CommentMetadata]:
        # See example above
        pass
```

## Post-Request to ML API

```python
# ml_client.py - Call ML API from backend

import httpx
from dto.scoring_input import MLScoringRequest

class MLAPIClient:
    def __init__(self, ml_api_url: str = "http://localhost:8001"):
        self.ml_api_url = ml_api_url
    
    async def score_creator(self, request: MLScoringRequest):
        """Send creator data to ML for scoring."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ml_api_url}/score/creator",
                json=_serialize_request(request)
            )
            return response.json()
    
    async def recommend(self, brand_profile, candidate_creators):
        """Get creator recommendations from ML."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.ml_api_url}/recommend/creators",
                json={
                    "request_id": "...",
                    "brand": _serialize(brand_profile),
                    "candidate_creators": [_serialize_request(c) for c in candidate_creators],
                    "num_recommendations": 5
                }
            )
            return response.json()

def _serialize_request(request: MLScoringRequest) -> dict:
    """Convert dataclass to JSON-serializable dict."""
    from dataclasses import asdict
    import json
    
    data = asdict(request)
    return json.loads(json.dumps(data, default=str))
```

## Caching Strategy

Recommended caching to avoid redundant ML calls:

```python
# Cache creator scores for 24 hours
CACHE_TTL = 86400  # seconds

@cache(ttl=CACHE_TTL)
async def get_creator_score(creator_id: str):
    # Fetch fresh YouTube data
    youtube_data = await youtube_service.fetch_creator_data_for_ml(creator_id)
    # Call ML
    ml_response = await ml_client.score_creator(youtube_data)
    return ml_response
```

---

**Note:** All Python objects here use Pydantic models defined in `dto/scoring_input.py` for automatic validation.
