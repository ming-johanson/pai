import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function ChangePasswordPage() {
  const { email, changePassword } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setSaved(false);
    if (newPassword !== confirm) {
      setError('New passwords do not match');
      return;
    }
    setLoading(true);
    try {
      await changePassword(currentPassword, newPassword);
      setSaved(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirm('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <h1 className="text-2xl font-bold text-slate-900">Your account</h1>
        <p className="mt-1 text-sm text-slate-500">Signed in as {email}</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="current" className="mb-1 block text-sm font-medium text-slate-700">
              Current password
            </label>
            <input
              id="current"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              className="input-field"
              required
            />
          </div>
          <div>
            <label htmlFor="new" className="mb-1 block text-sm font-medium text-slate-700">
              New password
            </label>
            <input
              id="new"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              className="input-field"
              minLength={6}
              required
            />
          </div>
          <div>
            <label htmlFor="confirm" className="mb-1 block text-sm font-medium text-slate-700">
              Confirm new password
            </label>
            <input
              id="confirm"
              type="password"
              value={confirm}
              onChange={(event) => setConfirm(event.target.value)}
              className="input-field"
              required
            />
          </div>

          {error && <p className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
          {saved && (
            <p className="rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
              Password changed.
            </p>
          )}

          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? 'Saving...' : 'Change password'}
          </button>
        </form>
      </div>
    </div>
  );
}
