import "./LevelSelector.css";

function LevelSelector({
  value = "beginner",
  onChange,
}) {
  return (
    <select
      className="level-selector"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    >
      <option value="beginner">Beginner</option>
      <option value="intermediate">Intermediate</option>
      <option value="advanced">Advanced</option>
    </select>
  );
}

export default LevelSelector;