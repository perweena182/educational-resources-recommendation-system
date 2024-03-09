from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS
from googleapiclient.discovery import build


app = Flask(__name__)
CORS(app) 
# Load datasets
try:
    df = pd.read_csv('Books.csv')

# Function to update URL from HTTP to HTTPS
    def update_url(url):
        if url.startswith('http://'):
            return 'https://' + url[len('http://'):]
        return url

# Update URLs in the DataFrame
    df['Image-URL-M'] = df['Image-URL-M'].apply(update_url)

# Write back to CSV
    df.to_csv('updated_books.csv', index=False)
    books = pd.read_csv('updated_books.csv')
    users = pd.read_csv('users.csv')
    ratings = pd.read_csv('ratings.csv')

    # Preprocessing
    ratings_with_name = ratings.merge(books, on='ISBN')
    x = ratings_with_name.groupby('User-ID').count()['Book-Rating'] > 200
    users_goodrating = x[x].index
    filtered_rating = ratings_with_name[ratings_with_name['User-ID'].isin(users_goodrating)]
    y = filtered_rating.groupby('Book-Title').count()['Book-Rating'] >= 50
    famous_books = y[y].index
    final_ratings = filtered_rating[filtered_rating['Book-Title'].isin(famous_books)]
    pt = final_ratings.pivot_table(index='Book-Title', columns='User-ID', values='Book-Rating')
    pt.fillna(0, inplace=True)
    similarity_scores = cosine_similarity(pt)

except Exception as e:
    print("Error loading datasets or preprocessing:", e)

# Your recommend function
def recommend(book_name):
    try:
        index = np.where(pt.index == book_name)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]
        
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            
            data.append(item)
        
        return data

    except Exception as e:
        print("Error in recommend function:", e)
        return []
YOUTUBE_API_KEY = 'AIzaSyAOaWeuNWz-bX8gSarFnJfnDsbiTV-PS3Y'

# Function to search YouTube videos
def search_youtube(query):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=5  # Adjust as needed
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append({
                    'title': search_result['snippet']['title'],
                    'thumbnail': search_result['snippet']['thumbnails']['default']['url'],
                    'video_id': search_result['id']['videoId']
                })

        return videos
    except Exception as e:
        print("Error searching YouTube:", e)
        return []

        
# Flask route to handle YouTube search requests
@app.route('/search_youtube', methods=['POST'])
def search_youtube_endpoint():
    try:
        query = request.json['query']
        results = search_youtube(query)
        return jsonify({'results': results})
    except Exception as e:
        print("Error processing YouTube search request:", e)
        return jsonify({'results': []})


# Flask route to handle recommendations
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        # Extract book name from request
        book_name = request.json['book_name']
        
        # Call the recommend function
        recommendations = recommend(book_name)
        
        return jsonify({'recommendations': recommendations})

    except Exception as e:
        print("Error processing request:", e)
        return jsonify({'recommendations': []})

if __name__ == '__main__':
    app.run(debug=True)
