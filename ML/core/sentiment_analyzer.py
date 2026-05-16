# """
# Sentiment Analysis Module using transformers (Hugging Face) for comment analysis.
# Analyzes comment text to extract sentiment, emotions, and overall quality.
# """
# from typing import List, Optional
# import statistics
# from datetime import datetime

# from dto.scoring_input import CommentMetadata
# from dto.scoring_output import SentimentAnalysisResult, CommentSentimentBreakdown


# class SentimentAnalyzer:
#     """
#     Analyzes sentiment of comments using transformer-based NLP.
#     Requires: pip install transformers torch
#     """
    
#     def __init__(self):
#         """Initialize sentiment and emotion models."""
#         try:
#             from transformers import pipeline
#             # Zero-shot classification for flexible sentiment
#             self.sentiment_pipeline = pipeline(
#                 "sentiment-analysis",
#                 model="distilbert-base-uncased-finetuned-sst-2-english"
#             )
#             # Emotion detection
#             self.emotion_pipeline = pipeline(
#                 "text-classification",
#                 model="j-hartmann/emotion-english-distilroberta-base"
#             )
#             self.available = True
#         except ImportError:
#             print("Warning: transformers not installed. Sentiment analysis disabled.")
#             print("Install with: pip install transformers torch")
#             self.available = False
    
#     def analyze_comment(self, comment: CommentMetadata) -> SentimentAnalysisResult:
#         """
#         Analyze sentiment and emotion for a single comment.
        
#         Returns:
#             SentimentAnalysisResult with sentiment_label, score, and emotions
#         """
#         if not self.available:
#             return self._default_result(comment)
        
#         try:
#             # Sentiment analysis
#             sentiment_output = self.sentiment_pipeline(comment.text[:512])[0]  # Truncate for efficiency
#             sentiment_label = sentiment_output['label'].lower()  # POSITIVE or NEGATIVE
#             sentiment_score = sentiment_output['score']
            
#             # Convert to -1 to 1 scale
#             if sentiment_label == "negative":
#                 sentiment_score = -sentiment_score
            
#             # Emotion detection
#             emotion_output = self.emotion_pipeline(comment.text[:512])[0]
#             emotion_label = emotion_output['label'].lower()
            
#             # Emotion score (confidence)
#             emotion_score = emotion_output['score']
            
#             # Map to overall sentiment
#             sentiment_map = {
#                 "positive": "positive",
#                 "negative": "negative",
#                 "neutral": "neutral",
#             }
#             overall_sentiment = sentiment_map.get(sentiment_label, "neutral")
            
#             # Emotion tags based on emotion detection
#             emotion_tags = self._get_emotion_tags(emotion_label, comment.text)
            
#             return SentimentAnalysisResult(
#                 text_sample=comment.text[:100] + "..." if len(comment.text) > 100 else comment.text,
#                 sentiment_label=overall_sentiment,
#                 sentiment_score=sentiment_score,
#                 confidence=max(sentiment_output['score'], emotion_score),
#                 emotion_tags=emotion_tags,
#             )
#         except Exception as e:
#             print(f"Error analyzing comment: {e}")
#             return self._default_result(comment)
    
#     def analyze_comments(self, comments: List[CommentMetadata]) -> CommentSentimentBreakdown:
#         """
#         Analyze sentiment for a batch of comments.
        
#         Returns:
#             CommentSentimentBreakdown with aggregated statistics
#         """
#         if not comments:
#             return CommentSentimentBreakdown(
#                 total_comments_analyzed=0,
#                 positive_pct=0.0,
#                 negative_pct=0.0,
#                 neutral_pct=0.0,
#                 average_sentiment_score=0.0,
#             )
        
#         results = [self.analyze_comment(c) for c in comments]
        
#         # Aggregate stats
#         positive_count = sum(1 for r in results if r.sentiment_label == "positive")
#         negative_count = sum(1 for r in results if r.sentiment_label == "negative")
#         neutral_count = len(results) - positive_count - negative_count
        
#         sentiment_scores = [r.sentiment_score for r in results]
#         avg_score = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
        
#         # Collect emotion tags
#         all_emotions = []
#         for r in results:
#             all_emotions.extend(r.emotion_tags)
        
#         # Most common emotions
#         top_emotions = self._get_most_common(all_emotions, top_n=5)
        
#         # Sentiment trend (simple: if avg score improving positive, "improving")
#         # In real implementation, would compare over time windows
#         if avg_score > 0.5:
#             sentiment_trend = "improving"
#         elif avg_score < -0.3:
#             sentiment_trend = "declining"
#         else:
#             sentiment_trend = "stable"
        
#         # Sample results
#         positive_results = [r for r in results if r.sentiment_label == "positive"][:3]
#         negative_results = [r for r in results if r.sentiment_label == "negative"][:3]
        
#         return CommentSentimentBreakdown(
#             total_comments_analyzed=len(results),
#             positive_pct=(positive_count / len(results) * 100) if results else 0.0,
#             negative_pct=(negative_count / len(results) * 100) if results else 0.0,
#             neutral_pct=(neutral_count / len(results) * 100) if results else 0.0,
#             average_sentiment_score=avg_score,
#             top_emotions=top_emotions,
#             sentiment_trend=sentiment_trend,
#             sample_positive=positive_results,
#             sample_negative=negative_results,
#         )
    
#     @staticmethod
#     def _get_emotion_tags(emotion_label: str, text: str) -> List[str]:
#         """
#         Map emotion label and text to human-readable emotion tags.
#         """
#         emotion_keys = {
#             "joy": ["love", "support", "excited", "enthusiastic"],
#             "anger": ["angry", "upset", "criticism"],
#             "sadness": ["sad", "disappointed", "concerned"],
#             "neutral": ["informative", "factual"],
#             "disgust": ["dislike", "disapprove"],
#             "surprise": ["shocked", "unexpected"],
#             "fear": ["worried", "concerned"],
#         }
        
#         # Check for explicit keywords in text
#         text_lower = text.lower()
#         found_tags = []
        
#         for emotion, tags in emotion_keys.items():
#             if emotion == emotion_label:
#                 found_tags.extend(tags)
        
#         # Add keyword-based tags
#         if any(word in text_lower for word in ["love", "amazing", "awesome"]):
#             found_tags.append("love")
#         if any(word in text_lower for word in ["hate", "terrible", "awful"]):
#             found_tags.append("anger")
#         if any(word in text_lower for word in ["thanks", "appreciate", "grateful"]):
#             found_tags.append("support")
        
#         return list(set(found_tags))[:5]  # Unique, max 5
    
#     @staticmethod
#     def _get_most_common(items: List[str], top_n: int = 5) -> List[str]:
#         """Get most common items from a list."""
#         if not items:
#             return []
#         from collections import Counter
#         counted = Counter(items)
#         return [item for item, _ in counted.most_common(top_n)]
    
#     @staticmethod
#     def _default_result(comment: CommentMetadata) -> SentimentAnalysisResult:
#         """Fallback result when transformer not available."""
#         # Simple heuristic-based sentiment
#         text_lower = comment.text.lower()
        
#         positive_words = {"love", "great", "amazing", "awesome", "excellent", "thanks", "appreciate"}
#         negative_words = {"hate", "terrible", "awful", "bad", "worse", "worse", "dislike"}
        
#         positive_count = sum(1 for word in positive_words if word in text_lower)
#         negative_count = sum(1 for word in negative_words if word in text_lower)
        
#         if positive_count > negative_count:
#             sentiment = "positive"
#             score = 0.5
#         elif negative_count > positive_count:
#             sentiment = "negative"
#             score = -0.5
#         else:
#             sentiment = "neutral"
#             score = 0.0
        
#         return SentimentAnalysisResult(
#             text_sample=comment.text[:100],
#             sentiment_label=sentiment,
#             sentiment_score=score,
#             confidence=0.6,
#             emotion_tags=[],
#         )



"""
Sentiment Analysis Module using transformers (Hugging Face) for comment analysis.
OPTIMIZED for minimal API usage - lightweight models and efficient processing.
Added support for Nigerian Pidgin English and African English variants.
"""
from typing import List, Optional, Dict
import statistics
import re
from datetime import datetime

from dto.scoring_input import CommentMetadata
from dto.scoring_output import SentimentAnalysisResult, CommentSentimentBreakdown


class SentimentAnalyzer:
    """
    Analyzes sentiment of comments using transformer-based NLP.
    Optimized for low-resource environments and African English/Pidgin variants.
    
    Resource usage per comment:
    - Max 512 tokens
    - ~10-20MB RAM per batch
    - ~0.1-0.3 seconds per comment on CPU
    """
    
    # Lightweight model options (choose based on deployment)
    MODEL_OPTIONS = {
        "tiny": "cardiffnlp/twitter-roberta-base-sentiment-latest",  # 498MB
        "light": "distilbert-base-uncased-finetuned-sst-2-english",  # 268MB
        "pidgin": "Davlan/bert-base-multilingual-cased-finetuned-nigerian-sentiment",  # Experimental
    }
    
    # African/Nigerian slang and sentiment markers
    PIDGIN_SENTIMENT_MAP = {
        # Positive Pidgin
        "naija": 0.7, "wahala": -0.3, "sabi": 0.6, "chop": 0.4, "bless": 0.8,
        "big ups": 0.9, "mad o": 0.6, "shebi": 0.3, "abeg": 0.2,
        "no wahala": 0.5, "oga": 0.4, "maestro": 0.7, "killin": 0.6,
        # Negative Pidgin  
        "yawa": -0.8, "gbese": -0.6, "wayo": -0.5, "shakara": -0.3,
        "baff up": -0.4, "suffering": -0.7, "sapa": -0.9,
        # Neutral/Contextual
        "abi": 0.0, "na": 0.0, "ooh": 0.0, "ehn": 0.0,
    }
    
    # Common Nigerian expressions
    NIGERIAN_POSITIVE = {
        "god bless", "more grace", "keep winning", "proud of you",
        "you try", "well done", "keep it up", "inspiring", "motivating",
        "go higher", "making us proud", "representing", "hitting different"
    }
    
    NIGERIAN_NEGATIVE = {
        "not it", "big flop", "waste of time", "trash", "rubbish",
        "falling hand", "disappoint", "not giving"
    }
    
    def __init__(self, model_size: str = "light"):
        """
        Initialize sentiment models.
        
        Args:
            model_size: "tiny", "light", or "pidgin"
        """
        self.model_size = model_size
        self.available = False
        self.sentiment_pipeline = None
        
        try:
            from transformers import pipeline
            
            # Select model based on preference
            model_name = self.MODEL_OPTIONS.get(model_size, self.MODEL_OPTIONS["light"])
            
            # Use lightweight pipeline with reduced memory
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=-1,  # CPU only (use 0 for GPU if available)
                truncation=True,
                max_length=128,  # Reduced from 512 for speed
            )
            self.available = True
            print(f"Sentiment analyzer initialized with model: {model_name}")
            
        except ImportError:
            print("Warning: transformers not installed. Sentiment analysis disabled.")
            print("Install with: pip install transformers torch --no-cache-dir")
        except Exception as e:
            print(f"Warning: Could not load sentiment model: {e}")
            print("Falling back to rule-based sentiment analysis")
    
    def analyze_comment(self, comment: CommentMetadata) -> SentimentAnalysisResult:
        """
        Analyze sentiment and emotion for a single comment.
        Optimized for Nigerian/Pidgin English.
        
        Returns:
            SentimentAnalysisResult with sentiment_label, score, and emotions
        """
        # Preprocess text for Nigerian context
        processed_text = self._preprocess_pidgin(comment.text)
        
        if not self.available:
            return self._rule_based_analysis(comment, processed_text)
        
        try:
            # Sentiment analysis with truncation for efficiency
            truncated = processed_text[:256]  # Half the original length
            sentiment_output = self.sentiment_pipeline(truncated)[0]
            
            sentiment_label = sentiment_output['label'].lower()
            sentiment_score = sentiment_output['score']
            
            # Adjust score for neutral or ambiguous results
            sentiment_score = self._adjust_sentiment_score(
                sentiment_score, 
                sentiment_label, 
                processed_text
            )
            
            # Convert to -1 to 1 scale
            if sentiment_label in ["negative", "NEGATIVE"]:
                sentiment_score = -sentiment_score
            elif sentiment_label in ["neutral", "NEUTRAL"]:
                sentiment_score = sentiment_score * 0.5  # Neutral is closer to 0
            
            # Emotion detection (simplified - skip heavy emotion model)
            emotion_tags = self._extract_emotion_tags(processed_text)
            
            overall_sentiment = self._map_sentiment_label(sentiment_label, sentiment_score)
            
            return SentimentAnalysisResult(
                comment_id=comment.comment_id,
                text_sample=comment.text[:100] + "..." if len(comment.text) > 100 else comment.text,
                sentiment_label=overall_sentiment,
                sentiment_score=sentiment_score,
                confidence=min(sentiment_output['score'] + 0.2, 1.0),  # Boost confidence slightly
                emotion_tags=emotion_tags,
            )
            
        except Exception as e:
            print(f"Error analyzing comment (ID: {comment.comment_id}): {e}")
            return self._rule_based_analysis(comment, processed_text)
    
    def analyze_comments(self, comments: List[CommentMetadata]) -> CommentSentimentBreakdown:
        """
        Analyze sentiment for a batch of comments with efficient batching.
        
        Returns:
            CommentSentimentBreakdown with aggregated statistics
        """
        if not comments:
            return self._empty_breakdown()
        
        # Process in smaller batches to manage memory
        batch_size = 10  # Small batch for low-resource environments
        all_results = []
        
        for i in range(0, len(comments), batch_size):
            batch = comments[i:i+batch_size]
            batch_results = [self.analyze_comment(c) for c in batch]
            all_results.extend(batch_results)
        
        # Aggregate stats
        positive_count = sum(1 for r in all_results if r.sentiment_label == "positive")
        negative_count = sum(1 for r in all_results if r.sentiment_label == "negative")
        neutral_count = len(all_results) - positive_count - negative_count
        
        sentiment_scores = [r.sentiment_score for r in all_results]
        avg_score = statistics.mean(sentiment_scores) if sentiment_scores else 0.0
        confidence_scores = [r.confidence for r in all_results]
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.0
        
        # Aggregate emotion tags
        all_emotions = []
        for r in all_results:
            all_emotions.extend(r.emotion_tags)
        
        top_emotions = self._get_most_common(all_emotions, top_n=5)
        
        # Sentiment trend (simplified for batch)
        sentiment_trend = self._calculate_trend(all_results)
        
        # Quality score (0-100) - how positive and engaged the audience is
        quality_score = self._calculate_sentiment_quality_score(
            positive_count, negative_count, avg_score, len(all_results)
        )
        
        # Sample results
        positive_results = [r for r in all_results if r.sentiment_label == "positive"][:3]
        negative_results = [r for r in all_results if r.sentiment_label == "negative"][:3]
        
        return CommentSentimentBreakdown(
            total_comments_analyzed=len(all_results),
            positive_pct=(positive_count / len(all_results) * 100) if all_results else 0.0,
            negative_pct=(negative_count / len(all_results) * 100) if all_results else 0.0,
            neutral_pct=(neutral_count / len(all_results) * 100) if all_results else 0.0,
            average_sentiment_score=avg_score,
            average_confidence=avg_confidence,
            top_emotions=top_emotions,
            sentiment_trend=sentiment_trend,
            sentiment_quality_score=quality_score,
            sample_positive=positive_results,
            sample_negative=negative_results,
        )
    
    def _preprocess_pidgin(self, text: str) -> str:
        """
        Preprocess Nigerian Pidgin English text for better sentiment analysis.
        """
        if not text:
            return ""
        
        text = text.lower()
        
        # Normalize common Pidgin variations
        replacements = {
            r'\bwahala\b': "problem",
            r'\babeg\b': "please",
            r'\bnaija\b': "nigeria",
            r'\bsabi\b': "know",
            r'\boooo\b': "oh",
            r'\booh\b': "oh",
            r'\bchop\b': "eat",
            r'\bshebi\b': "right",
            r'\byawa\b': "trouble",
            r'\bgbese\b': "debt",
            r'\bwayo\b': "scam",
            r'\bsapa\b': "poverty",
            r'\boga\b': "boss",
            r'\bmad o\b': "crazy",
            r'\bkillin\b': "killing",
            r'\bbaff up\b': "dress up",
        }
        
        for pidgin, english in replacements.items():
            text = re.sub(pidgin, english, text)
        
        # Remove excessive exclamation marks and emojis (simplify)
        text = re.sub(r'!+', '!', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return text[:256]  # Limit length
    
    def _adjust_sentiment_score(self, score: float, label: str, text: str) -> float:
        """
        Adjust sentiment score based on Nigerian context and Pidgin markers.
        """
        text_lower = text.lower()
        
        # Check for Pidgin sentiment markers
        pidgin_score = 0.0
        for phrase, sentiment in self.PIDGIN_SENTIMENT_MAP.items():
            if phrase in text_lower:
                pidgin_score += sentiment
        
        # Average pidgin adjustment
        if pidgin_score != 0:
            pidgin_score = pidgin_score / max(1, len([p for p in self.PIDGIN_SENTIMENT_MAP if p in text_lower]))
        
        # Check Nigerian positive/negative phrases
        for phrase in self.NIGERIAN_POSITIVE:
            if phrase in text_lower:
                pidgin_score += 0.4
                break
        
        for phrase in self.NIGERIAN_NEGATIVE:
            if phrase in text_lower:
                pidgin_score -= 0.5
                break
        
        # Blend with model score
        adjusted = score + (pidgin_score * 0.3)
        
        # Clamp to [0, 1] range
        return max(0.0, min(1.0, adjusted))
    
    def _extract_emotion_tags(self, text: str) -> List[str]:
        """
        Extract emotion tags using keyword matching (lightweight alternative to emotion model).
        """
        text_lower = text.lower()
        tags = []
        
        emotion_keywords = {
            "excitement": ["excited", "amazing", "awesome", "wow", "incredible", "love it"],
            "support": ["support", "appreciate", "thanks", "grateful", "proud", "keep going"],
            "criticism": ["bad", "terrible", "awful", "dislike", "hate", "trash", "rubbish"],
            "humor": ["funny", "lol", "haha", "hilarious", "comedy", "😂", "🤣"],
            "frustration": ["frustrated", "annoying", "waste", "disappointed", "tired"],
            "excitement_ng": ["killin", "mad o", "banger", "hit", "🔥", "💯"],
            "support_ng": ["big ups", "more grace", "god bless", "you try"],
            "criticism_ng": ["falling hand", "flop", "not it", "yawa", "no way"],
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(emotion)
        
        return tags[:3]  # Max 3 emotions per comment
    
    def _map_sentiment_label(self, model_label: str, score: float) -> str:
        """
        Map model output to sentiment label with adjustment for low scores.
        """
        if abs(score) < 0.15:
            return "neutral"
        
        if model_label in ["positive", "POSITIVE"]:
            return "positive"
        elif model_label in ["negative", "NEGATIVE"]:
            return "negative"
        else:
            return "neutral"
    
    def _rule_based_analysis(
        self, 
        comment: CommentMetadata, 
        processed_text: str
    ) -> SentimentAnalysisResult:
        """
        Fallback rule-based sentiment analysis for when ML model unavailable.
        """
        text_lower = processed_text.lower()
        
        # Positive markers (Nigerian inclusive)
        positive_markers = {
            "love", "great", "amazing", "awesome", "excellent", "thanks", 
            "appreciate", "good", "nice", "wonderful", "perfect", "best",
            "proud", "inspiring", "motivating", "god bless", "more grace",
            "killin", "you try", "well done", "big ups", "🔥", "💯"
        }
        
        # Negative markers
        negative_markers = {
            "hate", "terrible", "awful", "bad", "worse", "dislike", "trash",
            "rubbish", "waste", "disappoint", "falling hand", "flop", "yawa",
            "not it", "no way"
        }
        
        # Count markers
        positive_count = sum(1 for word in positive_markers if word in text_lower)
        negative_count = sum(1 for word in negative_markers if word in text_lower)
        
        # Calculate score
        total_markers = positive_count + negative_count
        if total_markers == 0:
            sentiment = "neutral"
            score = 0.0
            confidence = 0.5
        else:
            raw_score = (positive_count - negative_count) / total_markers
            score = max(-1.0, min(1.0, raw_score))
            confidence = min(0.8, 0.5 + (total_markers * 0.05))
            
            if score > 0.3:
                sentiment = "positive"
            elif score < -0.3:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        emotion_tags = self._extract_emotion_tags(processed_text)
        
        return SentimentAnalysisResult(
            comment_id=comment.comment_id,
            text_sample=comment.text[:100],
            sentiment_label=sentiment,
            sentiment_score=score,
            confidence=confidence,
            emotion_tags=emotion_tags,
        )
    
    def _calculate_trend(self, results: List[SentimentAnalysisResult]) -> str:
        """
        Calculate sentiment trend from batch of results.
        """
        if len(results) < 3:
            return "stable"
        
        # Simple trend: compare first half to second half
        midpoint = len(results) // 2
        first_half = statistics.mean([r.sentiment_score for r in results[:midpoint]])
        second_half = statistics.mean([r.sentiment_score for r in results[midpoint:]])
        
        difference = second_half - first_half
        
        if difference > 0.15:
            return "improving"
        elif difference < -0.15:
            return "declining"
        else:
            return "stable"
    
    def _calculate_sentiment_quality_score(
        self, 
        positive_count: int, 
        negative_count: int, 
        avg_score: float,
        total: int
    ) -> float:
        """
        Calculate sentiment quality score (0-100).
        Higher score = more positive, engaged audience.
        """
        if total == 0:
            return 50.0
        
        pos_neg_ratio = positive_count / max(negative_count, 1)
        pos_neg_score = min(100, (pos_neg_ratio / 10) * 100) if pos_neg_ratio > 1 else (pos_neg_ratio * 50)
        
        # Normalize avg_score from -1..1 to 0..100
        score_normalized = (avg_score + 1) / 2 * 100
        
        # Weighted composite
        quality = (pos_neg_score * 0.6) + (score_normalized * 0.4)
        
        return min(quality, 100.0)
    
    def _empty_breakdown(self) -> CommentSentimentBreakdown:
        """Return empty breakdown for no comments."""
        return CommentSentimentBreakdown(
            total_comments_analyzed=0,
            positive_pct=0.0,
            negative_pct=0.0,
            neutral_pct=0.0,
            average_sentiment_score=0.0,
            average_confidence=0.0,
            top_emotions=[],
            sentiment_trend="stable",
            sentiment_quality_score=50.0,
            sample_positive=[],
            sample_negative=[],
        )
    
    @staticmethod
    def _get_most_common(items: List[str], top_n: int = 5) -> List[str]:
        """Get most common items from a list efficiently."""
        if not items:
            return []
        from collections import Counter
        counted = Counter(items)
        return [item for item, _ in counted.most_common(top_n)]