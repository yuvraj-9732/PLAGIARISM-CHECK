import os
import pickle
from suffix_trees import STree

class SuffixTreeIndex:
    def __init__(self, config):
        self.config = config
        self.trees = {}  # doc_id -> suffix tree
    
    def build_index(self, corpus_dir):
        """Build suffix trees for all documents in corpus"""
        if not os.path.exists(corpus_dir):
            raise FileNotFoundError(f"Corpus directory not found: {corpus_dir}")
        
        for filename in os.listdir(corpus_dir):
            if filename.endswith('.txt'):
                doc_id = filename.split('.')[0]
                filepath = os.path.join(corpus_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read().lower()
                
                self.trees[doc_id] = STree.STree(text)
    
    def find_exact_matches(self, query: str, doc_id: str) -> list:
        """Find exact matches of query in document"""
        if doc_id not in self.trees:
            return []
        
        tree = self.trees[doc_id]
        query_lower = query.lower() # Lowercase the query to match the tree's text
        
        # Use the built-in find_all method which is more efficient
        return tree.find_all(query_lower)