
import {
  createContext,
  useCallback,
  useEffect,
  useState,
} from "react";

import authService from "../services/authService";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem("learnix_token");

    if (!token) {
      setUser(null);
      setLoading(false);
      return null;
    }

    try {
      const currentUser =
        await authService.getCurrentUser();

      setUser(currentUser);

      return currentUser;
    } catch (error) {
      console.error(
        "Failed to load user:",
        error
      );

      localStorage.removeItem("learnix_token");
      setUser(null);

      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (credentials) => {
    const data =
      await authService.login(credentials);

    if (!data?.access_token) {
      throw new Error(
        "Login succeeded but no access token was returned."
      );
    }

    localStorage.setItem(
      "learnix_token",
      data.access_token
    );

    await loadUser();

    return data;
  };

  const register = async (registrationData) => {
    const data =
      await authService.register(
        registrationData
      );

    if (data?.access_token) {
      localStorage.setItem(
        "learnix_token",
        data.access_token
      );

      await loadUser();
    }

    return data;
  };

  const logout = async () => {
    try {
      await authService.logout();
    } finally {
      localStorage.removeItem(
        "learnix_token"
      );

      setUser(null);
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    login,
    register,
    logout,
    refreshUser: loadUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

