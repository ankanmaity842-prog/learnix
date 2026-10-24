import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";

import quizService from "../../services/quizService";
import "./VideoLearning.css";

function linkifyDescription(description, videoId) {
  const pattern =
    /https?:\/\/[^\s<>]+|(?:\b\d{1,2}:)?\b\d{1,2}:\d{2}\b/g;

  const parts = [];
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = pattern.exec(description)) !== null) {
    const value = match[0];
    const start = match.index;

    if (start > lastIndex) {
      parts.push(description.slice(lastIndex, start));
    }

    if (/^https?:\/\//i.test(value)) {
      // Keep punctuation outside the clickable URL.
      const url = value.replace(/[.,!?;:)]+$/, "");
      const trailing = value.slice(url.length);

      if (url) {
        parts.push(
          <a
            key={`url-${key++}`}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="youtube-description-link"
          >
            {url}
          </a>
        );
      }

      if (trailing) {
        parts.push(trailing);
      }
    } else {
      const seconds = value.split(":").reduce(
        (total, part) => total * 60 + Number(part),
        0
      );

      parts.push(
        <a
          key={`timestamp-${key++}`}
          href={`https://www.youtube.com/watch?v=${encodeURIComponent(
            videoId
          )}&t=${seconds}s`}
          target="_blank"
          rel="noopener noreferrer"
          className="youtube-description-link"
          aria-label={`Open video at ${value}`}
        >
          {value}
        </a>
      );
    }

    lastIndex = start + value.length;
  }

  if (lastIndex < description.length) {
    parts.push(description.slice(lastIndex));
  }

  return parts;
}

function YouTubeDescription({ description, videoId }) {
  const [expanded, setExpanded] = useState(false);

  if (!description?.trim()) {
    return null;
  }

  return (
    <section className="youtube-description">
      <div
        className={`youtube-description__text ${
          expanded ? "is-expanded" : "is-collapsed"
        }`}
      >
        {linkifyDescription(description, videoId)}
      </div>

      <button
        type="button"
        className="youtube-description__toggle"
        onClick={() => setExpanded((current) => !current)}
        aria-expanded={expanded}
      >
        {expanded ? "Show less" : "Show more"}
      </button>
    </section>
  );
}

function VideoLearning() {
  const location = useLocation();
  const navigate = useNavigate();
  const { videoId: routeVideoId } = useParams();

  const video = location.state?.video;

  const videoId = routeVideoId || video?.video_id || video?.id;

  const title = video?.title || "Learning Video";
  const channel = video?.channel || "Educational channel";
  const description = video?.description || "";
  const language = video?.language || "en";
  const difficulty = video?.difficulty || "Beginner";

  const [notes, setNotes] = useState("");
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");

  const handleGenerateQuiz = async () => {
    if (!videoId) {
      setQuizError(
        "Video information is missing. Return to search and open the lesson again."
      );
      return;
    }

    setQuizLoading(true);
    setQuizError("");

    try {
      const quiz = await quizService.generateForVideo(
        video,
        videoId,
        {
          language,
          content: notes.trim(),
          numberOfQuestions: 5,
          difficulty: "medium",
        }
      );

      if (
        !Array.isArray(quiz?.questions) ||
        quiz.questions.length === 0
      ) {
        throw new Error("No quiz questions were generated.");
      }

      navigate("/quiz", {
        state: {
          quiz,
          videoId,
          videoTitle: title,
        },
      });
    } catch (error) {
      setQuizError(
        error.response?.data?.detail ||
          error.message ||
          "Unable to generate the video quiz."
      );
    } finally {
      setQuizLoading(false);
    }
  };

  return (
    <main className="video-learning-page">
      <div className="learning-breadcrumb">
        <Link to="/search">Search</Link>
        <span>/</span>
        <span>Learning</span>
      </div>

      <section className="learning-layout">
        <div className="video-main">
          <div className="video-player">
            {videoId ? (
              <iframe
                src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(
                  videoId
                )}?rel=0&playsinline=1`}
                title={title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              />
            ) : (
              <div className="video-player-error" role="alert">
                Video information is unavailable. Return to search and
                select a lesson again.
              </div>
            )}
          </div>

          <div className="video-details">
            <span>RECOMMENDED LESSON</span>

            <h1>{title}</h1>

            <div className="video-meta">
              <span>{channel}</span>
              <span>{language.toUpperCase()}</span>
              <span>{difficulty}</span>
            </div>

            <YouTubeDescription
              description={description}
              videoId={videoId}
            />

            {videoId && (
              <a
                className="youtube-link"
                href={`https://www.youtube.com/watch?v=${encodeURIComponent(
                  videoId
                )}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Watch on YouTube ↗
              </a>
            )}
          </div>
        </div>

        <aside className="learning-sidebar">
          <span>LEARNING PATH</span>
          <h2>Your current path</h2>

          <div className="lesson-list">
            <div className="learning-lesson completed">
              <span>✓</span>
              <div>
                <strong>Explore the topic</strong>
                <small>Completed</small>
              </div>
            </div>

            <div className="learning-lesson active">
              <span>02</span>
              <div>
                <strong>{title}</strong>
                <small>In progress</small>
              </div>
            </div>

            <div className="learning-lesson">
              <span>03</span>
              <div>
                <strong>Review your knowledge</strong>
                <small>Upcoming</small>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section className="learning-tools">
        <Link to="/notes" state={{ video }}>
          <strong>Notes</strong>
          <span>Review learning notes</span>
        </Link>

        <Link to="/knowledge">
          <strong>Knowledge</strong>
          <span>Review your knowledge</span>
        </Link>
      </section>

      <section className="video-quiz-generator">
        <span>LESSON ASSESSMENT</span>
        <h2>Test what this video teaches</h2>

        <p>
          Learnix uses available captions to generate questions
          about the concepts explained in this lesson.
        </p>

        <label htmlFor="lesson-notes">
          Lesson notes (optional)
        </label>

        <textarea
          id="lesson-notes"
          rows={5}
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          placeholder="If captions are unavailable, paste your lesson notes here..."
        />

        {quizError && (
          <p role="alert" className="quiz-error">
            {quizError}
          </p>
        )}

        <button
          type="button"
          onClick={handleGenerateQuiz}
          disabled={quizLoading || !videoId}
        >
          {quizLoading
            ? "Generating lesson quiz..."
            : "Generate video quiz"}
        </button>
      </section>
    </main>
  );
}

export default VideoLearning;

