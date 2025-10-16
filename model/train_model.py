import pandas as pd
import ast
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load datasets
movies = pd.read_csv('../data/movies.csv')
credits = pd.read_csv('../data/credits.csv')

# Merge datasets
movies = movies.merge(credits, on='title')

# Select important columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Convert JSON-like strings to Python lists
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

movies.dropna(inplace=True)

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)[:3]])
movies['crew'] = movies['crew'].apply(lambda x: [i['name'] for i in ast.literal_eval(x) if i['job'] == 'Director'])

# Convert overview (string) into a list
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Combine all text into 'tags'
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create new dataframe
new_df = movies[['movie_id', 'title', 'tags']]

# Convert list -> string
new_df = new_df.copy()
new_df.loc[:, 'tags'] = new_df['tags'].apply(lambda x: " ".join(x))


# Vectorize tags text
tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
vectors = tfidf.fit_transform(new_df['tags'])

# Compute cosine similarity
cosine_sim = cosine_similarity(vectors)

# Save model and data
pickle.dump(new_df, open('content_model.pkl', 'wb'))
pickle.dump(cosine_sim, open('cosine_sim.pkl', 'wb'))

print("✅ Model trained & saved successfully!")
