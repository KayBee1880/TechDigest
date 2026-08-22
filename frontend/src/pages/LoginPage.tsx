import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useLogin } from '../api/auth'
import { useAuth } from '../auth/useAuth'

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const login = useLogin()
  const { setSession } = useAuth()
  const navigate = useNavigate()

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    login.mutate(
      { email, password },
      {
        onSuccess: (data) => {
          setSession(data.user, data.token)
          navigate('/')
        },
      },
    )
  }

  return (
    <div className="mx-auto max-w-sm p-6">
      <h1 className="mb-4 text-2xl font-semibold">Log in</h1>
      <form onSubmit={handleSubmit} className="space-y-3">
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full rounded border border-slate-800 bg-slate-900 p-2"
        />
        <input
          type="password"
          required
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full rounded border border-slate-800 bg-slate-900 p-2"
        />
        {login.isError && <p className="text-sm text-red-400">{login.error.message}</p>}
        <button
          type="submit"
          disabled={login.isPending}
          className="w-full rounded bg-sky-600 py-2 hover:bg-sky-500 disabled:opacity-50"
        >
          {login.isPending ? 'Logging in…' : 'Log in'}
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-400">
        No account?{' '}
        <Link to="/register" className="text-sky-400 hover:underline">
          Register
        </Link>
      </p>
    </div>
  )
}
