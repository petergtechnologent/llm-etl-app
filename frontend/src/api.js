import axios from 'axios';

// Adjust this if your backend is on a different port
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

export const getNotes = async () => {
  const response = await axios.get(`${API_BASE}/notes`);
  return response.data;
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post(`${API_BASE}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};
