const API_URL = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  const { token, ...fetchOptions } = options;
  const response = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...fetchOptions.headers,
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || Object.values(payload).flat().join(" ") || "Не удалось выполнить запрос";
    throw new Error(detail);
  }
  return payload;
}

export const getPublicStats = () => request("/public/stats/");
export const register = (credentials) => request("/auth/register/", { method: "POST", body: JSON.stringify(credentials) });
export const login = (credentials) => request("/auth/login/", { method: "POST", body: JSON.stringify(credentials) });
export const askQuestion = (token, question) => request("/questions/", { method: "POST", token, body: JSON.stringify({ question }) });
export const getHistory = (token) => request("/questions/", { token });
export const getProfile = (token) => request("/profile/", { token });
export const updateProfile = (token, profile) => request("/profile/", { method: "PATCH", token, body: JSON.stringify(profile) });
export const sendFeedback = (token, answerId, helpful) => request("/feedback/", {
  method: "POST",
  token,
  body: JSON.stringify({ answer_id: answerId, helpful, comment: "" }),
});
