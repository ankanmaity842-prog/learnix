import DifficultyBadge from "../DifficultyBadge/DifficultyBadge";
import "./VideoCard.css";

function VideoCard({ video, onOpen }) {
  return (
    <article className="video-card">
      <div className="video-thumbnail">
        <img
          src={video.thumbnail}
          alt={video.title}
        />

        <span className="video-duration">
          {video.duration || "Video"}
        </span>
      </div>

      <div className="video-content">
        <h3>{video.title}</h3>

        <p className="video-channel">
          {video.channel}
        </p>

        <div className="video-meta">
          <DifficultyBadge
            level={video.difficulty || "beginner"}
          />

          <span>
            {video.views || 0} views
          </span>
        </div>

        <button
          className="watch-button"
          onClick={() => onOpen?.(video)}
        >
          Start learning
        </button>
      </div>
    </article>
  );
}

export default VideoCard;