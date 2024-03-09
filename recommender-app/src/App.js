import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [searchTerm, setSearchTerm] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [youtubeResults, setYoutubeResults] = useState([]);
  const [searchHistory, setSearchHistory] = useState([]);

  useEffect(() => {
    const storedHistory = localStorage.getItem('searchHistory');
    if (storedHistory) {
      setSearchHistory(JSON.parse(storedHistory));
    }
  }, []);

  useEffect(() => {
    // Fetch recommendations from Flask backend when component mounts
    fetchRecommendations('');
  }, []);

  const fetchRecommendations = (bookName) => {
    fetch('http://localhost:5000/get_recommendations', {  // Update URL to use port 5000
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ book_name: bookName })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      setRecommendations(data.recommendations);
    })
    .catch(error => {
      console.error('Error fetching recommendations:', error);
      // Handle error here
    });
  };

  const handleSearch = () => {
    fetchRecommendations(searchTerm);
    addToSearchHistory(searchTerm);
  };

  const handleYoutubeSearch = () => {
    searchYoutube(searchTerm);
    addToSearchHistory(searchTerm);
  };

  const addToSearchHistory = (term) => {
    if (!searchHistory.includes(term)) {
      const updatedHistory = [...searchHistory, term];
      setSearchHistory(updatedHistory);
      localStorage.setItem('searchHistory', JSON.stringify(updatedHistory));
    }
  };

  const clearSearchHistory = () => {
    setSearchHistory([]);
    localStorage.removeItem('searchHistory');
  };

  const searchYoutube = (query) => {
    fetch('http://localhost:5000/search_youtube', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => setYoutubeResults(data.results))
    .catch(error => console.error('Error searching YouTube:', error));
  };

  return (
    <div className="App">
      <h1 >Educational Resources Recommendation System</h1>
      <div>
        <input 
          type="text" 
          placeholder="Enter book title or YouTube video query..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={handleSearch}>Search Books</button>
        <button onClick={handleYoutubeSearch}>Search Videos</button>
      </div>
      <div className="content-section">
        <div className="recommendations">
  <div className="recommendations-grid">
    <h1> Recommended images </h1>
    {recommendations.map((recommendation, index) => (
      <div key={index} className="recommendation-item">
        <img src={recommendation[2]} alt={recommendation[0]} />
        <p>{recommendation[0]}</p>
      </div>
    ))}
  </div>

  {/* YouTube results section */}
<div className="youtube-results">
  <h1>YouTube Search Results</h1>
  <div className="videos-grid">
    {youtubeResults.map((video, index) => (
      <div key={index} className="video-item">
        <a href={`https://www.youtube.com/watch?v=${video.video_id}`} target="_blank" rel="noopener noreferrer">
          <img src={video.thumbnail} alt={video.title} />
          <p>{video.title}</p>
        </a>
      </div>
    ))}
  </div>
</div>

        
        <div className="search-history">
          <h2>Search History</h2>
          <ul>
            {searchHistory.map((term, index) => (
              <li key={index}>{term}</li>
            ))}
          </ul>
          <button onClick={clearSearchHistory}>Clear History</button>
        </div>
      </div>
    </div>
    </div>
  );
}

export default App;
