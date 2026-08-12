import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { ArrowUp, Mic, Paperclip, Plus, Square, X, Zap } from 'lucide-react'

interface ComposerProps {
  onSend: (message: string, rush: boolean, viaVoice?: boolean, file?: File | null) => void
  onSendVoice: (audio: Blob, rush: boolean) => void
  onMicUnlock?: () => void
  isSending: boolean
}

export function Composer({ onSend, onSendVoice, onMicUnlock, isSending }: ComposerProps) {
  const [message, setMessage] = useState('')
  const [rush, setRush] = useState(false)
  const [attachment, setAttachment] = useState<File | null>(null)
  const [isRecording, setIsRecording] = useState(false)
  const [micError, setMicError] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop())
    }
  }, [])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = message.trim()
    if (isSending || (!trimmed && !attachment)) return
    onSend(trimmed, rush, false, attachment)
    setMessage('')
    setAttachment(null)
  }

  function handleFilesSelected(event: ChangeEvent<HTMLInputElement>) {
    const files = event.target.files
    if (files && files.length > 0) {
      setAttachment(files[0])
    }
    event.target.value = ''
  }

  function removeAttachment() {
    setAttachment(null)
  }

  function stopStream() {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
  }

  async function handleMicClick() {
    if (isSending) return

    // Must run synchronously within this click's gesture, before any await —
    // it's what lets the auto-played reply audio bypass the autoplay block later.
    onMicUnlock?.()

    if (isRecording) {
      mediaRecorderRef.current?.stop()
      return
    }

    setMicError(false)

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream

      const recorder = new MediaRecorder(stream)
      mediaRecorderRef.current = recorder
      chunksRef.current = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      recorder.onstop = () => {
        stopStream()
        setIsRecording(false)

        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        chunksRef.current = []

        if (blob.size > 0) {
          onSendVoice(blob, rush)
        }
      }

      recorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error('Microphone access failed', err)
      stopStream()
      setMicError(true)
      setTimeout(() => setMicError(false), 2500)
    }
  }

  return (
    <div className="px-6 pb-4">
      <form onSubmit={handleSubmit} className="rounded-2xl border border-white/5 bg-surface-raised p-3">
        {attachment && (
          <div className="mb-2 flex flex-wrap gap-2">
            <div className="flex items-center gap-2 rounded-lg bg-accent-muted px-3 py-1.5 text-sm text-text">
              <Paperclip size={14} className="shrink-0 text-accent-strong" />
              <span className="max-w-[220px] truncate">{attachment.name}</span>
              <button
                type="button"
                aria-label={`Remove ${attachment.name}`}
                onClick={removeAttachment}
                className="flex h-4 w-4 items-center justify-center text-text-muted hover:text-text"
              >
                <X size={14} />
              </button>
            </div>
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
              aria-label={isRecording ? 'Stop recording' : micError ? 'Microphone unavailable' : 'Voice input'}
              onClick={handleMicClick}
              disabled={isSending}
              className={`flex h-9 w-9 items-center justify-center rounded-full border text-text-muted transition-colors hover:text-text disabled:opacity-60 ${
                isRecording ? 'animate-pulse border-red-400 text-red-400' : ''
              } ${micError ? 'border-red-400 text-red-400' : 'border-white/10'}`}
            >
              {isRecording ? <Square size={14} /> : <Mic size={16} />}
            </button>

            <button
              type="submit"
              aria-label="Send"
              disabled={isSending || isRecording || (message.trim().length === 0 && !attachment)}
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
