import api from "./api";

const notesService = {
  async getNotes() {
    const response = await api.get("/notes");
    return response.data;
  },

  async createNote(data) {
    const response = await api.post(
      "/notes",
      data
    );

    return response.data;
  },

  async updateNote(id, data) {
    const response = await api.put(
      `/notes/${id}`,
      data
    );

    return response.data;
  },

  async deleteNote(id) {
    const response = await api.delete(
      `/notes/${id}`
    );

    return response.data;
  },
};

export default notesService;