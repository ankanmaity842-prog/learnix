import { Link, useLocation } from "react-router-dom";
import "./VideoLearning.css";

function VideoLearning() {
  const location = useLocation();

  const video = location.state?.video;

  if (!video) {
    return (
      <main className="video-learning-page">
        <div className="learning-breadcrumb">
          <Link to="/search">Search</Link>
          <span>/</span>
          <span>Learning</span>
        </div>

        <section className="learning-empty">
          <span>LEARNING RESOURCE</span>

          <h1>No lesson selected</h1>

          <p>
            Choose a learning video from the search page
            to start your lesson.
          </p>

          <Link
            to="/search"
            className="back-search-button"
          >
            Browse learning videos
          </Link>
        </section>
      </main>
    );
  }

  const youtubeUrl =
    `https://www.youtube.com/watch?v=${video.video_id}`;

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
              src={`https://www.youtube.com/embed/${video.video_id}`}
              title={video.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>

          <div className="video-details">
            <span>RECOMMENDED LESSON</span>

            <h1>{video.title}</h1>

            <p>
              {video.description ||
                "Follow this lesson at your own pace and build your understanding step by step."}
            </p>

            <div className="video-meta">
              <span>
                {video.channel}
              </span>

              <span>
                {video.language?.toUpperCase() || "EN"}
              </span>

              <span>
                {video.difficulty || "Beginner"}
              </span>
            </div>

            <a
              href={youtubeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="youtube-link"
            >
              Watch on YouTube
            </a>
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
                <strong>
                  {video.title}
                </strong>

                <small>
                  In progress
                </small>
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