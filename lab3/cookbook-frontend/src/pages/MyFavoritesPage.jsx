import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api";

function MyFavoritesPage() {
  const { token, logout } = useAuth();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;

    async function load() {
      try {
        setLoading(true);
        setError("");

        const res = await fetch(`${API_BASE}/me/favorites/`, {
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (res.status === 401) {
          logout();
          throw new Error("Session expired. Please log in again.");
        }

        if (!res.ok) {
          throw new Error("Failed to load favorites");
        }

        const data = await res.json();
        setFavorites(data);
      } catch (e) {
        setError(e.message || "Error loading favorites");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [token, logout]);

  if (!token) {
    return (
      <section className="page">
        <h2 className="page-title">My favorites</h2>
        <p>You need to log in to see your favorites.</p>
      </section>
    );
  }

  return (
    <section className="page">
      <h2 className="page-title">My favorites</h2>

      {loading && <p>Loading favorites...</p>}
      {error && <p className="form-error">{error}</p>}

      {!loading && favorites.length === 0 && (
        <p>You don't have any favorite recipes yet.</p>
      )}

      <ul className="recipe-list">
        {favorites.map((fav) => (
          <li key={fav.recipe_id} className="recipe-list-item">
            <div className="recipe-main">
              <strong>{fav.title}</strong>
              <div className="recipe-meta">
                Added:{" "}
                {fav.added_at
                  ? new Date(fav.added_at).toLocaleString()
                  : "unknown"}
              </div>
            </div>
            <div className="recipe-actions">
              <Link to={`/recipes/${fav.recipe_id}`} className="btn btn-secondary">
                Details
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default MyFavoritesPage;
