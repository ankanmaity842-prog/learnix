import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import SearchBar from "../../components/SearchBar/SearchBar";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";
import LevelSelector from "../../components/LevelSelector/LevelSelector";
import VideoGrid from "../../components/VideoGrid/VideoGrid";

import recommendationService from "../../services/recommendationService";

import "./Search.css";


function Search() {
  const [params] = useSearchParams();

  const initialQuery =
    params.get("q") || "";

  const [query, setQuery] =
    useState(initialQuery);

  const [language, setLanguage] =
    useState("en");

  const [level, setLevel] =
    useState("beginner");

  const [videos, setVideos] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const search = async (
    value,
    selectedLanguage = language,
    selectedLevel = level
  ) => {

    const cleanQuery =
      value.trim();

    if (!cleanQuery) {
      setQuery("");
      setVideos([]);
      setError("");
      return;
    }

    setQuery(cleanQuery);
    setLoading(true);
    setError("");

    try {

      const data =
        await recommendationService
          .getForTopic(
            cleanQuery,
            {
              language:
                selectedLanguage,

              level:
                selectedLevel,

              limit: 20,
            }
          );

      const recommendations =
        Array.isArray(
          data?.recommendations
        )
          ? data.recommendations
          : [];

      setVideos(
        recommendations
      );

      if (
        !recommendations.length
      ) {
        setError(
          `No educational ${selectedLevel} videos found for "${cleanQuery}".`
        );
      }

    } catch (err) {

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

      setLoading(false);

    }
  };


  useEffect(() => {

    if (
      initialQuery.trim()
    ) {
      search(
        initialQuery,
        "en",
        "beginner"
      );
    }

  }, []);


  const handleLanguageChange =
    (value) => {

      setLanguage(value);

      if (query.trim()) {
        search(
          query,
          value,
          level
        );
      }
    };


  const handleLevelChange =
    (value) => {

      setLevel(value);

      if (query.trim()) {
        search(
          query,
          language,
          value
        );
      }
    };


  return (
    <div className="search-page">

      <main className="search-container">

        <div className="search-heading">

          <span>
            EXPLORE
          </span>

          <h1>
            Find your next lesson
          </h1>

          <p>
            Search any topic and Learnix
            will find popular educational
            videos matched to your level.
          </p>

        </div>


        <SearchBar
          onSearch={search}
        />


        <div className="search-filters">

          <LanguageSelector
            value={language}
            onChange={
              handleLanguageChange
            }
          />

          <LevelSelector
            value={level}
            onChange={
              handleLevelChange
            }
          />

        </div>


        <div className="results-heading">

          <div>

            <span>
              LEARNING RESOURCES
            </span>

            <h2>
              {query ||
                "Recommended videos"}
            </h2>

          </div>


          {!loading &&
            query &&
            !error && (
              <small>
                {videos.length}{" "}
                {videos.length === 1
                  ? "video"
                  : "videos"}
              </small>
            )}

        </div>


        {loading ? (

          <div className="video-empty">
            Finding popular educational
            videos for{" "}
            <strong>
              {level}
            </strong>{" "}
            level...
          </div>

        ) : error ? (

          <div className="video-empty">
            {error}
          </div>

        ) : (

          <VideoGrid
            videos={videos}
          />

        )}

      </main>

    </div>
  );
}


export default Search;
