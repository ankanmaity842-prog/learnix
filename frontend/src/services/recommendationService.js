import api from "./api";

const recommendationService = {
  async getRecommendations(params = {}) {
    const response = await api.get(
      "/recommendations",
      {
        params,
      }
    );

    return response.data;
  },
};

export default recommendationService;