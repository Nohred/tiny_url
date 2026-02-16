const API_BASE = import.meta.env.VITE_API_BASE;

export async function shortenUrl(long_url) {
  const res = await fetch(`${API_BASE}/api/shorten`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ long_url }),
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

console.log("API_BASE =", import.meta.env.VITE_API_BASE);


