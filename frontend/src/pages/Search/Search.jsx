import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import SearchBar from "../../components/SearchBar/SearchBar";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";
import LevelSelector from "../../components/LevelSelector/LevelSelector";
import VideoGrid from "../../components/VideoGrid/VideoGrid";

import recommendationService from "../../services/recommendationService";
import "./Search.css";

const LEVEL_LIMITS = {
  beginner: 30,
  intermediate: 25,
  advanced: 12,
};

function Search() {
  const [params] = useSearchParams();
  const initialQuery = params.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [language, setLanguage] = useState("en");
  const [level, setLevel] = useState("beginner");
  const [videos, setVideos] = useState([]);
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const search = async (
    value,
    selectedLanguage = language,
    selectedLevel = level,
    channel = selectedChannel
  ) => {
    const cleanQuery = value.trim();

    if (!cleanQuery) {
      setQuery("");
      setVideos([]);
      setChannels([]);
      setSelectedChannel(null);
      setError("");
      return;
    }

    setQuery(cleanQuery);
    setLoading(true);
    setError("");

    try {
      const requestParams = {
        language: selectedLanguage,
        level: selectedLevel,
        limit: LEVEL_LIMITS[selectedLevel],
      };

      const data = channel
        ? await recommendationService.getForChannel(
            channel.channel_id,
            cleanQuery,
            requestParams
          )
        : await recommendationService.getForTopic(
            cleanQuery,
            requestParams
          );

      const recommendations = Array.isArray(data?.recommendations)
        ? data.recommendations
        : [];

      setVideos(recommendations);

      // Channel suggestions are shown only in topic-search mode.
      if (!channel) {
        try {
          const channelData =
            await recommendationService.getChannels(cleanQuery, {
              language: selectedLanguage,
            });

          setChannels(
            Array.isArray(channelData?.channels)
              ? channelData.channels
              : []
          );
        } catch {
          setChannels([]);
        }
      } else {
        setChannels([]);
      }

      if (!recommendations.length) {
        setError(
          `No eligible ${selectedLevel} videos found for "${cleanQuery}"` +
            (channel ? ` from ${channel.channel}.` : ".")
        );
      }
    } catch (err) {
      console.error("Search failed:", err.response?.data || err);
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
    if (initialQuery.trim()) {
      search(initialQuery, "en", "beginner", null);
    }
    // Initial URL query should run once on page mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLanguageChange = (value) => {
    setLanguage(value);
    if (query.trim()) {
      search(query, value, level, selectedChannel);
    }
  };

  const handleLevelChange = (value) => {
    setLevel(value);
    if (query.trim()) {
      search(query, language, value, selectedChannel);
    }
  };

  const handleChannelSelect = (channel) => {
    setSelectedChannel(channel);
    search(query, language, level, channel);
  };

  const clearSelectedChannel = () => {
    setSelectedChannel(null);
    search(query, language, level, null);
  };

  return (
    <div className="search-page">
      <main className="search-container">
        <div className="search-heading">
          <span>EXPLORE</span>
          <h1>Find your next lesson</h1>
          <p>
            Search educational topics or choose a channel to see
            level-specific learning videos.
          </p>
        </div>
       <SearchBar
        onSearch={(value) => {
        setSelectedChannel(null);
        search(value, language, level, null);
         }}
        />

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

        {selectedChannel && (
          <section className="selected-channel">
            <p>
              Showing videos only from{" "}
              <strong>{selectedChannel.channel}</strong>
            </p>
            <button type="button" onClick={clearSelectedChannel}>
              Back to topic results
            </button>
          </section>
        )}

        {!selectedChannel && channels.length > 0 && (
          <section className="channel-recommendations">
            <div className="results-heading">
              <div>
                <span>CHANNELS</span>
                <h2>Suggested channels</h2>
                <p>
                  Choose a channel to restrict video results to that creator.
                </p>
              </div>
            </div>

            <div className="channel-list">
              {channels.map((channel) => (
                <button
                  key={channel.channel_id}
                  type="button"
                  className="channel-card"
                  onClick={() => handleChannelSelect(channel)}
                >
                  {channel.thumbnail && (
                    <img
                      src={channel.thumbnail}
                      alt=""
                      loading="lazy"
                    />
                  )}

                  <div>
                    <strong>{channel.channel}</strong>
                    <p>{channel.description}</p>
                    {typeof channel.match_score === "number" && (
                      <small>
                        Name match:{" "}
                        {Math.round(channel.match_score * 100)}%
                      </small>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}

        <div className="results-heading">
          <div>
            <span>LEARNING RESOURCES</span>
            <h2>
              {selectedChannel
                ? selectedChannel.channel
                : query || "Recommended videos"}
            </h2>
          </div>

          {!loading && query && !error && (
            <small>
              {videos.length} {videos.length === 1 ? "video" : "videos"}
            </small>
          )}
        </div>

        {loading ? (
          <div className="video-empty">
            Finding popular {level} educational videos...
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
