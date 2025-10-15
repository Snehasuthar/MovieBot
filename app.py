from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
from fuzzywuzzy import process

app = Flask(__name__)

# Load data and similarity matrix
movies = pickle.load(open('model/content_model.pkl', 'rb'))
similarity = pickle.load(open('model/cosine_sim.pkl', 'rb'))

# Load original data (for movie details)
movies_full = pd.read_csv('data/movies.csv')

# Recommendation function
def recommend(movie, top_n=5):
    movie = movie.lower().strip()
    if movie not in movies['title'].str.lower().values:
        return []
    idx = movies[movies['title'].str.lower() == movie].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])
    recs = []
    for i in distances[1:top_n + 1]:
        recs.append(movies.iloc[i[0]].title)
    return recs

# Fuzzy match
def suggest_movie_name(input_movie):
    all_titles = movies['title'].tolist()
    suggestion, score = process.extractOne(input_movie, all_titles)
    if score >= 70:
        return suggestion
    return None

@app.route('/')
def home():
    famous_movies = ['Avatar', 'The Dark Knight', 'Inception', 'Titanic', 'Interstellar']
    return render_template('index.html', famous_movies=famous_movies)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    movie_name = request.form['movie_name']
    
    # Fetch movie details from dataset
    movie_row = movies_full[movies_full['title'].str.lower() == movie_name.lower()]
    movie_info = None
    
    if not movie_row.empty:
        movie = movie_row.iloc[0]
        movie_info = {
            "title": movie['title'],
            "overview": movie.get('overview', 'No description available.'),
            "release_date": movie.get('release_date', 'Unknown'),
            "rating": movie.get('vote_average', 'N/A')
        }

    # Generate recommendations
    recommendations = recommend(movie_name)
    
    if not recommendations:
        suggestion = suggest_movie_name(movie_name)
        if suggestion:
            return jsonify({"error": f"Did you mean '{suggestion}'?"})
        else:
            return jsonify({"error": "Movie not found!"})
    
    return jsonify({
        "movie_info": movie_info,
        "recommendations": recommendations
    })

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('q', '').lower()
    matches = movies[movies['title'].str.lower().str.contains(query, na=False)]
    return jsonify(matches['title'].head(10).tolist())

# 🔍 New route — fetch movie details
@app.route('/movie_info', methods=['GET'])
def movie_info():
    title = request.args.get('title', '')
    movie_row = movies_full[movies_full['title'].str.lower() == title.lower()]
    
    if movie_row.empty:
        return jsonify({"error": "No details found"})
    
    movie = movie_row.iloc[0]
    info = {
        "title": movie['title'],
        "overview": movie.get('overview', 'No description available.'),
        "release_date": movie.get('release_date', 'Unknown'),
        "rating": movie.get('vote_average', 'N/A')
    }
    return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
