import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { ArrowUp, Mic, Paperclip, Plus, X, Zap } from 'lucide-react'

interface ComposerProps {
  onSend: (message: string, rush: boolean) => void
  isSending: boolean
}

export function Composer({ onSend, isSending }: ComposerProps) {
  const [message, setMessage] = useState('')
  const [rush, setRush] = useState(false)
  const [attachments, setAttachments] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = message.trim()
    if (!trimmed || isSending) return
    onSend(trimmed, rush)
    setMessage('')
  }

  function handleFilesSelected(event: ChangeEvent<HTMLInputElement>) {
    const files = event.target.files
    if (files && files.length > 0) {
      setAttachments((prev) => [...prev, ...Array.from(files)])
    }
    event.target.value = ''
  }

  function removeAttachment(index: number) {
    setAttachments((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="px-6 pb-4">
      <form onSubmit={handleSubmit} className="rounded-2xl border border-white/5 bg-surface-raised p-3">
        {attachments.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {attachments.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center gap-2 rounded-lg bg-accent-muted px-3 py-1.5 text-sm text-text"
              >
                <Paperclip size={14} className="shrink-0 text-accent-strong" />
                <span className="max-w-[220px] truncate">{file.name}</span>
                <button
                  type="button"
                  aria-label={`Remove ${file.name}`}
                  onClick={() => removeAttachment(index)}
                  className="flex h-4 w-4 items-center justify-center text-text-muted hover:text-text"
                >
                  <X size={14} />
                </button>
              </div>
            ))}
          </div>
        )}

        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Tell WardLog what you did today…"
          className="w-full bg-transparent px-2 py-1.5 text-text placeholder:text-text-subtle focus:outline-none"
        />

        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              multiple
              onChange={handleFilesSelected}
              className="hidden"
            />
            <button
              type="button"
              aria-label="Attach"
              onClick={() => fileInputRef.current?.click()}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-text-muted hover:text-text"
            >
              <Plus size={16} />
            </button>

            <button
              type="button"
              onClick={() => setRush((v) => !v)}
              aria-pressed={rush}
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium transition-colors ${
                rush ? 'bg-text text-bg' : 'bg-transparent text-text-muted border border-white/10'
              }`}
            >
              <Zap size={14} />
              Rush
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              aria-label="Voice input"
              className="flex h-9 w-9 items-center justify-center rounded-full border border-white/10 text-text-muted hover:text-text"
            >
              <Mic size={16} />
            </button>

            <button
              type="submit"
              aria-label="Send"
              disabled={isSending || message.trim().length === 0}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-bg hover:opacity-90 disabled:opacity-60"
            >
              <ArrowUp size={16} />
            </button>
          </div>
        </div>
      </form>

      <p className="mt-2 text-center text-xs text-text-subtle">
        WardLog listens and drafts activity entries for your review — nothing is logged until you accept it.
      </p>
    </div>
  )
}
