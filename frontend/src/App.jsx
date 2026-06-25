import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [insight, setInsight] = useState("");

  const search = async () => {
    if (!query.trim()) return;

    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();
      setResults(data.results);
      setInsight(data.insight);
    } catch (error) {
      console.error(error);
      alert("Could not connect to backend.");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Semantic Search App</h1>

      <div className="search-box">
        <input
          type="text"
          placeholder="Ask something..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        <button onClick={search}>
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div className="results">
  {results.length === 0 && !loading && (
    <p className="empty">Search results will appear here.</p>
  )}
{insight && (
  <div className="insight-box">
    <h2>AI Insight</h2>
    <p>{insight}</p>
  </div>
)}
  {results.map((result) => (
    <div className="result-card" key={result.id}>
      <h3>{result.title}</h3>
      <p>{result.snippet}</p>
    </div>
  ))}
</div>
    </div>
  );
}

export default App;