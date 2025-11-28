import { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';

const API_BASE = 'http://127.0.0.1:8000/api';
const CATEGORY_ENDPOINT = `${API_BASE}/recipe-categories/`;

function RecipeFormPage({ mode }) {
  const { id } = useParams();
  const navigate = useNavigate();

  const isEdit = mode === 'edit';

  const [title, setTitle] = useState('');
  const [instructions, setInstructions] = useState('');
  const [category, setCategory] = useState(''); // id категорії як string
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const [categories, setCategories] = useState([]);
  const [categoriesError, setCategoriesError] = useState('');
  const [categoriesLoading, setCategoriesLoading] = useState(true);

  // 1) Завантажуємо список категорій для селекту
  useEffect(() => {
    async function loadCategories() {
      try {
        setCategoriesLoading(true);
        const res = await fetch(CATEGORY_ENDPOINT);
        if (!res.ok) {
          throw new Error('Failed to load categories');
        }
        const data = await res.json();
        setCategories(data);
      } catch (e) {
        setCategoriesError(e.message || 'Error loading categories');
      } finally {
        setCategoriesLoading(false);
      }
    }

    loadCategories();
  }, []);

  // 2) Якщо редагування – завантажуємо рецепт
  useEffect(() => {
    if (!isEdit) return;

    async function loadRecipe() {
      try {
        const res = await fetch(`${API_BASE}/recipes/${id}/`);
        if (!res.ok) {
          throw new Error('Failed to load recipe for edit');
        }
        const data = await res.json();
        setTitle(data.title || '');
        setInstructions(data.instructions || '');
        setCategory(data.category ? String(data.category) : '');
      } catch (e) {
        setError(e.message || 'Error loading recipe');
      }
    }

    loadRecipe();
  }, [isEdit, id]);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError('');

    const body = {
      title,
      instructions,
      category: category ? Number(category) : null,
    };

    try {
      let url = `${API_BASE}/recipes/`;
      let method = 'POST';

      if (isEdit) {
        url = `${API_BASE}/recipes/${id}/`;
        method = 'PUT';
      }

      const res = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || 'Failed to save recipe');
      }

      // Після збереження повертаємося до списку
      navigate('/recipes');
    } catch (err) {
      setError(err.message || 'Error saving recipe');
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="page">
      <h2 className="page-title">
        {isEdit ? 'Edit recipe' : 'Create recipe'}
      </h2>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <form className="form" onSubmit={handleSubmit}>
        <div className="form-row">
          <label className="form-label" htmlFor="title">
            Title
          </label>
          <input
            id="title"
            className="form-input"
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Strawberry Cloud Cake"
          />
        </div>

        <div className="form-row">
          <label className="form-label" htmlFor="instructions">
            Instructions
          </label>
          <textarea
            id="instructions"
            className="form-textarea"
            required
            value={instructions}
            onChange={(e) => setInstructions(e.target.value)}
            placeholder="Write step-by-step magic here ✨"
          />
        </div>

        <div className="form-row">
          <label className="form-label" htmlFor="category">
            Category (FK to category table)
          </label>

          {/* селект замість numeric input */}
          <select
            id="category"
            className="form-input"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">
              {categoriesLoading ? 'Loading categories...' : 'Choose category'}
            </option>

            {!categoriesLoading &&
              categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name ?? `Category #${cat.id}`}
                </option>
              ))}
          </select>

          {categoriesError && (
            <p style={{ color: 'red', fontSize: '0.8rem' }}>
              {categoriesError}
            </p>
          )}

          <p className="text-muted">
            This links the recipe to an existing category record in the DB.
          </p>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : isEdit ? 'Save changes' : 'Create'}
          </button>

          <Link to="/recipes">
            <button type="button" className="btn btn-outline">
              Cancel
            </button>
          </Link>
        </div>
      </form>

      <div className="back-link">
        <Link to="/recipes">← Back to list</Link>
      </div>
    </section>
  );
}

export default RecipeFormPage;
