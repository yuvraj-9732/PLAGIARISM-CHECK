import os

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-123'
    UPLOAD_FOLDER = 'data/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Data Paths
    TEMP_DIR = 'data/temp'
    
    # Preprocessing
    REMOVE_STOPWORDS = False
    REMOVE_DIGITS = True
    REMOVE_PUNCTUATION = True
    
    # Bloom Filter
    BLOOM_ERROR_RATE = 0.001
    BLOOM_INITIAL_CAPACITY = 10000
    KMER_SIZE = 7
    
    # NLP Similarity
    SBERT_MODEL = 'all-MiniLM-L6-v2'
    SIMILARITY_THRESHOLD = 0.8
    
    # Web Search Settings
    SEARCH_RESULTS_PER_QUERY = 3
    MIN_SENTENCE_LENGTH = 5  # Minimum words in a sentence to search
    MAX_SENTENCES_TO_CHECK = 50  # Limit to prevent too many API calls
    REQUEST_DELAY = 1.0  # Seconds between requests
    
    # Web Scraping Settings
    REQUEST_TIMEOUT = 10
    MAX_CONTENT_LENGTH = 50000  # Max characters to extract per page
    SKIP_DOMAINS = ['facebook.com', 'twitter.com', 'instagram.com', 'youtube.com']