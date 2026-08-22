import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { LoginPage } from '../../src/pages/LoginPage'

const mutateMock = vi.fn()
const useLoginMock = vi.fn()
const setSessionMock = vi.fn()
const navigateMock = vi.fn()

vi.mock('../../src/api/auth', () => ({
  useLogin: () => useLoginMock(),
}))

vi.mock('../../src/auth/AuthContext', () => ({
  useAuth: () => ({ setSession: setSessionMock }),
}))

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>()
  return { ...actual, useNavigate: () => navigateMock }
})

describe('LoginPage', () => {
  beforeEach(() => {
    mutateMock.mockReset()
    setSessionMock.mockReset()
    navigateMock.mockReset()
    useLoginMock.mockReturnValue({ mutate: mutateMock, isPending: false, isError: false })
  })

  it('submits entered credentials and redirects on success', async () => {
    const user = userEvent.setup()
    mutateMock.mockImplementation((credentials, { onSuccess }) => {
      onSuccess({ user: { id: 1, email: credentials.email, created_at: '' }, token: 'tok' })
    })

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    await user.type(screen.getByPlaceholderText('Email'), 'a@example.com')
    await user.type(screen.getByPlaceholderText('Password'), 'password123')
    await user.click(screen.getByRole('button', { name: /log in/i }))

    expect(mutateMock).toHaveBeenCalledWith(
      { email: 'a@example.com', password: 'password123' },
      expect.objectContaining({ onSuccess: expect.any(Function) }),
    )
    expect(setSessionMock).toHaveBeenCalledWith(
      expect.objectContaining({ email: 'a@example.com' }),
      'tok',
    )
    expect(navigateMock).toHaveBeenCalledWith('/')
  })

  it('shows the error message returned by a failed login attempt', () => {
    useLoginMock.mockReturnValue({
      mutate: mutateMock,
      isPending: false,
      isError: true,
      error: { message: 'Invalid email or password' },
    })

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('Invalid email or password')).toBeInTheDocument()
  })

  it('disables the submit button while the login request is pending', () => {
    useLoginMock.mockReturnValue({ mutate: mutateMock, isPending: true, isError: false })

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>,
    )

    expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled()
  })
})
