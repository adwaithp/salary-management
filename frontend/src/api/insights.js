import client from "./client";

export const getOverview = () =>
  client.get("/insights/overview/").then((r) => r.data);
export const getCountrySummary = () =>
  client.get("/insights/by-country/").then((r) => r.data);
export const getJobTitleSummary = (country) =>
  client.get("/insights/by-job-title/", { params: country ? { country } : {} }).then((r) => r.data);
export const getDepartmentSummary = () =>
  client.get("/insights/by-department/").then((r) => r.data);
export const getTopEarners = (limit = 10) =>
  client.get("/insights/top-earners/", { params: { limit } }).then((r) => r.data);
