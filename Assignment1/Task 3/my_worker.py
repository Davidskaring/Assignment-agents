import string
from collections import Counter

# Worker function to be executed by parallel processes
def clean_and_count(text_chunk):
    # Create a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    
    # Clean data: Remove punctuation and convert to lowercase
    clean_text = text_chunk.translate(translator).lower()
    
    # Split the text into individual words
    words = clean_text.split()
    
    # Return a Counter object (dictionary of word frequencies)
    return Counter(words)