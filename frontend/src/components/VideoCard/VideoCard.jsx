import { useNavigate } from "react-router-dom";
import DifficultyBadge from "../DifficultyBadge/DifficultyBadge";
import "./VideoCard.css";

function VideoCard({ video, onOpen }) {
  const navigate = useNavigate();

  const handleOpen = () => {
    if (onOpen) {
      onOpen(video);
      return;
    }

    navigate(`/video/${video.video_id}`, {
      state: { video },
    });
  };

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
          onClick={handleOpen}
        >
          Start learning
        </button>
      </div>
    </article>
  );
}

export default VideoCard;