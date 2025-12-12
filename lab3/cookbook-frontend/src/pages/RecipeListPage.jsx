import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api";
const RECIPES_PER_PAGE = 12;

function RecipeListPage() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const { token, logout } = useAuth();

  useEffect(() => {
    if (!token) return;

    async function load() {
      try {
        setLoading(true);
        setError("");
        const res = await fetch(`${API_BASE}/recipes/`, {
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
          throw new Error("Failed to load recipes");
        }

        const data = await res.json();
        setRecipes(data);
        setCurrentPage(1);
      } catch (e) {
        setError(e.message || "Error loading recipes");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [token, logout]);

  // keep current page in range when number of recipes changes
  useEffect(() => {
    const totalPages = Math.max(1, Math.ceil(recipes.length / RECIPES_PER_PAGE));
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [recipes, currentPage]);

  if (loading) return <p>Loading recipes...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  const totalPages = Math.max(1, Math.ceil(recipes.length / RECIPES_PER_PAGE));
  const startIndex = (currentPage - 1) * RECIPES_PER_PAGE;
  const visibleRecipes = recipes.slice(
    startIndex,
    startIndex + RECIPES_PER_PAGE
  );

  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handlePrev = () => {
    if (currentPage > 1) {
      handlePageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      handlePageChange(currentPage + 1);
    }
  };

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
        {visibleRecipes.map((r) => (
          <li key={r.id} className="recipe-item">
            <span className="recipe-item-title">{r.title}</span>
            <Link to={`/recipes/${r.id}`} className="link-secondary">
              Details
            </Link>
          </li>
        ))}
      </ul>

      {recipes.length > RECIPES_PER_PAGE && (
        <div className="pagination">
          <button
            type="button"
            className="pagination-btn"
            onClick={handlePrev}
            disabled={currentPage === 1}
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
                onClick={() => handlePageChange(page)}
              >
                {page}
              </button>
            );
          })}

          <button
            type="button"
            className="pagination-btn"
            onClick={handleNext}
            disabled={currentPage === totalPages}
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
