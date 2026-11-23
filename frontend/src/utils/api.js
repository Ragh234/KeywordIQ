import axios from "axios";

const api = axios.create({
    baseURL: "/api",
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Requests where a 401 means "wrong credentials", not "your session expired".
const AUTH_FORM_URLS = ["/auth/login", "/auth/signup"];

// Auto-logout on 401 (expired or invalid token)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const isAuthForm = AUTH_FORM_URLS.includes(error.config?.url);
        if (error.response?.status === 401 && !isAuthForm) {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            window.location.href = "/login";
        }
        return Promise.reject(error);
    }
);

export default api;
