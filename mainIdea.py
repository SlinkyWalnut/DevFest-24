import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download NLTK resources if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def get_main_idea(question):
    # Tokenization
    tokens = word_tokenize(question.lower())
    
    # Stopword Removal
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]
    
    # Consider significant words (nouns, verbs, adjectives)
    pos_tags = nltk.pos_tag(lemmatized_tokens)
    main_idea_tokens = [word for word, pos in pos_tags if pos.startswith('N') or pos.startswith('V') or pos.startswith('J')]
    
    # Join the tokens to form the main idea
    main_idea = ' '.join(main_idea_tokens)
    print(main_idea)
    
    return main_idea
