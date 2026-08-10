import { useId, type InputHTMLAttributes, type ReactNode } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  labelAction?: ReactNode
  endAdornment?: ReactNode
  overlay?: ReactNode
  error?: string
}

export function Input({
  label,
  labelAction,
  endAdornment,
  overlay,
  error,
  id,
  className = '',
  ...props
}: InputProps) {
  const generatedId = useId()
  const inputId = id ?? generatedId

  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <label htmlFor={inputId} className="text-sm font-medium text-text-muted">
          {label}
        </label>
        {labelAction}
      </div>
      <div className="relative">
        {overlay}
        <input
          id={inputId}
          className={`w-full rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text placeholder:text-text-subtle focus:border-accent focus:outline-none ${endAdornment ? 'pr-10' : ''} ${className}`}
          {...props}
        />
        {endAdornment && (
          <div className="absolute inset-y-0 right-3 flex items-center">{endAdornment}</div>
        )}
      </div>
      {error && <p className="mt-1 text-sm text-red-400">{error}</p>}
    </div>
  )
}
