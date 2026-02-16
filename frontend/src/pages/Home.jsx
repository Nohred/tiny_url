import { useState } from "react";
import { shortenUrl } from "../services/api.js";

export default function Home() {
  const [longUrl, setLongUrl] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);

    try {
      const data = await shortenUrl(longUrl.trim());
      setResult(data);
    } catch (err) {
      setError(err.message || String(err));
    }
  }

  return (
    <div className="container">
      <h1>Tiny URL</h1>

      <form onSubmit={onSubmit} className="form">
        <input
          value={longUrl}
          onChange={(e) => setLongUrl(e.target.value)}
          placeholder="https://example.com/very/long/url"
        />
        <button type="submit">Shorten</button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <div>{result.message}</div>

          <div style={{ marginTop: 8 }}>
            Link:{" "}
            <a href={result.short_url} target="_blank" rel="noreferrer">
              {result.short_url}
            </a>
          </div>

          {result.code && <div className="muted">Code: {result.code}</div>}
          <div className="muted">Reduced: {String(result.reduced)}</div>
        </div>
      )}
    </div>
  );
}
