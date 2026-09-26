import api from "./api";

const searchService = {
  async search(query, options = {}) {
    const response = await api.get("/search", {
      params: {
        q: query,
        ...options,
      },
    });

    return response.data;
  },
};

export default searchService;