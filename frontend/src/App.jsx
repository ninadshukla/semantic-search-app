import { useState, useEffect } from "react";
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
  const [selectedSource, setSelectedSource] = useState("All Sources");
  const [history, setHistory] = useState([]);

  useEffect(() => {
  const loadHistory = async () => {
    const email = localStorage.getItem("email");

    if (!email) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/auth/history/${email}`
      );

      const data = await response.json();

      setHistory(data.history || []);
    } catch (error) {
      console.log(error);
    }
  };

  loadHistory();
}, []);
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
      const email = localStorage.getItem("email");

if (email && query.trim()) {
  await fetch("http://127.0.0.1:8000/auth/history", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      query: query,
    }),
  });
  setHistory((prev) => [query, ...prev]);
}

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
  const sourceFilteredResults =
  selectedSource === "All Sources"
    ? results
    : results.filter((result) => result.title === selectedSource);

const filteredResults = sourceFilteredResults.filter(
  (result) => result.score >= minScore
);

const sources = [
  "All Sources",
  ...new Set(results.map((result) => result.title)),
];

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

  {hasSearched && sources.length > 1 && (
    <select
      value={selectedSource}
      onChange={(e) => setSelectedSource(e.target.value)}
      className="source-select"
    >
      {sources.map((source) => (
        <option key={source} value={source}>
          {source}
        </option>
      ))}
    </select>
  )}

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
{history.length > 0 && (
  <div className="history-box">
    <h3>Recent Searches</h3>

    {history.slice(0, 5).map((item, index) => (
      <button
        key={index}
        onClick={() => setQuery(item)}
      >
        {item}
      </button>
    ))}
  </div>
)}

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
              <h3>Result #{result.id} — {result.title}</h3>
              <p className="score">Relevance: {result.score}%</p>
              <p>{result.snippet}</p> 
              {result.source && (
  <a
    href={result.source}
    target="_blank"
    rel="noreferrer"
    className="source-link"
  >
    View Source
  </a>
)}
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

  const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("email");
  setLoggedIn(false);
};

return loggedIn ? (
  <>
    <button className="logout-button" onClick={logout}>
      Logout
    </button>
    <SearchApp />
  </>
) : (
  <LoginPage onLogin={() => setLoggedIn(true)} />
);
}

export default App;