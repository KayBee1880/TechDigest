import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useRegister } from '../api/auth'
import { useAuth } from '../auth/useAuth'

export function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const register = useRegister()
  const { setSession } = useAuth()
  const navigate = useNavigate()

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    register.mutate(
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
      <h1 className="mb-4 text-2xl font-semibold">Register</h1>
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
          minLength={8}
          placeholder="Password (min. 8 characters)"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full rounded border border-slate-800 bg-slate-900 p-2"
        />
        {register.isError && <p className="text-sm text-red-400">{register.error.message}</p>}
        <button
          type="submit"
          disabled={register.isPending}
          className="w-full rounded bg-sky-600 py-2 hover:bg-sky-500 disabled:opacity-50"
        >
          {register.isPending ? 'Creating account…' : 'Register'}
        </button>
      </form>
      <p className="mt-4 text-sm text-slate-400">
        Already have an account?{' '}
        <Link to="/login" className="text-sky-400 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  )
}
