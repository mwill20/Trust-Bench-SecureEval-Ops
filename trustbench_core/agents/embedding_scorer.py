"""Semantic similarity scorer using OpenAI embeddings for faithfulness evaluation."""

from __future__ import annotations

import os
from typing import List, Tuple
import numpy as np


class EmbeddingScorer:
    """Score answer faithfulness using semantic similarity via embeddings."""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        """Initialize the embedding scorer.
        
        Args:
            model: OpenAI embedding model to use (default: text-embedding-3-small)
                   - text-embedding-3-small: Fast, cheap, good quality
                   - text-embedding-3-large: Slower, more expensive, best quality
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI package required. Run: pip install openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text.strip()
        )
        return response.data[0].embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        a = np.array(vec1)
        b = np.array(vec2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def score(self, answer: str, truth: str) -> float:
        """Score answer faithfulness using semantic similarity.
        
        Args:
            answer: The generated answer to evaluate
            truth: The ground truth reference
            
        Returns:
            Similarity score between 0.0 and 1.0, where:
            - 1.0 = semantically identical
            - 0.8+ = high semantic similarity (good answer)
            - 0.6-0.8 = moderate similarity (acceptable)
            - <0.6 = low similarity (poor answer)
        """
        if not answer or not truth:
            return 0.0
        
        answer_emb = self._get_embedding(answer)
        truth_emb = self._get_embedding(truth)
        
        similarity = self._cosine_similarity(answer_emb, truth_emb)
        
        # Normalize to 0-1 range (cosine similarity can be -1 to 1, but typically 0-1 for text)
        return max(0.0, min(1.0, similarity))
    
    def score_batch(self, answers: List[str], truths: List[str]) -> List[float]:
        """Score multiple answer-truth pairs efficiently.
        
        Args:
            answers: List of generated answers
            truths: List of ground truth references
            
        Returns:
            List of similarity scores
        """
        if len(answers) != len(truths):
            raise ValueError(f"Length mismatch: {len(answers)} answers vs {len(truths)} truths")
        
        scores = []
        for answer, truth in zip(answers, truths):
            scores.append(self.score(answer, truth))
        
        return scores


def score_with_embeddings(
    answers: List[str],
    truths: List[str],
    model: str = "text-embedding-3-small"
) -> Tuple[List[float], dict]:
    """Convenience function to score answers using embeddings.
    
    Args:
        answers: Generated answers to evaluate
        truths: Ground truth references
        model: Embedding model to use
        
    Returns:
        Tuple of (scores, metadata)
    """
    try:
        scorer = EmbeddingScorer(model=model)
        scores = scorer.score_batch(answers, truths)
        
        return scores, {
            "scorer": "embedding_similarity",
            "embedding_model": model,
            "ragas": False,
            "reason": "using_openai_embeddings",
        }
    except Exception as exc:
        # Fallback to token overlap if embeddings fail
        raise RuntimeError(f"Embedding scorer failed: {exc}") from exc
