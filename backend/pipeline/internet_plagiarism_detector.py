import os
import tempfile
import uuid
from tqdm import tqdm
from preprocessing.text_processor import TextProcessor
from web_search.web_search import WebSearchEngine
from web_search.content_extractor import WebContentExtractor
from bloom_filter.bloom_filter import BloomFilterIndex
from suffix_tree.suffix_tree import SuffixTreeIndex
from nlp_similarity.semantic_similarity import SemanticSimilarity

class InternetPlagiarismDetector:
    def __init__(self, config):
        self.config = config
        self.text_processor = TextProcessor(config)
        self.web_search = WebSearchEngine(config)
        self.content_extractor = WebContentExtractor(config)
        self.bloom_filter = BloomFilterIndex(config)
        self.suffix_tree = SuffixTreeIndex(config)
        self.nlp = SemanticSimilarity(config)
    
    def detect_internet_plagiarism(self, file_path: str) -> dict:
        """Detect plagiarism by searching the internet"""
        # Preprocess input document
        doc_data = self.text_processor.process_document(file_path)
        sentences = doc_data['sentences']
        
        # Limit the number of sentences to check
        if len(sentences) > self.config['MAX_SENTENCES_TO_CHECK']:
            sentences = sentences[:self.config['MAX_SENTENCES_TO_CHECK']]
        
        results = {
            'exact_matches': [],
            'paraphrased_matches': [],
            'web_sources': [],
            'stats': {
                'total_sentences': len(sentences),
                'urls_found': 0,
                'plagiarism_percentage': 0,
                'web_queries_made': 0,
                'urls_checked': 0,
                'exact_matches_found': 0,
                'paraphrased_matches_found': 0
            }
        }
        
        # Create temporary directory for web content
        with tempfile.TemporaryDirectory(dir=self.config['TEMP_DIR']) as temp_dir:
            web_content_files = []
            unique_urls = set()
            total_urls_found_set = set()

            # --- Phase 1: Aggregate Web Content ---
            print("Phase 1: Aggregating web content...")
            for sentence in tqdm(sentences, desc="Searching for sources"):
                # Skip very short sentences
                if len(sentence.split()) < self.config['MIN_SENTENCE_LENGTH']:
                    continue

                # Search web for this sentence
                search_results = self.web_search.search(sentence)
                results['stats']['web_queries_made'] += 1

                if not search_results:
                    continue

                # Extract content from search results
                for result in search_results:
                    total_urls_found_set.add(result['link'])
                    url = result['link']
                    if url in unique_urls:
                        continue

                    # Skip certain domains
                    domain = result.get('displayLink', '') # Assuming displayLink is the domain
                    if any(skip in domain for skip in self.config['SKIP_DOMAINS']):
                        continue

                    # Extract content
                    content = self.content_extractor.extract_content(url)
                    if not content or len(content['text']) < 100:
                        continue

                    unique_urls.add(url)
                    results['stats']['urls_checked'] += 1

                    # Save content to temporary file
                    # Use a unique name for the file to avoid collisions
                    filename = f"web_{uuid.uuid4()}.txt"
                    filepath = os.path.join(temp_dir, filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content['text'])

                    web_content_files.append({
                        'filepath': filepath,
                        'url': url,
                        'title': content['title'],
                        'domain': content['domain']
                    })
            results['stats']['urls_found'] = len(total_urls_found_set)

            # --- Phase 2: Build Global Indexes ---
            if not web_content_files:
                return results # No web content found, no plagiarism

            print("Phase 2: Building search indexes...")
            self._build_temp_indexes(temp_dir)

            # --- Phase 3: Check All Sentences ---
            print("Phase 3: Checking document against sources...")
            plagiarized_sentence_count = 0
            for sentence in tqdm(sentences, desc="Analyzing sentences"):
                matches = self._check_sentence_against_web(sentence, web_content_files)

                if matches['exact']:
                    results['exact_matches'].append({'sentence': sentence, 'sources': matches['exact']})
                    results['stats']['exact_matches_found'] += 1
                    plagiarized_sentence_count += 1
                elif matches['paraphrased']:
                    results['paraphrased_matches'].append({'sentence': sentence, 'sources': matches['paraphrased']})
                    results['stats']['paraphrased_matches_found'] += 1
                    plagiarized_sentence_count += 1

            # --- Phase 4: Calculate Plagiarism Score ---
            if len(sentences) > 0:
                results['stats']['plagiarism_percentage'] = (plagiarized_sentence_count / len(sentences)) * 100

            # Clean up indexes
            self._clear_temp_indexes()

        return results

    def _build_temp_indexes(self, temp_dir: str):
        """Build indexes for temporary web content"""
        self.bloom_filter.build_index(temp_dir)
        self.suffix_tree.build_index(temp_dir)
        self.nlp.build_index(temp_dir)
    
    def _clear_temp_indexes(self):
        """Clear temporary indexes"""
        self.bloom_filter.filters = {}
        self.suffix_tree.trees = {}
        self.nlp.embeddings = {}
        self.nlp.sentences = {}
    
    def _check_sentence_against_web(self, sentence: str, web_content_files: list) -> dict:
        """Check a sentence against web content"""
        matches = {'exact': [], 'paraphrased': []}

        # Check for exact matches
        for content_file in web_content_files:
            doc_id = os.path.splitext(os.path.basename(content_file['filepath']))[0]

            if self.bloom_filter.might_contain(sentence, doc_id):
                positions = self.suffix_tree.find_exact_matches(sentence, doc_id)
                if positions:
                    matches['exact'].append({
                        'url': content_file['url'],
                        'title': content_file['title'],
                    })

        if matches['exact']:
            return matches # If exact matches are found, don't bother with paraphrasing

        # Check for paraphrased matches
        similar_sentences = self.nlp.find_similar_sentences(sentence)
        if similar_sentences:
            best_match = max(similar_sentences, key=lambda x: x['score'])
            
            # Find the corresponding web content file
            doc_id = best_match['doc_id']
            for content_file in web_content_files:
                if doc_id == os.path.splitext(os.path.basename(content_file['filepath']))[0]:
                    matches['paraphrased'].append({
                        'url': content_file['url'],
                        'title': content_file['title'],
                        'matched_sentence': best_match['sentence'],
                        'similarity_score': best_match['score']
                    })
                    break

        return matches