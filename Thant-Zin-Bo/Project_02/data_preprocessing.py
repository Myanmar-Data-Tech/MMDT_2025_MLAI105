import pandas as pd
import re # regular expressions 
import nltk  # tokenisation & lemmatisation helpers
from nltk.corpus import stopwords   # list of common stop-words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
#nltk.download('punkt'/'stopwords'/'wordnet') pulls the tokeniser rules, stop-word list, and WordNet lemma database the first time the code runs.
def remove_special_characters(text):
    # Remove special characters and numbers #to make vectoriser treats “Apple” and “apple” as the same token.
    text = re.sub('[^a-zA-Z]', ' ', text)
    return text.lower()



# Replace  one hot  preprocessing
def preprocess_text_features(df, text_column):
    # Character-level n-grams (2-4 characters)
    vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 10),
        max_features=1000,
        lowercase=True
    )
    
    # Fit and transform the text data
    text_features = vectorizer.fit_transform(df[text_column].astype(str))
    
    return text_features.toarray(), vectorizer





def clean_text(text):
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    # Tokenize text
    tokens = word_tokenize(text.lower())
    
    # Remove punctuation and stop words, and lemmatize
    cleaned_tokens = [lemmatizer.lemmatize(word) 
                      for word in tokens if word.isalnum() and word not in stop_words]
    
    return ' '.join(cleaned_tokens)

def preprocess_textinput(df, text_column):    
    vectorizer = CountVectorizer(max_features=5000)  
    df['cleaned_text'] = df[text_column].apply(remove_special_characters)    
    X = vectorizer.fit_transform(df['cleaned_text']).toarray()
    return X

def preprocess_category(df, column):
    df[column] = df[column].astype('category')
    df[column] = df[column].cat.codes
    return df

def preprocess_onehot(df, column):
    df = pd.get_dummies(df, columns=[column])
    return df