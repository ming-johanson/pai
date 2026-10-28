import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './context/AuthContext';
import BasketPage from './pages/BasketPage';
import CatalogPage from './pages/CatalogPage';
import CheckoutPage from './pages/CheckoutPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import LoginPage from './pages/LoginPage';
import OrderDetailPage from './pages/OrderDetailPage';
import OrdersPage from './pages/OrdersPage';
import SuccessPage from './pages/SuccessPage';

function RequireSignIn({ children }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<RequireSignIn><CatalogPage /></RequireSignIn>} />
            <Route path="/basket" element={<RequireSignIn><BasketPage /></RequireSignIn>} />
            <Route path="/checkout" element={<RequireSignIn><CheckoutPage /></RequireSignIn>} />
            <Route path="/success" element={<RequireSignIn><SuccessPage /></RequireSignIn>} />
            <Route path="/orders" element={<RequireSignIn><OrdersPage /></RequireSignIn>} />
            <Route
              path="/orders/:orderId"
              element={<RequireSignIn><OrderDetailPage /></RequireSignIn>}
            />
            <Route path="/account" element={<RequireSignIn><ChangePasswordPage /></RequireSignIn>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}
