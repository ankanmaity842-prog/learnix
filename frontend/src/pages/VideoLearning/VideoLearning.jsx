import { Link } from "react-router-dom";
import "./VideoLearning.css";

function VideoLearning() {
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
            <div className="video-placeholder">
              <button className="play-button">▶</button>
            </div>
          </div>

          <div className="video-details">
            <span>RECOMMENDED LESSON</span>

            <h1>Selected learning resource</h1>

            <p>
              Follow the lesson at your own pace. Learnix uses your learning
              preferences and progress to help organize your experience.
            </p>

            <div className="video-meta">
              <span>Learning level</span>
              <span>Language</span>
              <span>Duration</span>
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
                <strong>Previous concept</strong>
                <small>Completed</small>
              </div>
            </div>

            <div className="learning-lesson active">
              <span>02</span>
              <div>
                <strong>Current lesson</strong>
                <small>In progress</small>
              </div>
            </div>

            <div className="learning-lesson">
              <span>03</span>
              <div>
                <strong>Next concept</strong>
                <small>Upcoming</small>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section className="learning-tools">
        <Link to="/notes">
          <strong>Notes</strong>
          <span>Review learning notes</span>
        </Link>

        <Link to="/quiz">
          <strong>Quiz</strong>
          <span>Test your understanding</span>
        </Link>

        <Link to="/knowledge">
          <strong>Knowledge</strong>
          <span>Review your knowledge</span>
        </Link>
      </section>
    </main>
  );
}

export default VideoLearning;