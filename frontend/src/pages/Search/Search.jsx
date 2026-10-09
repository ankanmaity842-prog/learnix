import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import SearchBar from "../../components/SearchBar/SearchBar";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";
import LevelSelector from "../../components/LevelSelector/LevelSelector";
import VideoGrid from "../../components/VideoGrid/VideoGrid";

import recommendationService from "../../services/recommendationService";

import "./Search.css";


const LEVEL_LIMITS = {
  beginner: 45,
  intermediate: 25,
  advanced: 12,
};


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

  const [channels, setChannels] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const search = async (
    value,
    selectedLanguage = language,
    selectedLevel = level,
  ) => {

    const cleanQuery =
      value.trim();

    if (!cleanQuery) {
      setQuery("");
      setVideos([]);
      setChannels([]);
      setError("");
      return;
    }

    setQuery(cleanQuery);
    setLoading(true);
    setError("");

    try {

      const data =
        await recommendationService.getForTopic(
          cleanQuery,
          {
            language:
              selectedLanguage,

            level:
              selectedLevel,

            limit:
              LEVEL_LIMITS[
                selectedLevel
              ],
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

      /*
       * Channel recommendations are
       * intentionally separate from the
       * video result.
       */
      try {
        const channelData =
          await recommendationService.getChannels(
            cleanQuery,
            {
              language:
                selectedLanguage,
            }
          );

        setChannels(
          Array.isArray(
            channelData?.channels
          )
            ? channelData.channels
            : []
        );
      } catch {
        setChannels([]);
      }

      if (
        !recommendations.length
      ) {
        setError(
          `No ${selectedLevel} educational videos found for "${cleanQuery}".`
        );
      }

    } catch (err) {

      console.error(
        "Search failed:",
        err.response?.data ||
          err
      );

      setVideos([]);

      setError(
        err.response?.data?.detail ||
          "Unable to find educational videos right now."
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
            Search any educational topic
            and Learnix will find popular,
            level-specific learning videos.
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


        {channels.length > 0 && (

          <section className="channel-recommendations">

            <div className="results-heading">

              <div>
                <span>
                  CHANNELS
                </span>

                <h2>
                  Recommended channels
                </h2>
              </div>

            </div>


            <div className="channel-list">

              {channels.map(
                (channel) => (

                  <a
                    key={
                      channel.channel_id
                    }
                    href={`https://www.youtube.com/channel/${channel.channel_id}`}
                    target="_blank"
                    rel="noreferrer"
                    className="channel-card"
                  >

                    {channel.thumbnail && (
                      <img
                        src={
                          channel.thumbnail
                        }
                        alt={
                          channel.channel
                        }
                      />
                    )}

                    <div>
                      <strong>
                        {
                          channel.channel
                        }
                      </strong>

                      <p>
                        {
                          channel.description
                        }
                      </p>
                    </div>

                  </a>

                )
              )}

            </div>

          </section>

        )}


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
            Finding popular{" "}
            {level} educational
            videos...
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
