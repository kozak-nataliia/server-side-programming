import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:8000/api';

function RecipeDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/recipes/${id}/`);
        if (!res.ok) {
          throw new Error('Failed to load recipe');
        }
        const data = await res.json();
        setRecipe(data);
      } catch (e) {
        setError(e.message || 'Error loading recipe');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  async function handleDelete(e) {
    e.preventDefault();
    const ok = window.confirm('Delete this recipe?');
    if (!ok) return;

    try {
      const res = await fetch(`${API_BASE}/recipes/${id}/`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        throw new Error('Failed to delete recipe');
      }

      navigate('/recipes');
    } catch (err) {
      alert(err.message || 'Error while deleting');
    }
  }

  if (loading) return <p>Loading recipe...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;
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
        <Link to={`/recipes/${recipe.id}`}>
          {/* просто, щоб ID був явно використаний */}
        </Link>

        <Link to={`/recipes/${recipe.id}/edit`}>
          <button type="button" className="btn btn-primary">
            Edit
          </button>
        </Link>

        {/* форма для видалення по ID на сторінці деталей */}
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
