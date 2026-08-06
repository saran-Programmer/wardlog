import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'
import { Input } from '../../components/Input'
import { Button } from '../../components/Button'
import { PasswordVisibilityToggle } from '../../components/PasswordVisibilityToggle'
import { register } from '../../api/auth'
import { setAccessToken } from '../../lib/tokenStore'
import { ApiError } from '../../api/client'

export function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [speciality, setSpeciality] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsLoading(true)

    try {
      const response = await register({
        name,
        email,
        password,
        speciality: speciality || undefined,
        tone: 'PROFESSIONAL',
      })
      setAccessToken(response.accessToken)
      navigate('/chat')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Unable to create your account. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthLayout title="Create your account" subtitle="Start logging your clinical day in seconds.">
      <form className="space-y-5" onSubmit={handleSubmit}>
        <Input
          label="Full name"
          placeholder="Dr. Jordan Reyes"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoComplete="name"
          required
        />

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
          label="Specialty (optional)"
          placeholder="e.g. Orthopedic Surgery"
          value={speciality}
          onChange={(e) => setSpeciality(e.target.value)}
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Password"
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
            endAdornment={
              <PasswordVisibilityToggle visible={showPassword} onToggle={() => setShowPassword((v) => !v)} />
            }
          />
          <Input
            label="Confirm"
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
            minLength={8}
            required
            endAdornment={
              <PasswordVisibilityToggle
                visible={showConfirmPassword}
                onToggle={() => setShowConfirmPassword((v) => !v)}
              />
            }
          />
        </div>

        {error && <p className="text-sm text-red-400">{error}</p>}

        <Button type="submit" isLoading={isLoading}>
          Create Account
        </Button>

        <p className="text-center text-sm text-text-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-accent hover:underline">
            Log in
          </Link>
        </p>
      </form>
    </AuthLayout>
  )
}
