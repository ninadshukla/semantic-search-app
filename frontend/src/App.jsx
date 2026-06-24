import { useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

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
        {results.map((result, index) => (
          <div key={index} className="card">
            {result}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;