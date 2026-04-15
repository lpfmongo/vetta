from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DomainRerankingResult:
    """Represents a single reranked document with its relevance score."""

    relevance_score: float
    index: int
    document: Optional[str] = None

    def __post_init__(self):
        """Runtime validation to ensure the parsed API payload is strictly correct."""
        if not isinstance(self.relevance_score, (float, int)) or isinstance(
            self.relevance_score, bool
        ):
            raise TypeError(
                f"Expected 'relevance_score' to be a float, got {type(self.relevance_score).__name__}"
            )

        if not isinstance(self.index, int) or isinstance(self.index, bool):
            raise TypeError(
                f"Expected 'index' to be an int, got {type(self.index).__name__}"
            )

        if self.index < 0:
            raise ValueError("Expected 'index' to be non-negative.")

        if self.document is not None and not isinstance(self.document, str):
            raise TypeError("Document must be a string or None.")


@dataclass
class DomainRerankingResponse:
    """The full result of a reranking request."""

    model: str
    results: List[DomainRerankingResult]
    total_tokens: int

    def __post_init__(self):
        if not isinstance(self.model, str) or not self.model.strip():
            raise TypeError("Expected 'model' to be a non-empty string.")
        if not isinstance(self.results, list):
            raise TypeError(
                "Expected 'results' to be a list of DomainRerankingResult objects."
            )
        if not all(isinstance(r, DomainRerankingResult) for r in self.results):
            raise TypeError(
                "All items in 'results' must be DomainRerankingResult instances."
            )
        if not isinstance(self.total_tokens, int) or isinstance(
            self.total_tokens, bool
        ):
            raise TypeError(
                f"Expected 'total_tokens' to be an int, got {type(self.total_tokens).__name__}"
            )
        if self.total_tokens < 0:
            raise ValueError("Expected 'total_tokens' to be non-negative.")
