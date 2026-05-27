from sentence_transformers import SentenceTransformer, util
from sentence_transformers import CrossEncoder
import numpy as np
import threading

_lock = threading.Lock()
_embedding_model = None
_cross_encoder = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        with _lock:
            if _embedding_model is None:
                _embedding_model = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
    return _embedding_model


def get_cross_encoder():
    global _cross_encoder
    if _cross_encoder is None:
        with _lock:
            if _cross_encoder is None:
                _cross_encoder = CrossEncoder(
                    "cross-encoder/ms-marco-MiniLM-L-6-v2"
                )
    return _cross_encoder


class ResponseEvaluator:

    def evaluate(self, question: str, answer: str):

        # 1️⃣ Semantic similarity
        model = get_embedding_model()

        q_emb = model.encode(question, convert_to_tensor=True)
        a_emb = model.encode(answer, convert_to_tensor=True)

        semantic_score = float(util.cos_sim(q_emb, a_emb))

        # 2️⃣ Cross-encoder score
        cross_encoder = get_cross_encoder()
        cross_score = float(
            cross_encoder.predict([(question, answer)])[0]
        )

        # 3️⃣ Keyword overlap simple
        q_words = set(question.lower().split())
        a_words = set(answer.lower().split())

        overlap = len(q_words.intersection(a_words))
        keyword_score = overlap / (len(q_words) + 1e-6)

        # 4️⃣ Score global pondéré
        final_score = (
            0.4 * semantic_score +
            0.4 * cross_score +
            0.2 * keyword_score
        )

        return {
            "semantic_score": round(semantic_score, 3),
            "cross_score": round(cross_score, 3),
            "keyword_score": round(keyword_score, 3),
            "final_score": round(final_score, 3),
            "quality": self._quality_label(final_score)
        }

    def _quality_label(self, score):

        if score > 0.75:
            return "Excellent"
        elif score > 0.55:
            return "Good"
        elif score > 0.35:
            return "Weak"
        else:
            return "Poor"