
import { useEffect, useState, useCallback, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

import SearchBar from "../../components/SearchBar/SearchBar";
import LanguageSelector from "../../components/LanguageSelector/LanguageSelector";
import LevelSelector from "../../components/LevelSelector/LevelSelector";
import VideoGrid from "../../components/VideoGrid/VideoGrid";

import recommendationService from "../../services/recommendationService";
import api from "../../services/api";
import "./Search.css";

const LEVEL_LIMITS = {
  beginner: 30,
  intermediate: 25,
  advanced: 12,
};

function Search() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const initialQuery = params.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [language, setLanguage] = useState("en");
  const [level, setLevel] = useState("beginner");

  const [videos, setVideos] = useState([]);
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);

  const [recentSearches, setRecentSearches] = useState([]);
  const [recentVideos, setRecentVideos] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  // Only the newest search is allowed to update the visible results.
  const searchIdRef = useRef(0);

  const loadExploreHistory = useCallback(async () => {
    try {
      const response = await api.get("/learning/explore-history");

      setRecentSearches(
        Array.isArray(response.data?.recent_searches)
          ? response.data.recent_searches
          : []
      );

      setRecentVideos(
        Array.isArray(response.data?.recent_videos)
          ? response.data.recent_videos
          : []
      );
    } catch (err) {
      setRecentSearches([]);
      setRecentVideos([]);

      console.debug(
        "Explore history unavailable:",
        err.response?.status || err.message
      );
    }
  }, []);

  useEffect(() => {
    loadExploreHistory();
  }, [loadExploreHistory]);

  const search = async (
    value,
    selectedLanguage = language,
    selectedLevel = level,
    channel = selectedChannel,
    saveHistory = true
  ) => {
    const cleanQuery = String(value || "").trim();
    const currentSearchId = ++searchIdRef.current;

    if (!cleanQuery) {
      setQuery("");
      setVideos([]);
      setChannels([]);
      setSelectedChannel(null);
      setError("");
      setLoading(false);
      setHasSearched(false);
      return;
    }

    setQuery(cleanQuery);
    setLoading(true);
    setError("");
    setHasSearched(true);

    if (saveHistory && !channel) {
      try {
        await api.post("/learning/search-history", {
          topic: cleanQuery,
        });

        await loadExploreHistory();
      } catch (err) {
        console.debug(
          "Could not save search history:",
          err.response?.status || err.message
        );
      }
    }

    // A newer search may have started while history was being saved.
    if (currentSearchId !== searchIdRef.current) return;

    try {
      const requestParams = {
        language: selectedLanguage,
        level: selectedLevel,
        limit: LEVEL_LIMITS[selectedLevel] || 10,
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

      if (currentSearchId !== searchIdRef.current) return;

      const recommendations = Array.isArray(data?.recommendations)
        ? data.recommendations
        : [];

      const mappedVideos = recommendations
        .filter((video) => video && (video.video_id || video.id))
        .map((video) => ({
          ...video,
          video_id: String(video.video_id || video.id),
          topic: cleanQuery,
          language: video.language || selectedLanguage,
          difficulty: video.difficulty || selectedLevel,
          level_verified:
            video.level_verified === true ||
            video.level_match === "verified",
        }));

      setVideos(mappedVideos);

      if (!channel) {
        try {
          const channelData =
            await recommendationService.getChannels(cleanQuery, {
              language: selectedLanguage,
            });

          if (currentSearchId !== searchIdRef.current) return;

          setChannels(
            Array.isArray(channelData?.channels)
              ? channelData.channels
              : []
          );
        } catch (channelError) {
          if (currentSearchId !== searchIdRef.current) return;

          console.debug(
            "Channel suggestions unavailable:",
            channelError.message
          );
          setChannels([]);
        }
      } else {
        setChannels([]);
      }

      if (mappedVideos.length === 0) {
        setError(
          `No matching educational videos were found for "${cleanQuery}". ` +
            "Try a related topic or another language."
        );
      } else {
        setError("");
      }
    } catch (err) {
      if (currentSearchId !== searchIdRef.current) return;

      console.error(
        "Search failed:",
        err.response?.data || err
      );

      setVideos([]);
      setChannels([]);

      setError(
        err.response?.data?.detail ||
          "Unable to find educational videos right now. Please try again."
      );
    } finally {
      if (currentSearchId === searchIdRef.current) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (initialQuery.trim()) {
      search(initialQuery, "en", "beginner", null, true);
    }

    // Run the URL query once on mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLanguageChange = (value) => {
    setLanguage(value);

    if (query.trim()) {
      search(query, value, level, selectedChannel, false);
    }
  };

  const handleLevelChange = (value) => {
    setLevel(value);

    if (query.trim()) {
      search(query, language, value, selectedChannel, false);
    }
  };

  const handleChannelSelect = (channel) => {
    setSelectedChannel(channel);
    search(query, language, level, channel, false);
  };

  const clearSelectedChannel = () => {
    setSelectedChannel(null);
    search(query, language, level, null, false);
  };

  const handleRecentTopicClick = (topic) => {
    setSelectedChannel(null);
    search(topic, language, level, null, false);
  };

  const handleHistoryVideoOpen = (video) => {
    const videoId = video?.video_id || video?.id;
    if (!videoId) return;

    navigate(`/video/${videoId}`, {
      state: {
        video: {
          ...video,
          video_id: videoId,
        },
      },
    });
  };

  const handleSearch = (value) => {
    setSelectedChannel(null);
    search(value, language, level, null, true);
  };

  return (
    <div className="search-page">
      <main className="search-container">
        <div className="search-heading">
          <span>EXPLORE</span>
          <h1>Find your next lesson</h1>
          <p>
            Search educational topics or choose a channel to see
            recommended learning videos.
          </p>
        </div>

        {recentVideos.length > 0 && (
          <section className="explore-history-section">
            <div className="results-heading">
              <div>
                <span>YOUR LEARNING</span>
                <h2>Continue Watching</h2>
                <p>Return to a lesson you opened previously.</p>
              </div>
            </div>

            <VideoGrid
              videos={recentVideos}
              onOpen={handleHistoryVideoOpen}
            />
          </section>
        )}

        {recentSearches.length > 0 && (
          <section className="explore-history-section">
            <div className="results-heading">
              <div>
                <span>YOUR ACTIVITY</span>
                <h2>Recently Searched</h2>
                <p>Continue exploring a topic from your history.</p>
              </div>
            </div>

            <div className="recent-topic-list">
              {recentSearches.map((item) => (
                <button
                  key={item.topic}
                  type="button"
                  className="recent-topic-chip"
                  onClick={() => handleRecentTopicClick(item.topic)}
                >
                  {item.topic}
                </button>
              ))}
            </div>
          </section>
        )}

        <SearchBar onSearch={handleSearch} />

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

            <button
              type="button"
              onClick={clearSelectedChannel}
            >
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
                  Choose a channel to restrict results to that creator.
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

          {!loading && videos.length > 0 && (
            <small>
              {videos.length} {videos.length === 1 ? "video" : "videos"}
            </small>
          )}
        </div>

        {loading ? (
          <div className="video-empty" role="status">
            Finding {level} educational videos for "{query}"...
          </div>
        ) : error ? (
          <div className="video-empty" role="status">
            {error}
          </div>
        ) : videos.length > 0 ? (
          <>
            {videos.some((video) => video.level_verified === false) && (
              <p className="level-verification-note">
                Some videos match your topic, but their difficulty
                could not be verified from their titles or descriptions.
              </p>
            )}

            <VideoGrid videos={videos} />
          </>
        ) : hasSearched ? (
          <div className="video-empty" role="status">
            No matching educational videos were found. Try another topic
            or adjust your filters.
          </div>
        ) : null}
      </main>
    </div>
  );
}

export default Search;


