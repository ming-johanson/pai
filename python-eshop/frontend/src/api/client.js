const TOKEN_KEY = 'eshop_token';
const EMAIL_KEY = 'eshop_email';
const ROLE_KEY = 'eshop_role';

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export const SESSION_EXPIRED_EVENT = 'eshop:session-expired';

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
  localStorage.removeItem(ROLE_KEY);
}

async function request(path, options = {}) {
  const headers = {
    ...getAuthHeaders(),
    ...options.headers,
  };
  const sentToken = Boolean(headers.Authorization);
  const response = await fetch(path, {
    ...options,
    headers,
  });

  if (response.status === 401 && sentToken) {
    // The session expired or was tampered with. End it and send the user
    // to sign in again; their basket is safe on the server.
    clearSession();
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    const detail = Array.isArray(error.detail)
      ? error.detail.map((item) => item.msg).join(', ')
      : error.detail;
    throw new Error(detail || 'Request failed');
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  getEmail: () => localStorage.getItem(EMAIL_KEY),
  getRole: () => localStorage.getItem(ROLE_KEY),
  setAuth(token, email, role) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(EMAIL_KEY, email);
    localStorage.setItem(ROLE_KEY, role);
  },
  clearAuth() {
    clearSession();
  },
  isAuthenticated() {
    return Boolean(localStorage.getItem(TOKEN_KEY));
  },

  getBrands: () => request('/api/catalog/brands'),
  getTypes: () => request('/api/catalog/types'),
  getCatalogItems: ({ brandId, typeId, page }) => {
    const params = new URLSearchParams({ page: String(page || 1) });
    if (brandId != null && brandId !== '') params.set('brand_id', brandId);
    if (typeId != null && typeId !== '') params.set('type_id', typeId);
    return request(`/api/catalog/items?${params}`);
  },

  getBasket: () => request('/api/basket'),
  addToBasket: (catalogItemId, quantity = 1) =>
    request('/api/basket/items', {
      method: 'POST',
      body: JSON.stringify({ catalog_item_id: catalogItemId, quantity }),
    }),
  updateBasket: (quantities) =>
    request('/api/basket/items', {
      method: 'PUT',
      body: JSON.stringify({ quantities }),
    }),

  login: (email, password) =>
    request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  changePassword: (currentPassword, newPassword) =>
    request('/api/auth/password', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }),

  createOrder: (basketId) =>
    request('/api/orders', {
      method: 'POST',
      body: JSON.stringify({ basket_id: basketId }),
    }),
  getOrders: () => request('/api/orders'),
  getOrder: (orderId) => request(`/api/orders/${orderId}`),
};
