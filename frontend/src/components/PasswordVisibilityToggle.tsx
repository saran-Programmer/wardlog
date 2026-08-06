import { Eye, EyeOff } from 'lucide-react'

interface PasswordVisibilityToggleProps {
  visible: boolean
  onToggle: () => void
}

export function PasswordVisibilityToggle({ visible, onToggle }: PasswordVisibilityToggleProps) {
  return (
    <button
      type="button"
      tabIndex={-1}
      onClick={onToggle}
      className="text-text-subtle hover:text-text-muted"
      aria-label={visible ? 'Hide password' : 'Show password'}
    >
      {visible ? <EyeOff size={18} /> : <Eye size={18} />}
    </button>
  )
}
