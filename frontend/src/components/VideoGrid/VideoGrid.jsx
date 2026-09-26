import VideoCard from "../VideoCard/VideoCard";
import "./VideoGrid.css";

function VideoGrid({
  videos = [],
  onOpen,
}) {
  if (!videos.length) {
    return (
      <div className="video-empty">
        No learning videos found.
      </div>
    );
  }

  return (
    <div className="video-grid">
      {videos.map((video) => (
        <VideoCard
          key={video.video_id}
          video={video}
          onOpen={onOpen}
        />
      ))}
    </div>
  );
}

export default VideoGrid;