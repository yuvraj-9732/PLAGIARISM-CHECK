import os
import re
import string
import pdfplumber
from typing import Union
try:
    import nltk
    nltk.data.find('tokenizers/punkt')
except (ImportError, LookupError):
    print("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt')

class TextProcessor:
    def __init__(self, config):
        self.config = config

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or TXT files"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_ext == '.txt':
            return self._extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        text = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return '\n'.join(text)
    
    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text according to configuration"""
        # Lowercase conversion
        text = text.lower()
        
        # Remove punctuation (if enabled)
        if self.config['REMOVE_PUNCTUATION']:
            translator = str.maketrans('', '', string.punctuation)
            text = text.translate(translator)
        
        # Remove digits (if enabled)
        if self.config['REMOVE_DIGITS']:
            text = re.sub(r'\d+', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove stopwords (if enabled)
        if self.config['REMOVE_STOPWORDS']:
            try:
                from nltk.corpus import stopwords
                stop_words = set(stopwords.words('english'))
                words = [word for word in text.split() if word not in stop_words]
                text = ' '.join(words)
            except ImportError:
                print("Warning: NLTK not available. Skipping stopword removal.")
        
        return text
    
    def split_into_sentences(self, text: str) -> list:
        """Split text into sentences using NLTK for better accuracy."""
        try:
            return nltk.sent_tokenize(text)
        except Exception as e:
            print(f"NLTK sentence tokenization failed: {e}. Falling back to basic split.")
            return [s.strip() for s in text.split('.') if s.strip()]

    def process_document(self, file_path: str) -> dict:
        """Extract and preprocess document text"""
        raw_text = self.extract_text_from_file(file_path)
        preprocessed_text = self.preprocess_text(raw_text)
        sentences = self.split_into_sentences(raw_text) # Use raw text for sentence splitting

        return {
            'raw_text': raw_text,
            'preprocessed_text': preprocessed_text,
            'sentences': sentences
        }