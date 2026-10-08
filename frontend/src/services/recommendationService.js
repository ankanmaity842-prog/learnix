import api from "./api";

const recommendationService = {
  async getForTopic(topic, params = {}) {
    const response = await api.get(
      `/recommendations/for-topic/${encodeURIComponent(topic)}`,
      {
        params: {
          language: "en",
          level: "beginner",
          limit: 10,
          ...params,
        },
      }
    );

    return response.data;
  },

  async getRecommendations(params = {}) {
    const response = await api.get("/recommendations", {
      params,
    });

    return response.data;
  },
};

export default recommendationService;