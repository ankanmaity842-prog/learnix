import { useState } from "react";
import "./SearchBar.css";

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");

  const submit = (event) => {
    event.preventDefault();

    if (!query.trim()) return;

    onSearch?.(query.trim());
  };

  return (
    <form className="search-bar" onSubmit={submit}>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="What do you want to learn?"
        aria-label="Search topic"
      />

      <button type="submit">
        Search
      </button>
    </form>
  );
}

export default SearchBar;