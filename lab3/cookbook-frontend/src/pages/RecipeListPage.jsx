import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:8000/api';

function RecipeListPage() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE}/recipes/`);
        if (!res.ok) {
          throw new Error('Failed to load recipes');
        }
        const data = await res.json();
        setRecipes(data);
      } catch (e) {
        setError(e.message || 'Error loading recipes');
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  if (loading) return <p>Loading recipes...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <section className="page">
      <h2 className="page-title">Recipe list</h2>
      <p className="text-muted">
        Click <strong>Details</strong> to view, edit or delete a recipe.
      </p>

      {recipes.length === 0 && <p>No recipes yet. Be the first to add one! 🍰</p>}

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

      <div className="back-link">
        <Link to="/recipes/new">+ Add new recipe</Link>
      </div>
    </section>
  );
}

export default RecipeListPage;
