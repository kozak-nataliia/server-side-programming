import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const API_BASE = "http://127.0.0.1:8000/api";

function RecipeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token, user, logout } = useAuth();

  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [comments, setComments] = useState([]);
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [commentsError, setCommentsError] = useState("");
  const [newCommentText, setNewCommentText] = useState("");
  const [newCommentRating, setNewCommentRating] = useState("");

  const [favorite, setFavorite] = useState(null); // null = unknown, true/false = state
  const [favLoading, setFavLoading] = useState(false);
  const [favError, setFavError] = useState("");

  // load recipe itself (still behind auth, like before)
  useEffect(() => {
    if (!token) return;

    async function load() {
      try {
        setLoading(true);
        setError("");
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

  // load comments (public) + favorite state (for logged-in user)
  useEffect(() => {
    async function loadExtras() {
      // comments
      try {
        setCommentsLoading(true);
        setCommentsError("");
        const res = await fetch(`${API_BASE}/recipes/${id}/comments/`);
        if (!res.ok) {
          throw new Error("Failed to load comments");
        }
        const data = await res.json();
        setComments(data);
      } catch (e) {
        setCommentsError(e.message || "Error loading comments");
      } finally {
        setCommentsLoading(false);
      }

      // favorite state for this user
      if (!token) {
        setFavorite(null);
        return;
      }

      try {
        setFavError("");
        const favRes = await fetch(`${API_BASE}/me/favorites/`, {
          headers: {
            Authorization: `Token ${token}`,
            "Content-Type": "application/json",
          },
        });

        if (favRes.status === 401) {
          logout();
          throw new Error("Session expired. Please log in again.");
        }

        if (!favRes.ok) {
          throw new Error("Failed to load favorites");
        }

        const favData = await favRes.json();
        const isFav = favData.some(
          (item) => String(item.recipe_id) === String(id)
        );
        setFavorite(isFav);
      } catch (e) {
        setFavError(e.message || "Error loading favorites");
      }
    }

    loadExtras();
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

  async function handleToggleFavorite() {
    if (!token) return;
    try {
      setFavLoading(true);
      setFavError("");

      const res = await fetch(`${API_BASE}/recipes/${id}/favorite/`, {
        method: "POST",
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
        throw new Error("Failed to update favorite");
      }

      const data = await res.json();
      setFavorite(Boolean(data.favorite));
    } catch (e) {
      setFavError(e.message || "Error updating favorite");
    } finally {
      setFavLoading(false);
    }
  }

  async function handleAddComment(e) {
    e.preventDefault();
    if (!token) return;

    try {
      setCommentsError("");
      const res = await fetch(`${API_BASE}/recipes/${id}/comments/`, {
        method: "POST",
        headers: {
          Authorization: `Token ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: newCommentText,
          rating: newCommentRating ? Number(newCommentRating) : null,
        }),
      });

      if (res.status === 401) {
        logout();
        throw new Error("Session expired. Please log in again.");
      }

      if (!res.ok) {
        throw new Error("Failed to add comment");
      }

      const data = await res.json();
      setComments((prev) => [data, ...prev]); // new comment first
      setNewCommentText("");
      setNewCommentRating("");
    } catch (e) {
      setCommentsError(e.message || "Error adding comment");
    }
  }

  async function handleDeleteComment(commentId) {
    if (!token) return;
    const ok = window.confirm("Delete this comment?");
    if (!ok) return;

    try {
      const res = await fetch(`${API_BASE}/comments/${commentId}/`, {
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

      if (res.status !== 204 && !res.ok) {
        throw new Error("Failed to delete comment");
      }

      setComments((prev) => prev.filter((c) => c.id !== commentId));
    } catch (e) {
      setCommentsError(e.message || "Error deleting comment");
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
          <div className="detail-label">Category</div>
          <div className="detail-value">
            {recipe.category_name ?? recipe.category ?? "—"}
          </div>
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

      <div className="favorite-section">
        {token ? (
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleToggleFavorite}
            disabled={favLoading}
          >
            {favorite ? "★ In favorites" : "☆ Add to favorites"}
          </button>
        ) : (
          <p className="muted-text">Log in to save this recipe to favorites.</p>
        )}
        {favError && <p className="form-error">{favError}</p>}
      </div>

      <section className="comments-section">
        <h3>Comments</h3>

        {commentsLoading && <p>Loading comments...</p>}
        {commentsError && <p className="form-error">{commentsError}</p>}

        {!commentsLoading && comments.length === 0 && (
          <p>No comments yet.</p>
        )}

        <ul className="comment-list">
          {comments.map((c) => (
            <li key={c.id} className="comment-item">
              <div className="comment-header">
                <strong>{c.user}</strong>
                {c.rating != null && (
                  <span className="comment-rating">Rating: {c.rating}/5</span>
                )}
                <span className="comment-date">
                  {c.created_at
                    ? new Date(c.created_at).toLocaleString()
                    : ""}
                </span>
              </div>
              <p className="comment-text">{c.text}</p>
              {user && (user.username === c.user || user.is_staff) && (
                <button
                  type="button"
                  className="btn btn-link btn-sm"
                  onClick={() => handleDeleteComment(c.id)}
                >
                  Delete
                </button>
              )}
            </li>
          ))}
        </ul>

        {token ? (
          <form onSubmit={handleAddComment} className="comment-form">
            <div className="form-group">
              <label htmlFor="comment-text">Add a comment</label>
              <textarea
                id="comment-text"
                className="form-input"
                value={newCommentText}
                onChange={(e) => setNewCommentText(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="comment-rating">Rating (optional)</label>
              <select
                id="comment-rating"
                className="form-input"
                value={newCommentRating}
                onChange={(e) => setNewCommentRating(e.target.value)}
              >
                <option value="">No rating</option>
                <option value="1">1 – Bad</option>
                <option value="2">2</option>
                <option value="3">3 – Okay</option>
                <option value="4">4</option>
                <option value="5">5 – Great</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary">
              Submit comment
            </button>
          </form>
        ) : (
          <p className="muted-text">Log in to write a comment.</p>
        )}
      </section>

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
