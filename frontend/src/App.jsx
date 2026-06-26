import { useState } from "react";
import LoginPage from "./LoginPage";
import "./App.css";

function SearchApp() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [insight, setInsight] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [sliderValue, setSliderValue] = useState(0);
  const [minScore, setMinScore] = useState(0);

  const search = async () => {
    if (!query.trim()) return;

    setHasSearched(true);
    setLoading(true);
    setResults([]);
    setInsight("");

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      const searchResults = data.results || [];

      setResults(searchResults);

      if (searchResults.length > 0) {
        const insightResponse = await fetch("http://127.0.0.1:8000/insights", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
          query: query,
          snippets: searchResults.map((result) => result.snippet),
           }),
        });

        const insightData = await insightResponse.json();
        setInsight(insightData.insight || "");
      }
    } catch (error) {
      console.error(error);
      alert("Could not connect to backend.");
    } finally {
      setLoading(false);
    }
  }; 
  const filteredResults = results.filter((result) => result.score >= minScore);

  return (
    <div className="container">
      <h1>Semantic Search App</h1>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Ask something..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") search();
          }}
        />

        <button onClick={search} disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div> 
      <div className="filter-panel">
  <label>Minimum relevance: {sliderValue}%</label>
  <input
    type="range"
    min="0"
    max="100"
    value={sliderValue}
    onChange={(e) => setSliderValue(Number(e.target.value))}
    onMouseUp={() => setMinScore(sliderValue)}
    onTouchEnd={() => setMinScore(sliderValue)}
  />
</div>

      {loading && <div className="loading">🔍 Searching...</div>}

      {!loading &&
  insight &&
  filteredResults.length > 0 && (
    <div className="insight-box">
      <h2>AI Insight</h2>
      <p>{insight}</p>
    </div>
)}

      <div className="results">
        {!loading &&
  hasSearched &&
  filteredResults.length === 0 && (
    <div className="empty-state">No results found.</div>
)}

        {!loading &&
          filteredResults.map((result) => (
            <div className="result-card" key={result.id}>
              <h3>{result.title}</h3>
              <p className="score">Relevance: {result.score}%</p>
              <p>{result.snippet}</p>
            </div>
          ))}
      </div>
    </div>
  );
}

function App() {
  const [loggedIn, setLoggedIn] = useState(
    !!localStorage.getItem("token")
  );

  return loggedIn ? (
    <SearchApp />
  ) : (
    <LoginPage onLogin={() => setLoggedIn(true)} />
  );
}

export default App;