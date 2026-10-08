import { Link, useLocation, useParams } from "react-router-dom";
import "./VideoLearning.css";

function VideoLearning() {
  const location = useLocation();
  const { videoId } = useParams();

  const video = location.state?.video;

  const title =
    video?.title || "Learning Video";

  const channel =
    video?.channel || "Educational channel";

  const description =
    video?.description ||
    "Follow this lesson at your own pace and build your understanding step by step.";

  const language =
    video?.language?.toUpperCase() || "EN";

  const difficulty =
    video?.difficulty || "Beginner";

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
              src={`https://www.youtube-nocookie.com/embed/${videoId}?rel=0&playsinline=1`}
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
              <span>{language}</span>
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