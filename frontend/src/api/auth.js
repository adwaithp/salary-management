import axios from "axios";

export const login = async (username, password) => {
  const response = await axios.post("/api/auth/token/", { username, password });
  return response.data;
};
