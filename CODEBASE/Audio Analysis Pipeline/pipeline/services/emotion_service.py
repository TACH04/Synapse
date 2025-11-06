"""
Emotion Service
TRIPLE ENSEMBLE APPROACH: Combines three models for maximum accuracy:
1. HuBERT (audio - prosody expert)
2. Wav2Vec2 (audio - phonetic expert)
3. DistilRoBERTa (text - semantic expert)

Supports flexible modes: 'dual_audio' or 'triple_ensemble'
"""

import warnings
warnings.filterwarnings('ignore')

import torch
import numpy as np
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification, pipeline
from typing import Dict, Optional, Any, Literal


class EmotionService:
    """
    Triple Ensemble Speech Emotion Recognition service.

    Uses THREE models for comprehensive emotion analysis:
    1. HuBERT: Audio-based (prosody - tone, pitch, rhythm)
    2. Wav2Vec2: Audio-based (phonetic - articulation under emotion)
    3. DistilRoBERTa: Text-based (semantic - word meaning, sentiment)

    Supports two modes:
    - 'dual_audio': HuBERT + Wav2Vec2 (faster, focuses on vocal tone)
    - 'triple_ensemble': All three models (most accurate, includes text)

    This service answers: "How was it said? (from multiple perspectives)"
    """

    def __init__(self,
                 mode: Literal['dual_audio', 'triple_ensemble'] = 'triple_ensemble',
                 hubert_model: str = "superb/hubert-base-superb-er",
                 wav2vec2_model: str = "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
                 text_model: str = "j-hartmann/emotion-english-distilroberta-base",
                 sample_rate: int = 16000):
        """
        Initializes the triple ensemble emotion service.

        Args:
            mode: 'dual_audio' (HuBERT + Wav2Vec2) or 'triple_ensemble' (all three)
            hubert_model: HuBERT model for prosody analysis (4 emotions)
            wav2vec2_model: Wav2Vec2 model for phonetic analysis (8 emotions)
            text_model: Text model for semantic analysis (7 emotions)
            sample_rate: Audio sample rate (16000 Hz)
        """
        self.mode = mode
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sample_rate = sample_rate

        # Show GPU info
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"EmotionService: Using GPU - {gpu_name}")
        else:
            print(f"EmotionService: Using CPU (GPU not available)")

        try:
            # Load MODEL 1: HuBERT (prosody-focused, 4 emotions)
            print(f"Loading HuBERT model (prosody analysis)...")
            self.hubert_extractor = AutoFeatureExtractor.from_pretrained(hubert_model)
            self.hubert_model = AutoModelForAudioClassification.from_pretrained(hubert_model).to(self.device)
            self.hubert_id2label = self.hubert_model.config.id2label

            # Load MODEL 2: Wav2Vec2 (phonetic-focused, 8 emotions)
            print(f"Loading Wav2Vec2 model (phonetic analysis)...")
            self.wav2vec2_extractor = AutoFeatureExtractor.from_pretrained(wav2vec2_model)
            self.wav2vec2_model = AutoModelForAudioClassification.from_pretrained(wav2vec2_model).to(self.device)
            self.wav2vec2_id2label = self.wav2vec2_model.config.id2label

            # Load MODEL 3: Text model (semantic-focused, 7 emotions) - only if triple mode
            if mode == 'triple_ensemble':
                print(f"Loading Text model (semantic analysis)...")
                self.text_classifier = pipeline(
                    "text-classification",
                    model=text_model,
                    device=0 if self.device == "cuda" else -1,
                    top_k=None  # Get scores for all emotions
                )
            else:
                self.text_classifier = None

            print(f"\nEmotionService loaded in {mode.upper()} mode on {self.device}.")
            print(f"  Model 1 (HuBERT): {hubert_model}")
            print(f"  - Labels: {list(self.hubert_id2label.values())}")
            print(f"  Model 2 (Wav2Vec2): {wav2vec2_model}")
            print(f"  - Labels: {list(self.wav2vec2_id2label.values())}")
            if mode == 'triple_ensemble':
                print(f"  Model 3 (Text): {text_model}")
                print(f"  - Labels: ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']")

        except Exception as e:
            print(f"Error loading emotion models: {e}")
            raise

    def process(self, audio_slice: np.ndarray, transcript: str = "", acoustic_features: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Predicts emotion using TRIPLE ENSEMBLE (or dual-audio mode) with quality filtering.

        Args:
            audio_slice (np.ndarray): The 1D audio array (at 16kHz)
            transcript (str): The text transcript of the audio
            acoustic_features (Optional[Dict]): Pre-computed acoustic features (pitch, jitter, etc.)

        Returns:
            Optional[Dict[str, Any]]: A dict with:
                - label (str): Final predicted emotion label
                - score (float): Final confidence score (0-1)
                - confidence (str): 'very_high', 'high', 'medium', or 'low'
                - hubert_emotion (str): Emotion from HuBERT
                - hubert_score (float): HuBERT confidence
                - wav2vec2_emotion (str): Emotion from Wav2Vec2
                - wav2vec2_score (float): Wav2Vec2 confidence
                - text_emotion (str): Emotion from text (if triple mode)
                - text_score (float): Text confidence (if triple mode)
                - agreement (str): 'full', 'audio_consensus', 'partial', or 'none'
                - sarcasm_flag (bool): True if text disagrees with audio (triple mode)
                - mixed_emotion_flag (bool): True if models disagree significantly
                - method (str): 'dual_audio' or 'triple_ensemble'
            Returns None if analysis fails.
        """
        # Quality check: Segment too short or empty
        duration = len(audio_slice) / self.sample_rate
        if audio_slice.size == 0 or duration < 0.3:  # Minimum 0.3 seconds
            return None

        # Quality check: Very quiet (likely silence)
        if np.max(np.abs(audio_slice)) < 0.01:
            return None

        result = {}

        # 1. HuBERT analysis (prosody)
        try:
            hubert_emotion = self._analyze_hubert(audio_slice)
            if hubert_emotion:
                result['hubert_emotion'] = hubert_emotion['label']
                result['hubert_score'] = hubert_emotion['score']
        except Exception as e:
            print(f"⚠ HuBERT analysis failed: {e}")
            result['hubert_emotion'] = None
            result['hubert_score'] = 0.0

        # 2. Wav2Vec2 analysis (phonetic)
        try:
            wav2vec2_emotion = self._analyze_wav2vec2(audio_slice)
            if wav2vec2_emotion:
                result['wav2vec2_emotion'] = wav2vec2_emotion['label']
                result['wav2vec2_score'] = wav2vec2_emotion['score']
        except Exception as e:
            print(f"⚠ Wav2Vec2 analysis failed: {e}")
            result['wav2vec2_emotion'] = None
            result['wav2vec2_score'] = 0.0

        # 3. Text analysis (semantic) - only if triple mode and transcript available
        if self.mode == 'triple_ensemble' and transcript and transcript.strip():
            try:
                text_emotion = self._analyze_text(transcript)
                if text_emotion:
                    result['text_emotion'] = text_emotion['label']
                    result['text_score'] = text_emotion['score']
            except Exception as e:
                print(f"⚠ Text analysis failed: {e}")
                result['text_emotion'] = None
                result['text_score'] = 0.0
        else:
            result['text_emotion'] = None
            result['text_score'] = 0.0

        # 4. COMBINE all predictions with acoustic features
        final = self._combine_predictions(result, acoustic_features)

        return final if final else None

    def _analyze_hubert(self, audio_slice: np.ndarray) -> Optional[Dict[str, Any]]:
        """Analyze emotion using HuBERT (prosody: tone, pitch, rhythm)."""
        try:
            inputs = self.hubert_extractor(
                audio_slice,
                sampling_rate=self.sample_rate,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.hubert_model(**inputs).logits

            scores = torch.nn.functional.softmax(logits, dim=1)
            best_score, best_index = torch.max(scores, dim=1)

            return {
                "label": self.hubert_id2label[best_index.item()],
                "score": round(best_score.item(), 4)
            }
        except Exception as e:
            return None

    def _analyze_wav2vec2(self, audio_slice: np.ndarray) -> Optional[Dict[str, Any]]:
        """Analyze emotion using Wav2Vec2 (phonetic: articulation under emotion)."""
        try:
            inputs = self.wav2vec2_extractor(
                audio_slice,
                sampling_rate=self.sample_rate,
                return_tensors="pt",
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.wav2vec2_model(**inputs).logits

            scores = torch.nn.functional.softmax(logits, dim=1)
            best_score, best_index = torch.max(scores, dim=1)

            return {
                "label": self.wav2vec2_id2label[best_index.item()],
                "score": round(best_score.item(), 4)
            }
        except Exception as e:
            return None

    def _analyze_text(self, transcript: str) -> Optional[Dict[str, Any]]:
        """Analyze emotion from transcript text (emotional content)."""
        if not self.text_classifier:
            return None

        try:
            # Get predictions for all emotion classes
            predictions = self.text_classifier(transcript[:512])  # Limit text length

            if predictions and len(predictions) > 0:
                # predictions is a list of lists: [[{label, score}, {label, score}, ...]]
                top_prediction = max(predictions[0], key=lambda x: x['score'])

                return {
                    "label": top_prediction['label'],
                    "score": round(top_prediction['score'], 4)
                }
        except Exception as e:
            return None

    def _combine_predictions(self, result: Dict, acoustic_features: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Combine HuBERT, Wav2Vec2, and optionally Text predictions intelligently.

        **IMPROVEMENTS IMPLEMENTED:**
        1. ✅ Dynamic adaptive weighting based on confidence
        2. ✅ Acoustic feature integration for validation
        3. ✅ Veto power for high-confidence predictions
        4. ✅ Refined disagreement handling
        5. ✅ Confidence calibration
        6. ✅ Context-aware emotion mapping

        Strategy for TRIPLE ENSEMBLE:
        1. Veto: If any model >0.90 confidence → Give it priority
        2. All three agree → Very high confidence
        3. Both audio agree, text disagrees → Check acoustic features + text confidence
        4. Mixed predictions → Dynamic weighted vote

        Strategy for DUAL AUDIO:
        1. Both agree → High confidence
        2. Disagree → Use higher confidence prediction
        """
        has_hubert = result.get('hubert_emotion') is not None
        has_wav2vec2 = result.get('wav2vec2_emotion') is not None
        has_text = result.get('text_emotion') is not None and self.mode == 'triple_ensemble'

        if not has_hubert and not has_wav2vec2:
            return None

        # Get raw scores
        hubert_score = result.get('hubert_score', 0)
        wav2vec2_score = result.get('wav2vec2_score', 0)
        text_score = result.get('text_score', 0)

        # Map all to common label space (HuBERT's 4 categories)
        hubert_label = result.get('hubert_emotion', 'neu')
        wav2vec2_label = result.get('wav2vec2_emotion', 'neutral')
        text_label = result.get('text_emotion', 'neutral')

        # Map Wav2Vec2 and text labels to HuBERT space
        mapped_wav2vec2 = self._map_to_hubert(wav2vec2_label, acoustic_features)
        mapped_text = self._map_to_hubert(text_label, acoustic_features) if has_text else None

        # ============================================================
        # IMPROVEMENT #1: DYNAMIC ADAPTIVE WEIGHTING
        # ============================================================
        weights = self._calculate_dynamic_weights(
            hubert_score, wav2vec2_score, text_score,
            has_text, acoustic_features
        )

        # ============================================================
        # IMPROVEMENT #2: VETO POWER FOR HIGH-CONFIDENCE PREDICTIONS
        # ============================================================
        veto_result = self._check_veto_conditions(
            hubert_label, hubert_score,
            mapped_wav2vec2, wav2vec2_score,
            mapped_text, text_score,
            has_text, result, weights
        )
        if veto_result:
            return veto_result

        # Count agreements
        predictions = [p for p in [hubert_label, mapped_wav2vec2, mapped_text] if p is not None]
        unique_predictions = set(predictions)

        # CASE 1: All three agree (or both audio agree in dual mode)
        audio_agree = (hubert_label == mapped_wav2vec2)
        all_agree = (len(unique_predictions) == 1) if has_text else audio_agree

        if all_agree:
            combined_score = (
                hubert_score * weights['hubert'] +
                wav2vec2_score * weights['wav2vec2'] +
                text_score * weights['text']
            )

            # IMPROVEMENT #3: CONFIDENCE CALIBRATION
            # Boost if strong agreement + high individual scores
            if hubert_score > 0.7 and wav2vec2_score > 0.5:
                combined_score *= 1.25  # 25% boost
            elif hubert_score > 0.6:
                combined_score *= 1.15  # 15% boost

            # IMPROVEMENT #4: ACOUSTIC FEATURE VALIDATION
            if acoustic_features:
                combined_score = self._validate_with_acoustics(
                    hubert_label, combined_score, acoustic_features
                )

            return {
                'label': hubert_label,
                'score': min(round(combined_score, 4), 1.0),
                'confidence': self._calibrate_confidence(combined_score, hubert_label),
                'hubert_emotion': result.get('hubert_emotion'),
                'hubert_score': hubert_score,
                'wav2vec2_emotion': result.get('wav2vec2_emotion'),
                'wav2vec2_score': wav2vec2_score,
                'text_emotion': result.get('text_emotion'),
                'text_score': text_score,
                'agreement': 'full',
                'sarcasm_flag': False,
                'mixed_emotion_flag': False,
                'method': self.mode
            }

        # CASE 2: Both audio agree, text disagrees
        if has_text and audio_agree and mapped_text != hubert_label:
            # IMPROVEMENT #5: REFINED TEXT-AUDIO DISAGREEMENT LOGIC
            return self._handle_text_audio_disagreement(
                hubert_label, mapped_text,
                hubert_score, wav2vec2_score, text_score,
                result, weights, acoustic_features
            )

        # CASE 3: No clear agreement (mixed emotions or disagreement)
        return self._handle_mixed_predictions(
            hubert_label, mapped_wav2vec2, mapped_text,
            hubert_score, wav2vec2_score, text_score,
            result, weights, acoustic_features
        )

    def _calculate_dynamic_weights(self, hubert_score: float, wav2vec2_score: float,
                                   text_score: float, has_text: bool,
                                   acoustic_features: Optional[Dict]) -> Dict[str, float]:
        """
        Calculate dynamic weights based on model confidence levels.

        IMPROVEMENT #1: Dynamic Adaptive Weighting
        """
        if not has_text:
            # Dual audio mode: Favor the more confident model
            if hubert_score > 0.7 and wav2vec2_score < 0.3:
                return {'hubert': 0.70, 'wav2vec2': 0.30, 'text': 0.0}
            elif wav2vec2_score > 0.6 and hubert_score < 0.4:
                return {'hubert': 0.35, 'wav2vec2': 0.65, 'text': 0.0}
            else:
                return {'hubert': 0.55, 'wav2vec2': 0.45, 'text': 0.0}

        # Triple ensemble mode
        # If text has very high confidence (>0.85), give it more weight
        if text_score > 0.85:
            return {'hubert': 0.30, 'wav2vec2': 0.20, 'text': 0.50}

        # If both audio models are confident, reduce text weight
        if hubert_score > 0.7 and wav2vec2_score > 0.5:
            return {'hubert': 0.45, 'wav2vec2': 0.40, 'text': 0.15}

        # If audio models are weak but text is strong
        if hubert_score < 0.5 and wav2vec2_score < 0.5 and text_score > 0.7:
            return {'hubert': 0.25, 'wav2vec2': 0.20, 'text': 0.55}

        # Default balanced weights
        return {'hubert': 0.40, 'wav2vec2': 0.35, 'text': 0.25}

    def _check_veto_conditions(self, hubert_label: str, hubert_score: float,
                               wav2vec2_label: str, wav2vec2_score: float,
                               text_label: Optional[str], text_score: float,
                               has_text: bool, result: Dict, weights: Dict) -> Optional[Dict]:
        """
        Check if any model has veto power (>0.90 confidence on non-neutral emotion).

        IMPROVEMENT #2: Veto Power for High-Confidence Predictions
        """
        # Text veto (strongest, since it's most reliable for strong emotions)
        if has_text and text_score > 0.90 and text_label not in ['neu', 'neutral']:
            # Text is VERY confident about a non-neutral emotion
            combined_score = text_score * 0.70 + hubert_score * 0.20 + wav2vec2_score * 0.10

            return {
                'label': text_label,
                'score': min(round(combined_score, 4), 1.0),
                'confidence': 'very_high',
                'hubert_emotion': result.get('hubert_emotion'),
                'hubert_score': hubert_score,
                'wav2vec2_emotion': result.get('wav2vec2_emotion'),
                'wav2vec2_score': wav2vec2_score,
                'text_emotion': result.get('text_emotion'),
                'text_score': text_score,
                'agreement': 'text_veto',
                'sarcasm_flag': False,
                'mixed_emotion_flag': False,
                'method': self.mode,
                'note': 'Text model very high confidence override'
            }

        # HuBERT veto
        if hubert_score > 0.90 and hubert_label != 'neu':
            combined_score = hubert_score * 0.70 + wav2vec2_score * 0.20 + text_score * 0.10

            return {
                'label': hubert_label,
                'score': min(round(combined_score, 4), 1.0),
                'confidence': 'very_high',
                'hubert_emotion': result.get('hubert_emotion'),
                'hubert_score': hubert_score,
                'wav2vec2_emotion': result.get('wav2vec2_emotion'),
                'wav2vec2_score': wav2vec2_score,
                'text_emotion': result.get('text_emotion'),
                'text_score': text_score,
                'agreement': 'hubert_veto',
                'sarcasm_flag': False,
                'mixed_emotion_flag': False,
                'method': self.mode,
                'note': 'HuBERT very high confidence override'
            }

        return None  # No veto conditions met

    def _validate_with_acoustics(self, emotion: str, score: float,
                                 acoustic_features: Dict) -> float:
        """
        Validate emotion prediction using acoustic features.

        IMPROVEMENT #3: Acoustic Feature Integration
        """
        if not acoustic_features:
            return score

        pitch = acoustic_features.get('pitch_mean_f0', 0)
        jitter = acoustic_features.get('jitter_local', 0)
        hnr = acoustic_features.get('hnr_mean', 0)

        # Anger: High pitch, high jitter, low HNR (rough voice)
        if emotion == 'ang':
            if pitch > 150 and jitter > 0.02 and hnr < 10:
                return score * 1.15  # Boost confidence
            elif pitch < 100 and jitter < 0.01:
                return score * 0.85  # Reduce confidence (doesn't match anger)

        # Sadness: Low pitch, moderate jitter, low HNR
        elif emotion == 'sad':
            if pitch < 110 and hnr < 8:
                return score * 1.10
            elif pitch > 150:
                return score * 0.90

        # Happiness: Rising pitch, low jitter, high HNR
        elif emotion == 'hap':
            if pitch > 130 and jitter < 0.015 and hnr > 10:
                return score * 1.10
            elif pitch < 100:
                return score * 0.90

        # Neutral: Moderate everything
        elif emotion == 'neu':
            if 100 < pitch < 150 and jitter < 0.015 and hnr > 10:
                return score * 1.05

        return score

    def _calibrate_confidence(self, score: float, emotion: str) -> str:
        """
        Calibrate confidence labels based on score and emotion type.

        IMPROVEMENT #4: Confidence Calibration
        """
        # Higher threshold for neutral (reduce false neutral confidence)
        if emotion == 'neu':
            if score > 0.85:
                return 'very_high'
            elif score > 0.65:
                return 'high'
            elif score > 0.45:
                return 'medium'
            else:
                return 'low'

        # Lower threshold for strong emotions (they're harder to detect)
        else:
            if score > 0.75:
                return 'very_high'
            elif score > 0.55:
                return 'high'
            elif score > 0.35:
                return 'medium'
            else:
                return 'low'

    def _handle_text_audio_disagreement(self, audio_label: str, text_label: str,
                                        hubert_score: float, wav2vec2_score: float,
                                        text_score: float, result: Dict, weights: Dict,
                                        acoustic_features: Optional[Dict]) -> Dict:
        """
        Handle cases where text and audio models disagree.

        IMPROVEMENT #5: Refined Text-Audio Disagreement Logic
        """
        # If text is very confident (>0.85) about strong emotion
        if text_score > 0.85 and text_label not in ['neu', 'neutral']:
            # Check acoustic features to validate
            if acoustic_features:
                pitch = acoustic_features.get('pitch_mean_f0', 0)
                jitter = acoustic_features.get('jitter_local', 0)

                # If acoustic features support strong emotion (loud, intense)
                if pitch > 140 or jitter > 0.018:
                    # Trust text (person is masking emotion in voice but words reveal it)
                    combined_score = text_score * 0.55 + hubert_score * 0.25 + wav2vec2_score * 0.20

                    return {
                        'label': text_label,
                        'score': min(round(combined_score, 4), 1.0),
                        'confidence': 'high',
                        'hubert_emotion': result.get('hubert_emotion'),
                        'hubert_score': hubert_score,
                        'wav2vec2_emotion': result.get('wav2vec2_emotion'),
                        'wav2vec2_score': wav2vec2_score,
                        'text_emotion': result.get('text_emotion'),
                        'text_score': text_score,
                        'agreement': 'text_priority',
                        'sarcasm_flag': False,
                        'mixed_emotion_flag': False,
                        'method': self.mode,
                        'note': 'High text confidence with acoustic validation'
                    }

        # Otherwise, audio consensus wins (genuine sarcasm or restraint)
        combined_score = (
            hubert_score * 0.50 +
            wav2vec2_score * 0.35 +
            text_score * 0.15
        )

        return {
            'label': audio_label,
            'score': min(round(combined_score, 4), 1.0),
            'confidence': 'high',
            'hubert_emotion': result.get('hubert_emotion'),
            'hubert_score': hubert_score,
            'wav2vec2_emotion': result.get('wav2vec2_emotion'),
            'wav2vec2_score': wav2vec2_score,
            'text_emotion': result.get('text_emotion'),
            'text_score': text_score,
            'agreement': 'audio_consensus',
            'sarcasm_flag': True,
            'mixed_emotion_flag': False,
            'method': self.mode
        }

    def _handle_mixed_predictions(self, hubert_label: str, wav2vec2_label: str,
                                  text_label: Optional[str],
                                  hubert_score: float, wav2vec2_score: float,
                                  text_score: float, result: Dict, weights: Dict,
                                  acoustic_features: Optional[Dict]) -> Dict:
        """
        Handle cases with no clear agreement using weighted voting.
        """
        has_text = text_label is not None

        # Use weighted vote
        vote_scores = {}

        vote_scores[hubert_label] = vote_scores.get(hubert_label, 0) + (
            hubert_score * weights['hubert']
        )

        vote_scores[wav2vec2_label] = vote_scores.get(wav2vec2_label, 0) + (
            wav2vec2_score * weights['wav2vec2']
        )

        if has_text:
            vote_scores[text_label] = vote_scores.get(text_label, 0) + (
                text_score * weights['text']
            )

        primary_label = max(vote_scores, key=vote_scores.get)
        combined_score = vote_scores[primary_label]

        # Apply acoustic validation
        if acoustic_features:
            combined_score = self._validate_with_acoustics(
                primary_label, combined_score, acoustic_features
            )

        # Calibrate confidence
        confidence = self._calibrate_confidence(combined_score, primary_label)

        return {
            'label': primary_label,
            'score': round(combined_score, 4),
            'confidence': confidence,
            'hubert_emotion': result.get('hubert_emotion'),
            'hubert_score': hubert_score,
            'wav2vec2_emotion': result.get('wav2vec2_emotion'),
            'wav2vec2_score': wav2vec2_score,
            'text_emotion': result.get('text_emotion'),
            'text_score': text_score,
            'agreement': 'partial',
            'sarcasm_flag': False,
            'mixed_emotion_flag': True,
            'method': self.mode
        }

    def _map_to_hubert(self, label: str, acoustic_features: Optional[Dict] = None) -> str:
        """
        Map Wav2Vec2 and text model emotions to HuBERT's label space.

        IMPROVEMENT #6: Context-Aware Emotion Mapping
        Uses acoustic features for ambiguous mappings.

        HuBERT labels: ['neu', 'hap', 'ang', 'sad']
        Wav2Vec2 labels: ['angry', 'calm', 'disgust', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        Text labels: ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        """
        # Simple mappings (unambiguous)
        simple_mapping = {
            'angry': 'ang',
            'calm': 'neu',
            'happy': 'hap',
            'neutral': 'neu',
            'sad': 'sad',
            'anger': 'ang',
            'joy': 'hap',
            'sadness': 'sad',
            'neu': 'neu',
            'hap': 'hap',
            'ang': 'ang'
        }

        if label in simple_mapping:
            return simple_mapping[label]

        # Context-aware mappings (use acoustic features if available)
        if label in ['disgust', 'fearful', 'fear', 'surprised', 'surprise']:
            if not acoustic_features:
                # Default fallback without acoustics
                default_mapping = {
                    'disgust': 'ang',
                    'fearful': 'sad',
                    'fear': 'sad',
                    'surprised': 'neu',  # Changed: surprise is ambiguous
                    'surprise': 'neu'
                }
                return default_mapping.get(label, 'neu')

            pitch = acoustic_features.get('pitch_mean_f0', 120)
            jitter = acoustic_features.get('jitter_local', 0.01)

            # Disgust: Usually has anger-like prosody
            if label == 'disgust':
                return 'ang'

            # Fear/Fearful: Context-dependent
            if label in ['fearful', 'fear']:
                if pitch > 140 and jitter > 0.02:
                    return 'ang'  # Panic/agitation
                else:
                    return 'sad'  # Anxiety/worry

            # Surprise: Context-dependent
            if label in ['surprised', 'surprise']:
                if pitch > 140:
                    return 'hap'  # Positive surprise
                elif jitter > 0.02:
                    return 'ang'  # Shock/alarm
                else:
                    return 'neu'  # Mild surprise

        return 'neu'  # Default to neutral if unknown

