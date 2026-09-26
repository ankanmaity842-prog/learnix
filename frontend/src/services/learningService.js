import api from "./api";

const learningService = {
  async startSession(data) {
    const response = await api.post(
      "/learning/sessions",
      data
    );

    return response.data;
  },

  async updateProgress(id, data) {
    const response = await api.patch(
      `/learning/sessions/${id}`,
      data
    );

    return response.data;
  },

  async getSessions() {
    const response = await api.get(
      "/learning/sessions"
    );

    return response.data;
  },
};

export default learningService;