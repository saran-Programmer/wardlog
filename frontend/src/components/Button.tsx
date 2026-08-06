import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean
}

export function Button({ isLoading, disabled, children, className = '', ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || isLoading}
      className={`w-full rounded-lg bg-accent py-3 font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-60 ${className}`}
      {...props}
    >
      {isLoading ? 'Please wait…' : children}
    </button>
  )
}
