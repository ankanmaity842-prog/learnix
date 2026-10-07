
import api from "./api";

const authService = {
  async register(data) {
    const response = await api.post(
      "/auth/register",
      data
    );

    return response.data;
  },

  async login(data) {
    const response = await api.post(
      "/auth/login",
      data
    );

    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get(
      "/auth/me"
    );

    return response.data;
  },

  async logout() {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      console.error(
        "Logout request failed:",
        error
      );
    }
  },

  async forgotPassword(email) {
    const response = await api.post(
      "/auth/forgot-password",
      { email }
    );

    return response.data;
  },

  async resetPassword(
    token,
    password,
    confirmPassword
  ) {
    const response = await api.post(
      "/auth/reset-password",
      {
        token,
        password,
        confirm_password: confirmPassword,
      }
    );

    return response.data;
  },

  getGoogleLoginUrl() {
    return `${api.defaults.baseURL}/auth/google/login`;
  },
};

export default authService;


