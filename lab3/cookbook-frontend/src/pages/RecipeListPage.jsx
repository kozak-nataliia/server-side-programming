import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api";
const PAGE_SIZE = 12; // must match backend REST_FRAMEWORK["PAGE_SIZE"]

function RecipeListPage() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [count, setCount] = useState(0);
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);
  const { token, logout } = useAuth();

  async function loadPage(page) {
    try {
      setLoading(true);
      setError("");

      const url = `${API_BASE}/recipes/?page=${page}`;
      const res = await fetch(url, {
        headers: {
          Authorization: `Token ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (res.status === 401) {
        logout();
        throw new Error("Session expired. Please log in again.");
      }

      if (!res.ok) throw new Error("Failed to load recipes");

      const data = await res.json();

      // DRF pagination: {count,next,previous,results}
      if (data && Array.isArray(data.results)) {
        setRecipes(data.results);
        setCount(Number(data.count || 0));
        setNextUrl(data.next);
        setPrevUrl(data.previous);
      } else if (Array.isArray(data)) {
        // fallback if pagination is off (should not happen once backend is fixed)
        setRecipes(data);
        setCount(data.length);
        setNextUrl(null);
        setPrevUrl(null);
      } else {
        throw new Error("Unexpected API response format");
      }

      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e.message || "Error loading recipes");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!token) return;
    loadPage(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  if (loading) return <p>Loading recipes...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE));

  return (
    <section className="page">
      <h2 className="page-title">Recipe list</h2>
      <p className="text-muted">
        Click <strong>Details</strong> to view, edit or delete a recipe.
      </p>

      {recipes.length === 0 && (
        <p>No recipes yet. Be the first to add one! 🍰</p>
      )}

      <ul className="recipe-list">
        {recipes.map((r) => (
          <li key={r.id} className="recipe-item">
            <span className="recipe-item-title">{r.title}</span>
            <Link to={`/recipes/${r.id}`} className="link-secondary">
              Details
            </Link>
          </li>
        ))}
      </ul>

      {count > PAGE_SIZE && (
        <div className="pagination">
          <button
            type="button"
            className="pagination-btn"
            onClick={() => loadPage(currentPage - 1)}
            disabled={!prevUrl || currentPage === 1}
          >
            Prev
          </button>

          {Array.from({ length: totalPages }).map((_, index) => {
            const page = index + 1;
            return (
              <button
                key={page}
                type="button"
                className={
                  "pagination-btn" +
                  (page === currentPage ? " is-active" : "")
                }
                onClick={() => loadPage(page)}
              >
                {page}
              </button>
            );
          })}

          <button
            type="button"
            className="pagination-btn"
            onClick={() => loadPage(currentPage + 1)}
            disabled={!nextUrl || currentPage === totalPages}
          >
            Next
          </button>
        </div>
      )}

      <div className="back-link">
        <Link to="/recipes/new">+ Add new recipe</Link>
      </div>
    </section>
  );
}

export default RecipeListPage;
