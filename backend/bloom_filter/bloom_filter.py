import os
import pickle
from pybloom_live import ScalableBloomFilter

class BloomFilterIndex:
    def __init__(self, config):
        self.config = config
        self.filters = {}  # doc_id -> bloom filter
        self.k = config['KMER_SIZE']
    
    def build_index(self, corpus_dir):
        """Build bloom filters for all documents in corpus"""
        if not os.path.exists(corpus_dir):
            raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")
        
        for filename in os.listdir(corpus_dir):
            if filename.endswith('.txt'):
                doc_id = filename.split('.')[0]
                filepath = os.path.join(corpus_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read().lower()
                
                # Create bloom filter
                bloom = ScalableBloomFilter(
                    initial_capacity=self.config['BLOOM_INITIAL_CAPACITY'],
                    error_rate=self.config['BLOOM_ERROR_RATE']
                )
                
                # Add all k-mers
                for i in range(len(text) - self.k + 1):
                    kmer = text[i:i+self.k]
                    bloom.add(kmer)
                
                self.filters[doc_id] = bloom
    
    def might_contain(self, query_text: str, doc_id: str) -> bool:
        """Check if document might contain query text"""
        if doc_id not in self.filters:
            return False
        
        bloom = self.filters[doc_id]
        query_text = query_text.lower()
        
        # For a query to be a potential substring, all its k-mers must be in the bloom filter.
        if len(query_text) < self.k:
            return query_text in bloom

        for i in range(len(query_text) - self.k + 1):
            kmer = query_text[i:i+self.k]
            if kmer not in bloom:
                return False # If any k-mer is missing, it's not a match.
        return True