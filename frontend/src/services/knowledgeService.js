import api from "./api";

const knowledgeService = {
  async getKnowledge() {
    const response = await api.get(
      "/knowledge"
    );

    return response.data;
  },

  async getKnowledgeGaps(topic) {
    const response = await api.get(
      "/knowledge/gaps",
      {
        params: { topic },
      }
    );

    return response.data;
  },
};

export default knowledgeService;