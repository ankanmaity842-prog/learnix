import "./LanguageSelector.css";

function LanguageSelector({
  value = "en",
  onChange,
}) {
  return (
    <select
      className="language-selector"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    >
      <option value="en">English</option>
      <option value="hi">Hindi</option>
      <option value="bn">Bengali</option>
    </select>
  );
}

export default LanguageSelector;