import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import SearchBar from "../../components/SearchBar/SearchBar";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";
import LevelSelector from "../../components/LevelSelector/LevelSelector";
import VideoGrid from "../../components/VideoGrid/VideoGrid";

import recommendationService from "../../services/recommendationService";

import "./Search.css";

function Search() {
  const [params] = useSearchParams();
  const initialQuery = params.get("q") || "";
  const requestSequence = useRef(0);

  const [query, setQuery] = useState(initialQuery);
  const [language, setLanguage] = useState("en");
  const [level, setLevel] = useState("beginner");
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const search = async (value, options = {}) => {
    const cleanQuery = value.trim();

    if (!cleanQuery) {
      requestSequence.current += 1;
      setQuery("");
      setVideos([]);
      setError("");
      setLoading(false);
      return;
    }

    const selectedLanguage = options.language ?? language;
    const selectedLevel = options.level ?? level;
    const requestId = ++requestSequence.current;

    setQuery(cleanQuery);
    setLoading(true);
    setError("");

    try {
      const data = await recommendationService.getForTopic(
        cleanQuery,
        {
          language: selectedLanguage,
          level: selectedLevel,
          limit: 20,
        }
      );

      if (requestId !== requestSequence.current) return;

      const recommendations = Array.isArray(data?.recommendations)
        ? data.recommendations
        : [];

      setVideos(recommendations.slice(0, 20));

      if (!recommendations.length) {
        setError(`No learning videos found for "${cleanQuery}".`);
      }
    } catch (err) {
      if (requestId !== requestSequence.current) return;

      console.error(
        "Search failed:",
        err.response?.data || err
      );

      setVideos([]);
      setError(
        err.response?.data?.detail ||
          "Unable to find learning videos right now."
      );
    } finally {
      if (requestId === requestSequence.current) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (initialQuery.trim()) {
      search(initialQuery);
    }
  }, []);

  const handleLanguageChange = (value) => {
    setLanguage(value);
    if (query.trim()) {
      search(query, { language: value });
    }
  };

  const handleLevelChange = (value) => {
    setLevel(value);
    if (query.trim()) {
      search(query, { level: value });
    }
  };

  return (
    <div className="search-page">
      <main className="search-container">
        <div className="search-heading">
          <span>EXPLORE</span>
          <h1>Find your next lesson</h1>
          <p>
            Search any topic and discover educational videos
            matched to your learning level and language.
          </p>
        </div>

        <SearchBar onSearch={search} />

        <div className="search-filters">
          <LanguageSelector
            value={language}
            onChange={handleLanguageChange}
          />
          <LevelSelector
            value={level}
            onChange={handleLevelChange}
          />
        </div>

        <div className="results-heading">
          <div>
            <span>LEARNING RESOURCES</span>
            <h2>{query || "Recommended videos"}</h2>
            {query && (
              <small>
                {language.toUpperCase()} ·{" "}
                {level.charAt(0).toUpperCase() + level.slice(1)}
              </small>
            )}
          </div>

          {!loading && !error && query && (
            <small>{videos.length} videos</small>
          )}
        </div>

        {loading ? (
          <div className="video-empty">
            Finding the best learning videos...
          </div>
        ) : error ? (
          <div className="video-empty">{error}</div>
        ) : (
          <VideoGrid videos={videos} />
        )}
      </main>
    </div>
  );
}

export default Search;
