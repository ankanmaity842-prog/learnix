import { useSearchParams } from "react-router-dom";
import { useState } from "react";

import SearchBar from "../../components/SearchBar/SearchBar";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";
import LevelSelector from "../../components/LevelSelector/LevelSelector";
import VideoGrid from "../../components/VideoGrid/VideoGrid";

import "./Search.css";

function Search() {
  const [params] = useSearchParams();

  const initialQuery = params.get("q") || "";

  const [query, setQuery] = useState(initialQuery);

  const [language, setLanguage] = useState("en");

  const [level, setLevel] = useState("beginner");

  const [videos, setVideos] = useState([]);

  const search = async (value) => {
    setQuery(value);

    // Connect to:
    // GET /api/search/?q=...
    // through services/api.js
  };

  return (
    <div className="search-page">

      <main className="search-container">
        <div className="search-heading">
          <span>Explore</span>

          <h1>Find your next lesson</h1>

          <p>
            Search any topic and Learnix will
            evaluate available educational videos.
          </p>
        </div>

        <SearchBar onSearch={search} />

        <div className="search-filters">
          <LanguageSelector
            value={language}
            onChange={setLanguage}
          />

          <LevelSelector
            value={level}
            onChange={setLevel}
          />
        </div>

        <div className="results-heading">
          <div>
            <span>Results</span>

            <h2>
              {query || "Recommended videos"}
            </h2>
          </div>

          <small>
            {videos.length} videos
          </small>
        </div>

        <VideoGrid videos={videos} />
      </main>

    </div>
  );
}

export default Search;