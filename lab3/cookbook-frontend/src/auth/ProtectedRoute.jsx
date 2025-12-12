import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

// If requireAdmin=true, only staff users can access.
const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { token, isAdmin, initializing } = useAuth();

  // avoid flicker while profile is loading from saved token
  if (initializing) return null;

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/recipes" replace />;
  }

  return children;
};

export default ProtectedRoute;
