const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.token ? { Authorization: `Token ${options.token}` } : {}),
      ...options.headers,
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || Object.values(payload).flat().join(" ") || "Ошибка запроса";
    throw new Error(detail);
  }
  return payload;
}

export function register(credentials) {
  return request("/auth/register/", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export function login(credentials) {
  return request("/auth/login/", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
}

export function askQuestion(token, question) {
  return request("/questions/", {
    method: "POST",
    token,
    body: JSON.stringify({ question }),
  });
}

