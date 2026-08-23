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
    <div className="mx-auto max-w-sm px-6 py-16">
      <h1 className="mb-6 font-serif text-2xl font-semibold tracking-tight">Register</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm placeholder:text-stone-400 focus:border-stone-500 focus:outline-none dark:border-stone-700 dark:bg-stone-900 dark:placeholder:text-stone-500"
        />
        <input
          type="password"
          required
          minLength={8}
          placeholder="Password (min. 8 characters)"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm placeholder:text-stone-400 focus:border-stone-500 focus:outline-none dark:border-stone-700 dark:bg-stone-900 dark:placeholder:text-stone-500"
        />
        {register.isError && (
          <p className="text-sm text-red-600 dark:text-red-400">{register.error.message}</p>
        )}
        <button
          type="submit"
          disabled={register.isPending}
          className="w-full rounded-md bg-stone-900 py-2 text-sm text-white hover:bg-stone-700 disabled:opacity-50 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-300"
        >
          {register.isPending ? 'Creating account…' : 'Register'}
        </button>
      </form>
      <p className="mt-4 text-sm text-stone-500 dark:text-stone-400">
        Already have an account?{' '}
        <Link to="/login" className="text-stone-900 underline dark:text-stone-100">
          Log in
        </Link>
      </p>
    </div>
  )
}
