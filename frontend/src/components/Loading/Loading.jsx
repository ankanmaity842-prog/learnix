import "./Loading.css";

export default function Loading({
  message = "Loading...",
  fullScreen = false,
}) {
  return (
    <div
      className={`loading-container ${
        fullScreen ? "loading-fullscreen" : ""
      }`}
      role="status"
      aria-live="polite"
    >
      <div className="loading-spinner" />
      <span>{message}</span>
    </div>
  );
}