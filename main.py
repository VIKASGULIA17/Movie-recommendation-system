import streamlit as st
import pickle
import pandas as pd
import requests

# OMDb API Key
OMDB_API_KEY = "8c564c60"

# Function to fetch movie banner using OMDb API
def fetch_banner_omdb(movie_id):
    url = f"http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_url = data.get('Poster')
        if poster_url and poster_url != 'N/A':
            return poster_url
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching banner for ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750.png?text=No+Image"

# Load the pickled data
movie = pickle.load(open("movies.pkl", "rb"))
correlation = pickle.load(open("correlation.pkl", "rb"))

# Convert back to dataframe
movie = pd.DataFrame(movie)

# Safe movie recommendation function
def movie_recommendation(title):
    if title not in movie['title'].values:
        return [], []

    movie_index = movie[movie['title'] == title].index[0]
    distance = correlation[movie_index]
    movie_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:4]

    recommendation = []
    poster = []
    for index in movie_list:
        movie_id = movie.iloc[index[0]]['imdb_id']
        recommendation.append(movie.iloc[index[0]]['title'])
        banner = fetch_banner_omdb(movie_id)
        poster.append(banner)
    return recommendation, poster

# Streamlit UI
st.title("Movie Recommendation System")

movie_title = movie['title'].values
option = st.selectbox("Select a movie", movie_title)

if st.button("Recommend movie"):
    recommendation, poster = movie_recommendation(option)
    if recommendation:
        cols = st.columns(3)  # Create 3 side-by-side columns

        for i in range(3):
            with cols[i]:
                st.image(poster[i], use_container_width=True)
                st.write(recommendation[i])
    else:
        st.warning("Movie not found.")
