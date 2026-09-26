import "./DifficultyBadge.css";

function DifficultyBadge({ level = "medium" }) {
  return (
    <span
      className={`difficulty-badge difficulty-${level.toLowerCase()}`}
    >
      {level}
    </span>
  );
}

export default DifficultyBadge;