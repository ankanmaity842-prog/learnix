import DifficultyBadge from "../DifficultyBadge/DifficultyBadge";
import "./VideoCard.css";

function VideoCard({ video, onOpen }) {
  const videoUrl = `https://www.youtube.com/watch?v=${video.video_id}`;

  return (
    <article className="video-card">
      <div className="video-thumbnail">
        <img
          src={
            video.thumbnail ||
            `https://i.ytimg.com/vi/${video.video_id}/hqdefault.jpg`
          }
          alt={video.title}
          loading="lazy"
        />

        <span className="video-duration">
          {video.duration || "Lesson"}
        </span>
      </div>

      <div className="video-content">
        <h3>{video.title}</h3>

        <p className="video-channel">
          {video.channel || "Educational channel"}
        </p>

        <div className="video-meta">
          <DifficultyBadge
            level={video.difficulty || "beginner"}
          />

          {video.views ? (
            <span>
              {Number(video.views).toLocaleString()} views
            </span>
          ) : null}
        </div>

        <button
          className="watch-button"
          onClick={() => {
            if (onOpen) {
              onOpen(video);
            } else {
              window.open(
                videoUrl,
                "_blank",
                "noopener,noreferrer"
              );
            }
          }}
        >
          Start learning
        </button>
      </div>
    </article>
  );
}

export default VideoCard;