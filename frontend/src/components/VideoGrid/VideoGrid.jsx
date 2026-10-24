
import VideoCard from "../VideoCard/VideoCard";
import "./VideoGrid.css";

function VideoGrid({ videos = [], onOpen }) {
  if (!videos.length) {
    return (
      <div className="video-empty" role="status">
        No learning videos found. Try another topic or difficulty level.
      </div>
    );
  }

  const hasUnverifiedVideos = videos.some(
    (video) => video.level_verified === false
  );

  return (
    <section className="video-grid-section">
      {hasUnverifiedVideos && (
        <p className="video-verification-notice" role="note">
          Some videos match your topic, but their difficulty level
          could not be verified from the available title or description.
        </p>
      )}

      <div className="video-grid">
        {videos.map((video) => (
          <VideoCard
            key={video.video_id || video.id}
            video={video}
            onOpen={onOpen}
          />
        ))}
      </div>
    </section>
  );
}

export default VideoGrid;
