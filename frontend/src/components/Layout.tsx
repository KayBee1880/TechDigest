import { Link, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/useAuth'
import { ThemeToggle } from './ThemeToggle'

export function Layout() {
  const { user, clearSession } = useAuth()

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 transition-colors dark:bg-stone-950 dark:text-stone-100">
      <header className="border-b border-stone-200 dark:border-stone-800">
        <nav className="mx-auto flex max-w-3xl items-center justify-between px-6 py-5">
          <Link to="/" className="font-serif text-2xl font-semibold tracking-tight">
            TechDigest
          </Link>
          <div className="flex items-center gap-5 text-sm">
            <Link
              to="/"
              className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
            >
              Feed
            </Link>
            <Link
              to="/saved"
              className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
            >
              Saved
            </Link>
            {user ? (
              <>
                <span className="hidden text-stone-400 sm:inline dark:text-stone-500">
                  {user.email}
                </span>
                <button
                  type="button"
                  onClick={clearSession}
                  className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
                >
                  Log out
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
                >
                  Log in
                </Link>
                <Link
                  to="/register"
                  className="text-stone-600 hover:text-stone-900 dark:text-stone-400 dark:hover:text-stone-100"
                >
                  Register
                </Link>
              </>
            )}
            <ThemeToggle />
          </div>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
