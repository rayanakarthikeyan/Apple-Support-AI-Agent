import re, math
from typing import List, Dict, Tuple, Optional
from src.agent.models import ResolutionExemplar, Intent

class BM25Retriever:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[ResolutionExemplar] = []
        self.doc_lengths: List[int] = []
        self.avgdl: float = 0.0
        self.df: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    @staticmethod
    def tokenize(text: str) -> List[str]:
        text = text.lower()
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        return re.findall(r'[a-z0-9_]+', text)

    def fit(self, exemplars: List[ResolutionExemplar]):
        self.corpus = exemplars
        N = len(exemplars)
        if N == 0:
            return
        self.doc_lengths = []
        self.df = {}
        for ex in exemplars:
            combined = ex.customer_text + ' ' + ex.brand_reply + ' ' + ' '.join(ex.tags)
            tokens = self.tokenize(combined)
            self.doc_lengths.append(len(tokens))
            for t in set(tokens):
                self.df[t] = self.df.get(t, 0) + 1
        self.avgdl = sum(self.doc_lengths) / max(1, N)
        self.idf = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log(1.0 + (N - freq + 0.5) / (freq + 0.5))

    def retrieve(self, query: str, top_k: int = 3, intent_filter: Optional[Intent] = None) -> List[Tuple[ResolutionExemplar, float]]:
        query_tokens = self.tokenize(query)
        if not self.corpus or not query_tokens:
            return [(ex, 0.0) for ex in self.corpus[:top_k]]
        scores = []
        for idx, ex in enumerate(self.corpus):
            boost = 1.5 if (intent_filter and ex.intent == intent_filter) else 0.0
            doc_len = self.doc_lengths[idx]
            combined = ex.customer_text + ' ' + ex.brand_reply + ' ' + ' '.join(ex.tags)
            doc_tokens = self.tokenize(combined)
            doc_freqs = {}
            for dt in doc_tokens:
                doc_freqs[dt] = doc_freqs.get(dt, 0) + 1
            score = 0.0
            for qt in query_tokens:
                if qt in doc_freqs:
                    tf = doc_freqs[qt]
                    idf_val = self.idf.get(qt, 0.1)
                    denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avgdl)))
                    score += idf_val * ((tf * (self.k1 + 1.0)) / denom)
            score += boost
            scores.append((ex, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]