
import { useNavigate } from "react-router-dom";
import DifficultyBadge from "../DifficultyBadge/DifficultyBadge";
import "./VideoCard.css";

function VideoCard({ video, onOpen }) {
  const navigate = useNavigate();

  const videoId = video?.video_id || video?.id;
  const title = video?.title || "Untitled lesson";

  const difficulty = [
    "beginner",
    "intermediate",
    "advanced",
  ].includes(String(video?.difficulty || "").toLowerCase())
    ? String(video.difficulty).toLowerCase()
    : "beginner";

  const thumbnail =
    video?.thumbnail ||
    (videoId
      ? `https://i.ytimg.com/vi/${encodeURIComponent(videoId)}/hqdefault.jpg`
      : "");

  const handleOpen = () => {
    if (onOpen) {
      onOpen({
        ...video,
        video_id: videoId,
        difficulty,
      });
      return;
    }

    if (!videoId) return;

    navigate(`/video/${encodeURIComponent(videoId)}`, {
      state: {
        video: {
          ...video,
          video_id: videoId,
          difficulty,
        },
      },
    });
  };

  return (
    <article className="video-card">
      <button
        type="button"
        className="video-thumbnail"
        onClick={handleOpen}
        disabled={!videoId}
        aria-label={`Start learning: ${title}`}
      >
        {thumbnail && (
          <img
            src={thumbnail}
            alt={title}
            loading="lazy"
          />
        )}

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

          {video?.views != null && video.views !== "" && (
            <span>
              {Number(video.views).toLocaleString()} views
            </span>
          )}
        </div>

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


