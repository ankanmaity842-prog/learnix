
import { useNavigate } from "react-router-dom";
import DifficultyBadge from "../DifficultyBadge/DifficultyBadge";
import "./VideoCard.css";

function VideoCard({ video, onOpen }) {
  const navigate = useNavigate();

  const videoId = video?.video_id || video?.id;

  const title = video?.title || "Untitled lesson";
  const description =
    video?.description || "Open this lesson on YouTube to view its details.";

  const difficulty = [
    "beginner",
    "intermediate",
    "advanced",
  ].includes(String(video?.difficulty || "").toLowerCase())
    ? String(video.difficulty).toLowerCase()
    : "beginner";

  const youtubeUrl = videoId
    ? `https://www.youtube.com/watch?v=${encodeURIComponent(videoId)}`
    : null;

  const handleOpen = () => {
    if (onOpen) {
      onOpen(video);
      return;
    }

    if (!videoId) return;

    navigate(`/video/${videoId}`, {
      state: {
        video: {
          ...video,
          video_id: videoId,
          difficulty,
        },
      },
    });
  };

  const handleDescriptionClick = () => {
    if (youtubeUrl) {
      window.open(
        youtubeUrl,
        "_blank",
        "noopener,noreferrer"
      );
    }
  };

  return (
    <article className="video-card">
      <button
        type="button"
        className="video-thumbnail"
        onClick={handleOpen}
        aria-label={`Start learning: ${title}`}
      >
        <img
          src={
            video?.thumbnail ||
            (videoId
              ? `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`
              : "")
          }
          alt={title}
          loading="lazy"
        />

        <span className="video-duration">
          {video?.duration || "Lesson"}
        </span>
      </button>

      <div className="video-content">
        <h3>{title}</h3>

        <p className="video-channel">
          {video?.channel || "Educational channel"}
        </p>

        <div className="video-meta">
          <DifficultyBadge level={difficulty} />

          {video?.views ? (
            <span>
              {Number(video.views).toLocaleString()} views
            </span>
          ) : null}
        </div>

        <button
          type="button"
          className="video-description-link"
          onClick={handleDescriptionClick}
          disabled={!youtubeUrl}
          title="Open the original video on YouTube"
        >
          {description}
          <span className="description-action">
            Watch on YouTube ↗
          </span>
        </button>

        <button
          type="button"
          className="watch-button"
          onClick={handleOpen}
          disabled={!videoId}
        >
          Start learning
        </button>
      </div>
    </article>
  );
}

export default VideoCard;
