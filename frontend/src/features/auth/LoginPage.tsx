import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'
import { Input } from '../../components/Input'
import { Button } from '../../components/Button'
import { PasswordVisibilityToggle } from '../../components/PasswordVisibilityToggle'
import { login } from '../../api/auth'
import { setAccessToken } from '../../lib/tokenStore'
import { ApiError } from '../../api/client'

export function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      const response = await login({ email, password })
      setAccessToken(response.accessToken)
      navigate('/chat')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Unable to log in. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthLayout title="Welcome back" subtitle="Log in to continue logging your day.">
      <form className="space-y-5" onSubmit={handleSubmit}>
        <Input
          label="Email"
          type="email"
          placeholder="you@hospital.org"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          required
        />

        <Input
          label="Password"
          type={showPassword ? 'text' : 'password'}
          placeholder="••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
          endAdornment={
            <PasswordVisibilityToggle visible={showPassword} onToggle={() => setShowPassword((v) => !v)} />
          }
        />

        {error && <p className="text-sm text-red-400">{error}</p>}

        <Button type="submit" isLoading={isLoading}>
          Log In
        </Button>

        <p className="text-center text-sm text-text-muted">
          New to WardLog?{' '}
          <Link to="/register" className="text-accent hover:underline">
            Sign up
          </Link>
        </p>
      </form>
    </AuthLayout>
  )
}
