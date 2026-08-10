import { useState } from 'react'
import { X } from 'lucide-react'
import { Input } from './Input'
import { updateProfile } from '../api/users'
import { refreshToken } from '../api/auth'
import { setAccessToken } from '../lib/tokenStore'
import { ApiError } from '../api/client'
import type { ToneType, UserResponse } from '../types/auth'

const SEX_OPTIONS = ['Male', 'Female', 'Other']

const TONE_OPTIONS: { value: ToneType; label: string }[] = [
  { value: 'FUNNY', label: 'Funny' },
  { value: 'PROFESSIONAL', label: 'Professional' },
  { value: 'WARM', label: 'Warm' },
]

interface SettingsModalProps {
  user: UserResponse
  onClose: () => void
  onSaved: (user: UserResponse) => void
}

export function SettingsModal({ user, onClose, onSaved }: SettingsModalProps) {
  const [name, setName] = useState(user.name)
  const [assistantName, setAssistantName] = useState(user.assistantName ?? '')
  const [age, setAge] = useState(user.age?.toString() ?? '')
  const [sex, setSex] = useState(user.sex ?? '')
  const [speciality, setSpeciality] = useState(user.speciality ?? '')
  const [tone, setTone] = useState<ToneType>((user.tone as ToneType) ?? 'PROFESSIONAL')
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  async function handleSave() {
    setError(null)
    setIsSaving(true)

    try {
      const updated = await updateProfile({
        name,
        assistantName: assistantName || undefined,
        age: age ? Number(age) : undefined,
        sex: sex || undefined,
        speciality: speciality || undefined,
        tone,
      })

      const { accessToken } = await refreshToken()
      setAccessToken(accessToken)

      onSaved(updated)
      onClose()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Unable to save your settings. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-2xl border border-white/5 bg-surface p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text">Settings</h2>
          <button type="button" onClick={onClose} aria-label="Close" className="text-text-muted hover:text-text">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-4">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />

          <Input
            label="What should the AI call you"
            value={assistantName}
            onChange={(e) => setAssistantName(e.target.value)}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input label="Age" type="number" min={0} value={age} onChange={(e) => setAge(e.target.value)} />

            <div>
              <label className="mb-1.5 block text-sm font-medium text-text-muted">Sex</label>
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className="w-full rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text focus:border-accent focus:outline-none"
              >
                <option value="">Select…</option>
                {SEX_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <Input label="Specialty" value={speciality} onChange={(e) => setSpeciality(e.target.value)} />

          <div>
            <label className="mb-1.5 block text-sm font-medium text-text-muted">Tone</label>
            <div className="grid grid-cols-3 gap-2">
              {TONE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setTone(option.value)}
                  className={`rounded-lg border py-2.5 text-sm font-medium transition-colors ${
                    tone === option.value
                      ? 'border-accent text-accent'
                      : 'border-white/10 text-text-muted hover:text-text'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-text hover:bg-white/5"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving}
            className="rounded-lg bg-accent px-5 py-2 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {isSaving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  )
}
