import "./ErrorMessage.css";

export default function ErrorMessage({
  message = "Something went wrong.",
  onRetry,
}) {
  return (
    <div
      className="error-message"
      role="alert"
    >
      <div className="error-icon">!</div>

      <div className="error-content">
        <h3>Unable to continue</h3>
        <p>{message}</p>

        {onRetry && (
          <button
            type="button"
            className="error-retry"
            onClick={onRetry}
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}