from typing import List
from app.models.schemas import SourceCitation

class GroundingEvaluator:

    @classmethod
    def evaluate_groundedness(cls, answer: str, citations: List[SourceCitation]) -> float:
        """
        Calculates a baseline groundedness score (0.0 to 1.0) by checking token overlap
        between the LLM generated answer and the source citations.
        """
        if not answer or not citations:
            return 0.0

        # Tokenize answer and citations into lowercase word sets
        import re
        answer_words = set(re.findall(r'\w+', answer.lower()))
        if not answer_words:
            return 0.0

        citation_text = " ".join([c.snippet for c in citations])
        citation_words = set(re.findall(r'\w+', citation_text.lower()))

        # Filter out common stop words
        stopwords = {"the", "a", "an", "is", "are", "and", "or", "in", "on", "at", "to", "for", "of", "with", "by"}
        answer_words -= stopwords
        citation_words -= stopwords

        if not answer_words:
            return 1.0

        overlap = answer_words.intersection(citation_words)
        score = len(overlap) / len(answer_words)

        return round(min(1.0, max(0.0, score)), 2)
