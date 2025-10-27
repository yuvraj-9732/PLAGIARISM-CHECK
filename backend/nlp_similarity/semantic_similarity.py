import os
import torch
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict

class SemanticSimilarity:
    def __init__(self, config):
        self.config = config
        self.model = SentenceTransformer(config['SBERT_MODEL'])
        self.embeddings = {}  # doc_id -> sentence embeddings
        self.sentences = {}   # doc_id -> sentences
    
    def build_index(self, corpus_dir):
        """Precompute embeddings for all reference documents"""
        if not os.path.exists(corpus_dir):
            raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")
        
        for filename in os.listdir(corpus_dir):
            if filename.endswith('.txt'):
                doc_id = filename.split('.')[0]
                filepath = os.path.join(corpus_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Simple sentence splitting
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                
                if not sentences:
                    continue
                
                # Compute embeddings
                embeddings = self.model.encode(sentences, convert_to_tensor=True)
                
                self.sentences[doc_id] = sentences
                self.embeddings[doc_id] = embeddings
    
    def find_similar_sentences(self, query_sentence: str, threshold: float = None) -> List[Dict]:
        """Find sentences similar to query in reference corpus"""
        if threshold is None:
            threshold = self.config['SIMILARITY_THRESHOLD']
        
        query_embedding = self.model.encode(query_sentence, convert_to_tensor=True)
        results = []
        
        for doc_id, ref_embeddings in self.embeddings.items():
            # Compute cosine similarities
            cos_scores = util.cos_sim(query_embedding, ref_embeddings)[0]
            
            # Find sentences above threshold
            top_results = torch.where(cos_scores >= threshold)[0]
            for idx in top_results:
                score = cos_scores[idx].item()
                results.append({
                    'doc_id': doc_id,
                    'sentence': self.sentences[doc_id][idx],
                    'score': score
                })
        
        return results