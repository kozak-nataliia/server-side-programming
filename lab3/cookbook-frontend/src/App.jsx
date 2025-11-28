import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import "./App.css";
import RecipeListPage from "./pages/RecipeListPage.jsx";
import RecipeDetailPage from "./pages/RecipeDetailPage.jsx";
import RecipeFormPage from "./pages/RecipeFormPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";          // 🔹 додали
import ProtectedRoute from "./auth/ProtectedRoute.jsx"; // 🔹 додали
import { useAuth } from "./auth/AuthContext.jsx";       // 🔹 додали

function App() {
  const { token, logout } = useAuth(); // 🔹 знаємо, залогінений юзер чи ні

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 className="app-title">COOKBOOK</h1>
        <p className="app-subtitle">Best recipe website 💕</p>

        {/* навігація показується тільки коли є токен */}
        {token && (
          <nav className="app-nav">
            <NavLink
              to="/recipes"
              end
              className={({ isActive }) =>
                "nav-link " + (isActive ? "nav-link-active" : "")
              }
            >
              Recipe list
            </NavLink>

            <NavLink
              to="/recipes/new"
              className={({ isActive }) =>
                "nav-link " + (isActive ? "nav-link-active" : "")
              }
            >
              Add recipe
            </NavLink>

            <button className="nav-link nav-logout" onClick={logout}>
              Log out
            </button>
          </nav>
        )}
      </header>

      <main className="app-main">
        <Routes>
          {/* публічна сторінка логіну */}
          <Route path="/login" element={<LoginPage />} />

          {/* далі – все під авторизацією */}
          <Route
            path="/recipes"
            element={
              <ProtectedRoute>
                <RecipeListPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/recipes/new"
            element={
              <ProtectedRoute>
                <RecipeFormPage mode="create" />
              </ProtectedRoute>
            }
          />

          <Route
            path="/recipes/:id"
            element={
              <ProtectedRoute>
                <RecipeDetailPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/recipes/:id/edit"
            element={
              <ProtectedRoute>
                <RecipeFormPage mode="edit" />
              </ProtectedRoute>
            }
          />

          {/* все інше перекидаємо на список рецептів */}
          <Route path="*" element={<Navigate to="/recipes" />} />
        </Routes>
      </main>

      <footer className="app-footer">Made by ✨ Natalya ✨</footer>
    </div>
  );
}

export default App;
