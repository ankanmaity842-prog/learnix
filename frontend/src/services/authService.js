import api from "./api";

const authService = {
  async register(data) {
    const response = await api.post("/auth/register", data);
    return response.data;
  },

  async login(data) {
    const response = await api.post("/auth/login", data);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get("/auth/me");
    return response.data;
  },

  async logout() {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      // Local logout should still happen if backend logout fails.
      console.error("Logout request failed:", error);
    }
  },

  async forgotPassword(email) {
    const response = await api.post(
      "/auth/forgot-password",
      { email }
    );

    return response.data;
  },

  async resetPassword(token, password) {
    const response = await api.post(
      "/auth/reset-password",
      {
        token,
        password,
      }
    );

    return response.data;
  },

  getGoogleLoginUrl() {
    return `${api.defaults.baseURL}/auth/google/login`;
  },
};

export default authService;