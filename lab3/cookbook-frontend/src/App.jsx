import { Routes, Route, NavLink, Navigate } from "react-router-dom";
import "./App.css";
import RecipeListPage from "./pages/RecipeListPage.jsx";
import RecipeDetailPage from "./pages/RecipeDetailPage.jsx";
import RecipeFormPage from "./pages/RecipeFormPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";         
import RegisterPage from "./pages/RegisterPage.jsx";
import ProtectedRoute from "./auth/ProtectedRoute.jsx"; 
import { useAuth } from "./auth/AuthContext.jsx";       
import MyFavoritesPage from "./pages/MyFavoritesPage.jsx";
import AnalyticsPage from "./pages/AnalyticsPage.jsx";

function App() {
  const { token, user, isAdmin, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1 className="app-title">COOKBOOK</h1>
        <p className="app-subtitle">Best recipe website 💕</p>

        {/* навігація показується тільки коли є токен */}
        {token && (
          <>
            {/* user badge in the top-right corner */}
            <div className="header-user" title={isAdmin ? "Admin" : "User"}>
              <span className="header-user-name">{user?.username}</span>
              <span className="header-user-role">{isAdmin ? "admin" : "user"}</span>
            </div>

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

              {isAdmin && (
                <NavLink
                  to="/recipes/new"
                  className={({ isActive }) =>
                    "nav-link " + (isActive ? "nav-link-active" : "")
                  }
                >
                  Add recipe
                </NavLink>
              )}

              <NavLink
                to="/favorites"
                className={({ isActive }) =>
                  "nav-link " + (isActive ? "nav-link-active" : "")
                }
              >
                My favorites
              </NavLink>

              <NavLink
                to="/analytics"
                className={({ isActive }) => "nav-link " + (isActive ? "nav-link-active" : "")}
              >
                Analytics
              </NavLink>

              <button className="nav-link nav-logout" onClick={logout}>
                Log out
              </button>
            </nav>
          </>
        )}
      </header>

      <main className="app-main">
        <Routes>
          {/* публічна сторінка логіну */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

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
              <ProtectedRoute requireAdmin={true}>
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
              <ProtectedRoute requireAdmin={true}>
                <RecipeFormPage mode="edit" />
              </ProtectedRoute>
            }
          />

          <Route
            path="/favorites"
            element={
              <ProtectedRoute>
                <MyFavoritesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            }
          />

          {/* все інше перекидаємо на список рецептів */}
          <Route path="*" element={<Navigate to={token ? "/recipes" : "/login"} />} />
        </Routes>
      </main>

      <footer className="app-footer">Made by ✨ Natalya ✨</footer>
    </div>
  );
}

export default App;
