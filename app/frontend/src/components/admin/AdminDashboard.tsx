import { useEffect, useState, type FormEvent, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'sonner';
import { ArrowLeft, Plus, Trash2, Coins, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { getAdminUsers, createAdminUser, deleteAdminUser, updateUserTokens } from '../../api/admin';
import { useAuthStore } from '../../store/authStore';
import type { AdminUser } from '../../types';

const PAGE_SIZE = 20;

// ─── Shared modal backdrop ────────────────────────────────────────────────────

function ModalBackdrop({
  children,
  onClose,
  wide,
}: {
  children: ReactNode;
  onClose: () => void;
  wide?: boolean;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className={`w-full ${wide ? 'max-w-lg' : 'max-w-md'} bg-white dark:bg-gray-900 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-800 p-6 relative`}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
        >
          <X size={16} />
        </button>
        {children}
      </div>
    </div>
  );
}

// ─── Create User Modal ────────────────────────────────────────────────────────

function CreateUserModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: (user: AdminUser) => void;
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email || !password) { setError('Both fields are required.'); return; }
    setError('');
    setSubmitting(true);
    try {
      const user = await createAdminUser({ email, password, is_admin: isAdmin });
      toast.success(`User ${user.email} created.`);
      onCreated(user);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } }).response?.status;
      setError(status === 409 ? 'Email already in use.' : 'Failed to create user.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <ModalBackdrop onClose={onClose}>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Create User</h2>
      <form onSubmit={handleSubmit} noValidate className="space-y-3">
        {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Email
          </label>
          <input
            type="email"
            autoFocus
            autoComplete="off"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="user@example.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Password
          </label>
          <input
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <label className="flex items-center gap-2.5 cursor-pointer select-none pt-1">
          <input
            type="checkbox"
            checked={isAdmin}
            onChange={(e) => setIsAdmin(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700 dark:text-gray-300">Grant admin privileges</span>
        </label>
        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm font-medium transition-colors"
          >
            {submitting ? 'Creating…' : 'Create'}
          </button>
        </div>
      </form>
    </ModalBackdrop>
  );
}

// ─── Manage Tokens Modal ──────────────────────────────────────────────────────

function ManageTokensModal({
  user,
  onClose,
  onUpdated,
}: {
  user: AdminUser;
  onClose: () => void;
  onUpdated: () => void;
}) {
  const [balances, setBalances] = useState<Record<string, string>>(
    () => Object.fromEntries(user.token_balances.map((b) => [b.model_name, String(b.balance)])),
  );
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState('');

  async function handleSave(modelName: string) {
    const bal = parseInt(balances[modelName] ?? '0', 10);
    if (isNaN(bal) || bal < 0) {
      setError(`Balance for "${modelName}" must be a non-negative integer.`);
      return;
    }
    setError('');
    setSaving(modelName);
    try {
      await updateUserTokens(user.id, { model_name: modelName, balance: bal });
      toast.success(`${modelName}: balance set to ${bal.toLocaleString()}.`);
      onUpdated();
    } catch {
      setError(`Failed to update ${modelName}.`);
    } finally {
      setSaving(null);
    }
  }

  return (
    <ModalBackdrop onClose={onClose} wide>
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-0.5">Manage Tokens</h2>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 truncate">{user.email}</p>
      {error && <p className="text-sm text-red-600 dark:text-red-400 mb-3">{error}</p>}
      {user.token_balances.length === 0 ? (
        <p className="text-sm text-gray-400 dark:text-gray-500 py-6 text-center">No models available.</p>
      ) : (
        <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
          {user.token_balances.map((b) => (
            <div
              key={b.model_name}
              className="flex items-center gap-3 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2"
            >
              <span className="flex-1 text-sm font-medium text-gray-700 dark:text-gray-300 truncate">
                {b.model_name}
              </span>
              <input
                type="number"
                min={0}
                value={balances[b.model_name] ?? String(b.balance)}
                onChange={(e) =>
                  setBalances((prev) => ({ ...prev, [b.model_name]: e.target.value }))
                }
                className="w-28 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 px-2 py-1 text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-right"
              />
              <button
                onClick={() => handleSave(b.model_name)}
                disabled={saving === b.model_name}
                className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-xs font-medium transition-colors shrink-0"
              >
                {saving === b.model_name ? 'Saving…' : 'Save'}
              </button>
            </div>
          ))}
        </div>
      )}
      <div className="flex justify-end mt-4">
        <button
          onClick={onClose}
          className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          Close
        </button>
      </div>
    </ModalBackdrop>
  );
}

// ─── Main dashboard ───────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const currentUserId = useAuthStore((s) => s.userId);

  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [tokensModal, setTokensModal] = useState<AdminUser | null>(null);

  async function fetchUsers(p: number) {
    setLoading(true);
    try {
      const data = await getAdminUsers({ skip: p * PAGE_SIZE, limit: PAGE_SIZE });
      setUsers(data);
      setHasMore(data.length === PAGE_SIZE);
    } catch {
      toast.error('Failed to load users.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchUsers(page); }, [page]); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleDelete(targetUserId: number, email: string) {
    if (!window.confirm(`Delete user "${email}"? This cannot be undone.`)) return;
    try {
      await deleteAdminUser(targetUserId);
      setUsers((prev) => prev.filter((u) => u.id !== targetUserId));
      toast.success('User deleted.');
    } catch {
      toast.error('Failed to delete user.');
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-6 py-4 shrink-0">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <ArrowLeft size={15} />
              Back to chat
            </Link>
            <span className="text-gray-300 dark:text-gray-700 select-none">|</span>
            <h1 className="text-base font-semibold text-gray-900 dark:text-white">Admin Dashboard</h1>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors"
          >
            <Plus size={14} />
            Create User
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-6">
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-400 w-12">ID</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-400">Email</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-400">Username</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 dark:text-gray-400">Token Balances</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600 dark:text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-4 py-10 text-center">
                    <div className="inline-block animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full" />
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-4 py-10 text-center text-sm text-gray-400 dark:text-gray-500"
                  >
                    No users found.
                  </td>
                </tr>
              ) : (
                users.map((user) => {
                  const isSelf = user.id === currentUserId;
                  return (
                    <tr
                      key={user.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="px-4 py-3 font-mono text-xs text-gray-400 dark:text-gray-500">
                        {user.id}
                      </td>
                      <td className="px-4 py-3 text-gray-900 dark:text-white">
                        {user.email}
                        {user.is_admin && (
                          <span className="ml-2 text-xs px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                            admin
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                        {user.username ?? '—'}
                      </td>
                      <td className="px-4 py-3">
                        {user.token_balances.length === 0 ? (
                          <span className="text-gray-400 dark:text-gray-500">—</span>
                        ) : (
                          <div className="flex flex-wrap gap-1.5">
                            {user.token_balances.map((b) => (
                              <span
                                key={b.id !== 0 ? b.id : b.model_name}
                                className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300"
                              >
                                {b.model_name}: {b.balance.toLocaleString()}
                              </span>
                            ))}
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setTokensModal(user)}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:border-blue-400 hover:text-blue-600 dark:hover:border-blue-500 dark:hover:text-blue-400 transition-colors"
                          >
                            <Coins size={12} />
                            Manage Tokens
                          </button>
                          <button
                            onClick={() => handleDelete(user.id, user.email)}
                            disabled={isSelf}
                            title={isSelf ? 'You cannot delete your own account' : undefined}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-colors text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-700 hover:border-red-400 hover:text-red-600 dark:hover:border-red-500 dark:hover:text-red-400 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:border-gray-200 dark:disabled:hover:border-gray-700 disabled:hover:text-gray-600 dark:disabled:hover:text-gray-400"
                          >
                            <Trash2 size={12} />
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 dark:border-gray-800">
            <span className="text-xs text-gray-400 dark:text-gray-500">
              Page {page + 1}
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 0 || loading}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft size={13} />
                Prev
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!hasMore || loading}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Next
                <ChevronRight size={13} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {showCreateModal && (
        <CreateUserModal
          onClose={() => setShowCreateModal(false)}
          onCreated={(user) => {
            setUsers((prev) => [...prev, user]);
            setShowCreateModal(false);
          }}
        />
      )}

      {tokensModal !== null && (
        <ManageTokensModal
          user={tokensModal}
          onClose={() => setTokensModal(null)}
          onUpdated={() => fetchUsers(page)}
        />
      )}
    </div>
  );
}


