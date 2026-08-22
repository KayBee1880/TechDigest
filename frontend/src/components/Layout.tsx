import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

export function Layout() {
  const { user, clearSession } = useAuth()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <nav className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
        <Link to="/" className="text-lg font-semibold">
          TechDigest
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <Link to="/" className="hover:underline">
            Feed
          </Link>
          {user ? (
            <>
              <Link to="/saved" className="hover:underline">
                Saved
              </Link>
              <span className="text-slate-400">{user.email}</span>
              <button onClick={clearSession} className="text-slate-400 hover:underline">
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:underline">
                Log in
              </Link>
              <Link to="/register" className="hover:underline">
                Register
              </Link>
            </>
          )}
        </div>
      </nav>
      <Outlet />
    </div>
  )
}
