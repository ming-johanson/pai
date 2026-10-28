import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { SESSION_EXPIRED_EVENT, api } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [email, setEmail] = useState(api.getEmail());
  const [role, setRole] = useState(api.getRole());
  const [basketCount, setBasketCount] = useState(0);
  const isAuthenticated = Boolean(email && api.getToken());

  const refreshBasket = useCallback(async () => {
    if (!api.getToken()) {
      setBasketCount(0);
      return;
    }
    try {
      const basket = await api.getBasket();
      setBasketCount(basket.item_count);
    } catch {
      setBasketCount(0);
    }
  }, []);

  useEffect(() => {
    refreshBasket();
  }, [refreshBasket, email]);

  const login = useCallback(async (loginEmail, password) => {
    const result = await api.login(loginEmail, password);
    api.setAuth(result.access_token, result.email, result.role);
    setEmail(result.email);
    setRole(result.role);
    await refreshBasket();
    return result;
  }, [refreshBasket]);

  const changePassword = useCallback(
    (currentPassword, newPassword) => api.changePassword(currentPassword, newPassword),
    [],
  );

  useEffect(() => {
    function handleExpired() {
      setEmail(null);
      setRole(null);
      setBasketCount(0);
      const from = window.location.pathname;
      if (from !== '/login') {
        window.location.assign(`/login?expired=1&from=${encodeURIComponent(from)}`);
      }
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, handleExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleExpired);
  }, []);

  const logout = useCallback(() => {
    api.clearAuth();
    setEmail(null);
    setRole(null);
    setBasketCount(0);
  }, []);

  const value = useMemo(
    () => ({
      email,
      role,
      isAuthenticated,
      basketCount,
      refreshBasket,
      login,
      changePassword,
      logout,
    }),
    [email, role, isAuthenticated, basketCount, refreshBasket, login, changePassword, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
