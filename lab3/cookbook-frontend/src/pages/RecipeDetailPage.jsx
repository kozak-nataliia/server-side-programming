import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api";

function RecipeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token, logout } = useAuth();

  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;

    async function load() {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/recipes/${id}/`, {
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
          throw new Error("Failed to load recipe");
        }
        const data = await res.json();
        setRecipe(data);
      } catch (e) {
        setError(e.message || "Error loading recipe");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id, token, logout]);

  async function handleDelete(e) {
    e.preventDefault();
    const ok = window.confirm("Delete this recipe?");
    if (!ok) return;

    try {
      const res = await fetch(`${API_BASE}/recipes/${id}/`, {
        method: "DELETE",
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
        throw new Error("Failed to delete recipe");
      }

      navigate("/recipes");
    } catch (err) {
      alert(err.message || "Error while deleting");
    }
  }

  if (loading) return <p>Loading recipe...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!recipe) return <p>Recipe not found.</p>;

  return (
    <section className="page">
      <h2 className="page-title">Recipe details</h2>

      <div className="detail-grid">
        <div>
          <div className="detail-label">Title</div>
          <div className="detail-value">{recipe.title}</div>
        </div>

        <div>
          <div className="detail-label">Instructions</div>
          <div className="detail-value">{recipe.instructions}</div>
        </div>

        <div>
          <div className="detail-label">Category ID (FK)</div>
          <div className="detail-value">{recipe.category}</div>
        </div>

        <div>
          <div className="detail-label">Created at</div>
          <div className="detail-value">{recipe.created_at}</div>
        </div>

        <div>
          <div className="detail-label">Updated at</div>
          <div className="detail-value">{recipe.updated_at}</div>
        </div>
      </div>

      <div className="detail-actions">
        <Link to={`/recipes/${recipe.id}`}>{/* just to use id */}</Link>

        <Link to={`/recipes/${recipe.id}/edit`}>
          <button type="button" className="btn btn-primary">
            Edit
          </button>
        </Link>

        <form onSubmit={handleDelete}>
          <input type="hidden" name="recipeId" value={recipe.id} />
          <button type="submit" className="btn btn-danger">
            Delete
          </button>
        </form>
      </div>

      <div className="back-link">
        <Link to="/recipes">← Back to list</Link>
      </div>
    </section>
  );
}

export default RecipeDetailPage;
