import { useMutation } from '@tanstack/react-query'
import { apiRequest } from './client'
import type { AuthResponse } from './types'

interface Credentials {
  email: string
  password: string
}

export function login({ email, password }: Credentials): Promise<AuthResponse> {
  return apiRequest('/auth/login', { method: 'POST', body: { email, password } })
}

export function register({ email, password }: Credentials): Promise<AuthResponse> {
  return apiRequest('/auth/register', { method: 'POST', body: { email, password } })
}

export function useLogin() {
  return useMutation({ mutationFn: login })
}

export function useRegister() {
  return useMutation({ mutationFn: register })
}
