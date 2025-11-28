// src/App.jsx
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import './App.css';
import RecipeListPage from './pages/RecipeListPage.jsx';
import RecipeDetailPage from './pages/RecipeDetailPage.jsx';
import RecipeFormPage from './pages/RecipeFormPage.jsx';

function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 className="app-title">
          COOKBOOK 
        </h1>
        <p className="app-subtitle">
          Best recipe website 💕
        </p>

        <nav className="app-nav">
          <NavLink
            to="/recipes"
            end         
            className={({ isActive }) =>
              'nav-link ' + (isActive ? 'nav-link-active' : '')
            }
          >
            Recipe list
          </NavLink>

          <NavLink
            to="/recipes/new"
            className={({ isActive }) =>
              'nav-link ' + (isActive ? 'nav-link-active' : '')
            }
          >
            Add recipe
          </NavLink>
        </nav>

      </header>

      <main className="app-main">
        <Routes>
          <Route path="/recipes" element={<RecipeListPage />} />
          <Route path="/recipes/new" element={<RecipeFormPage mode="create" />} />
          <Route path="/recipes/:id" element={<RecipeDetailPage />} />
          <Route path="/recipes/:id/edit" element={<RecipeFormPage mode="edit" />} />
          <Route path="*" element={<Navigate to="/recipes" />} />
        </Routes>
      </main>

      <footer className="app-footer">
        Made by ✨ Natalya ✨
      </footer>
    </div>
  );
}

export default App;
