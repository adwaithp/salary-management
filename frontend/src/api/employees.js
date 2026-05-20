import client from "./client";

export const getEmployees = (params) =>
  client.get("/employees/", { params }).then((r) => r.data);
export const createEmployee = (data) =>
  client.post("/employees/", data).then((r) => r.data);
export const updateEmployee = (id, data) =>
  client.patch(`/employees/${id}/`, data).then((r) => r.data);
export const deleteEmployee = (id) =>
  client.delete(`/employees/${id}/`);
