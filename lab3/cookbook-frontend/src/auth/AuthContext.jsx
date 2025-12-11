import { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext(null);
const API_BASE = "http://127.0.0.1:8000/api";

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);

  // one-time: read token from localStorage and load profile if possible
  useEffect(() => {
    const saved = localStorage.getItem("authToken");
    if (!saved) {
      setInitializing(false);
      return;
    }

    setToken(saved);

    fetch(`${API_BASE}/auth/me/`, {
      headers: {
        Authorization: `Token ${saved}`,
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to load profile");
        }
        return res.json();
      })
      .then((data) => {
        setUser(data);
      })
      .catch(() => {
        // token is bad → drop it
        localStorage.removeItem("authToken");
        setToken(null);
        setUser(null);
      })
      .finally(() => setInitializing(false));
  }, []);

  const login = (newToken) => {
    localStorage.setItem("authToken", newToken);
    setToken(newToken);

    // after login load profile
    fetch(`${API_BASE}/auth/me/`, {
      headers: {
        Authorization: `Token ${newToken}`,
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to load profile");
        }
        return res.json();
      })
      .then((data) => {
        setUser(data);
      })
      .catch(() => {
        setUser(null);
      });
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setToken(null);
    setUser(null);
  };

  const value = {
    token,
    user,
    initializing,
    isAuthenticated: Boolean(token),
    isAdmin: Boolean(user?.is_staff),
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }
  return ctx;
};
