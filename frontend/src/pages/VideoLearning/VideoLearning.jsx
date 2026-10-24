
import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";

import quizService from "../../services/quizService";
import "./VideoLearning.css";

function VideoLearning() {
  const location = useLocation();
  const navigate = useNavigate();
  const { videoId } = useParams();

  const video = location.state?.video;

  const title = video?.title || "Learning Video";
  const channel = video?.channel || "Educational channel";
  const description = video?.description || "";
  const language = video?.language || "en";
  const difficulty = video?.difficulty || "Beginner";

  const [notes, setNotes] = useState("");
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizError, setQuizError] = useState("");

  const handleGenerateQuiz = async () => {
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
        !Array.isArray(quiz.questions) ||
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
            <iframe
              src={`https://www.youtube-nocookie.com/embed/${encodeURIComponent(
                videoId
              )}?rel=0&playsinline=1`}
              title={title}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>

          <div className="video-details">
            <span>RECOMMENDED LESSON</span>
            <h1>{title}</h1>
            <p>{description}</p>

            <div className="video-meta">
              <span>{channel}</span>
              <span>{language.toUpperCase()}</span>
              <span>{difficulty}</span>
            </div>
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
          disabled={quizLoading}
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
