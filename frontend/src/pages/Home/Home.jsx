import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./Home.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const defaultTopics = [
  "Python",
  "React",
  "Biology",
  "Physics",
  "Machine Learning",
];

const features = [
  {
    number: "01",
    title: "Search any topic",
    description:
      "Enter a subject you want to understand and discover educational videos collected from YouTube.",
  },
  {
    number: "02",
    title: "Find clearer explanations",
    description:
      "Learnix evaluates educational content using topic relevance, transcript simplicity, visual complexity and other learning signals.",
  },
  {
    number: "03",
    title: "Build knowledge progressively",
    description:
      "Use prerequisites, knowledge gaps and learning paths to understand what to study before moving forward.",
  },
];

const learningSteps = [
  {
    number: "01",
    title: "Choose a topic",
    text: "Search for anything from Python and physics to biology, economics or a topic you have never studied before.",
  },
  {
    number: "02",
    title: "Discover resources",
    text: "Learnix searches educational videos and ranks them around relevance, simplicity and your selected level.",
  },
  {
    number: "03",
    title: "Keep learning",
    text: "Start sessions, complete videos and build a knowledge profile as you learn.",
  },
];

function formatDuration(seconds) {
  const value = Number(seconds);

  if (!value || value <= 0) {
    return "Video";
  }

  const minutes = Math.floor(value / 60);

  if (minutes < 60) {
    return `${minutes} min`;
  }

  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;

  return remainingMinutes
    ? `${hours}h ${remainingMinutes}m`
    : `${hours}h`;
}

function getVideoId(video) {
  return (
    video?.video_id ||
    video?.youtube_id ||
    video?.id ||
    null
  );
}

function getVideoTitle(video) {
  return (
    video?.title ||
    "Educational video"
  );
}

function getVideoThumbnail(video) {
  if (video?.thumbnail) {
    return video.thumbnail;
  }

  const id = getVideoId(video);

  if (id) {
    return `https://i.ytimg.com/vi/${id}/mqdefault.jpg`;
  }

  return "";
}

function Home() {
  const [recommendations, setRecommendations] = useState([]);
  const [recommendedTopic, setRecommendedTopic] =
    useState("Python");

  const [loadingRecommendations, setLoadingRecommendations] =
    useState(true);

  useEffect(() => {
    let mounted = true;

    async function loadPublicRecommendations() {
      try {
        setLoadingRecommendations(true);

        const response = await fetch(
          `${API_URL}/recommendations/for-topic/Python?language=en&level=beginner&limit=3`
        );

        if (!response.ok) {
          throw new Error(
            `Request failed: ${response.status}`
          );
        }

        const data = await response.json();

        if (!mounted) {
          return;
        }

        setRecommendedTopic(
          data?.topic || "Python"
        );

        setRecommendations(
          Array.isArray(data?.recommendations)
            ? data.recommendations.slice(0, 3)
            : []
        );
      } catch (error) {
        console.error(
          "Unable to load home recommendations:",
          error
        );

        if (mounted) {
          setRecommendations([]);
        }
      } finally {
        if (mounted) {
          setLoadingRecommendations(false);
        }
      }
    }

    loadPublicRecommendations();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <main className="home-page">

      {/* =====================================================
          HERO
      ===================================================== */}

      <section className="home-hero">
        <div className="home-hero-content">

          <span className="home-eyebrow">
            PERSONALIZED LEARNING PLATFORM
          </span>

          <h1>
            Learn something
            <br />
            <span>worth knowing.</span>
          </h1>

          <p>
            Learnix helps you discover understandable
            educational content, build knowledge from the
            fundamentals and turn any topic into a structured
            learning journey.
          </p>

          <div className="home-search-preview">
            <div className="search-icon">
              ⌕
            </div>

            <span>
              Search Python, biology, physics, React...
            </span>

            <Link to="/search">
              Explore
            </Link>
          </div>

          <div className="home-topic-list">
            <span>Popular topics:</span>

            {defaultTopics.map((topic) => (
              <Link
                key={topic}
                to={`/search?q=${encodeURIComponent(
                  topic
                )}`}
              >
                {topic}
              </Link>
            ))}
          </div>

          <div className="home-actions">
            <Link
              to="/search"
              className="primary-button"
            >
              Start learning
            </Link>

            <Link
              to="/register"
              className="secondary-button"
            >
              Create free account
            </Link>
          </div>

        </div>


        {/* ===================================================
            REAL DATA PREVIEW
        =================================================== */}

        <div className="home-visual">
          <div className="learning-preview">

            <div className="preview-window-bar">
              <div className="preview-dots">
                <span />
                <span />
                <span />
              </div>

              <span className="preview-window-title">
                Learnix
              </span>
            </div>

            <div className="preview-content">

              <div className="preview-welcome">
                <div>
                  <span>
                    DISCOVER EDUCATIONAL CONTENT
                  </span>

                  <h3>
                    Recommended for learning
                  </h3>
                </div>

                <div className="preview-user">
                  L
                </div>
              </div>


              {/* Topic */}

              <div className="preview-topic">

                <div className="preview-topic-image">
                  <span>
                    {recommendedTopic
                      .slice(0, 2)
                      .toUpperCase()}
                  </span>
                </div>

                <div className="preview-topic-info">

                  <span className="preview-label">
                    FEATURED TOPIC
                  </span>

                  <strong>
                    {recommendedTopic}
                  </strong>

                  <small>
                    Beginner · AI-ranked resources
                  </small>

                </div>

                <span className="preview-topic-arrow">
                  →
                </span>

              </div>


              {/* Recommendation heading */}

              <div className="preview-section-heading">
                <span>
                  RECOMMENDED VIDEOS
                </span>

                <Link
                  to={`/search?q=${encodeURIComponent(
                    recommendedTopic
                  )}`}
                >
                  View all
                </Link>
              </div>


              {loadingRecommendations ? (
                <div className="preview-loading">
                  Finding educational resources...
                </div>
              ) : recommendations.length === 0 ? (
                <div className="preview-empty">
                  <strong>
                    Explore your first topic
                  </strong>

                  <span>
                    Search Learnix to discover
                    educational videos.
                  </span>
                </div>
              ) : (
                recommendations.map(
                  (video, index) => {
                    const videoId =
                      getVideoId(video);

                    const title =
                      getVideoTitle(video);

                    return (
                      <div
                        className="preview-video"
                        key={
                          videoId ||
                          `${title}-${index}`
                        }
                      >

                        <div className="preview-video-thumb">
                          {getVideoThumbnail(
                            video
                          ) ? (
                            <img
                              src={getVideoThumbnail(
                                video
                              )}
                              alt=""
                            />
                          ) : (
                            <span>▶</span>
                          )}

                          <span className="preview-play">
                            ▶
                          </span>
                        </div>

                        <div className="preview-video-info">

                          <strong>
                            {title}
                          </strong>

                          <span>
                            {video?.channel ||
                              video?.channel_name ||
                              "Educational resource"}
                          </span>

                          <small>
                            {video?.difficulty_level ||
                              video?.difficulty ||
                              "Beginner"}{" "}
                            ·{" "}
                            {formatDuration(
                              video?.duration_seconds
                            )}
                          </small>

                        </div>

                      </div>
                    );
                  }
                )
              )}

            </div>
          </div>
        </div>
      </section>


      {/* =====================================================
          VALUE STRIP
      ===================================================== */}

      <section className="home-value-strip">

        <div>
          <strong>
            YouTube-powered discovery
          </strong>

          <span>
            Educational resources collected from
            real video content
          </span>
        </div>

        <div>
          <strong>
            AI-assisted recommendations
          </strong>

          <span>
            Topics and resources analyzed around
            your learning needs
          </span>
        </div>

        <div>
          <strong>
            Knowledge-aware learning
          </strong>

          <span>
            Prerequisites, gaps and learning paths
            help organize what comes next
          </span>
        </div>

      </section>


      {/* =====================================================
          WHY LEARNIX
      ===================================================== */}

      <section className="home-section">

        <div className="section-heading">

          <span>
            WHY LEARNIX
          </span>

          <h2>
            Search less.
            <br />
            Understand more.
          </h2>

          <p>
            Finding educational videos is easy.
            Finding the right explanation, understanding
            what to learn first and knowing what comes
            next is harder. Learnix brings those pieces
            together.
          </p>

        </div>


        <div className="feature-grid">

          {features.map((feature) => (
            <article
              className="feature-card"
              key={feature.number}
            >

              <span className="feature-number">
                {feature.number}
              </span>

              <div className="feature-icon">
                {feature.number === "01" && "⌕"}
                {feature.number === "02" && "◇"}
                {feature.number === "03" && "↗"}
              </div>

              <h3>
                {feature.title}
              </h3>

              <p>
                {feature.description}
              </p>

            </article>
          ))}

        </div>

      </section>


      {/* =====================================================
          HOW IT WORKS
      ===================================================== */}

      <section className="learning-flow-section">

        <div className="learning-flow-inner">

          <div className="section-heading">

            <span>
              HOW IT WORKS
            </span>

            <h2>
              From curiosity to
              <br />
              real understanding.
            </h2>

            <p>
              Learnix turns a simple search into a more
              structured learning experience.
            </p>

          </div>


          <div className="learning-flow">

            {learningSteps.map(
              (step, index) => (
                <div
                  className="learning-step"
                  key={step.number}
                >

                  <div className="step-number">
                    {step.number}
                  </div>

                  <div className="step-content">

                    <h3>
                      {step.title}
                    </h3>

                    <p>
                      {step.text}
                    </p>

                  </div>

                  {index !==
                    learningSteps.length - 1 && (
                    <div className="step-line" />
                  )}

                </div>
              )
            )}

          </div>

        </div>

      </section>


      {/* =====================================================
          REAL RECOMMENDATION PREVIEW
      ===================================================== */}

      <section className="home-section learning-path-section">

        <div className="learning-path-preview">

          <div className="learning-path-copy">

            <span>
              LEARNING INTELLIGENCE
            </span>

            <h2>
              Know what to learn next.
            </h2>

            <p>
              Learnix can use topic classification,
              prerequisites, knowledge gaps and
              learning history to move beyond a
              simple video search.
            </p>

            <Link
              to="/search"
              className="secondary-button"
            >
              Explore a topic
            </Link>

          </div>


          <div className="path-map">

            <div className="path-node completed">
              <span>01</span>
              <strong>
                Fundamentals
              </strong>
              <small>
                Build the basics
              </small>
            </div>

            <div className="path-connector" />

            <div className="path-node active">
              <span>02</span>
              <strong>
                Core concepts
              </strong>
              <small>
                Deepen understanding
              </small>
            </div>

            <div className="path-connector" />

            <div className="path-node">
              <span>03</span>
              <strong>
                Practice
              </strong>
              <small>
                Apply what you learned
              </small>
            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          FINAL CTA
      ===================================================== */}

      <section className="home-cta">

        <div>

          <span>
            START LEARNING
          </span>

          <h2>
            Your next topic is only
            <br />
            a search away.
          </h2>

          <p>
            Search a subject, discover educational
            resources and start building your own
            learning history with Learnix.
          </p>

        </div>

        <Link
          to="/search"
          className="primary-button"
        >
          Explore Learnix
        </Link>

      </section>

    </main>
  );
}

export default Home;