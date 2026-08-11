import { useCallback, useRef, useState } from 'react'
import { synthesizeSpeech } from '../../../api/speech'

export type SpeechStatus = 'idle' | 'loading' | 'playing' | 'error'

const ERROR_DISPLAY_MS = 2500

// A valid (silent) audio source so `unlock()` has real media to play — an
// element that has never successfully played can't be "unlocked" by browsers'
// autoplay policies (Brave/Chrome block unmuted play() unless it's tied to a
// direct user gesture, and a later `.play()` deep inside an async chain no
// longer counts as one).
const SILENT_AUDIO_SRC =
  'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA='

export function useSpeechPlayback() {
  const [activeId, setActiveId] = useState<string | null>(null)
  const [status, setStatus] = useState<SpeechStatus>('idle')
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const urlRef = useRef<string | null>(null)

  // Lazily create one persistent <audio> element and reuse it for every
  // playback — reusing the same, already-unlocked element is what lets a
  // later programmatic play() succeed without a fresh gesture.
  function getAudio(): HTMLAudioElement {
    if (!audioRef.current) {
      audioRef.current = new Audio()
    }
    return audioRef.current
  }

  // Call synchronously from within a user gesture (e.g. a click handler)
  // before doing any async work, so the shared <audio> element is granted
  // autoplay permission while it can still be tied to that gesture.
  const unlock = useCallback(() => {
    const audio = getAudio()
    if (!audio.src) {
      audio.src = SILENT_AUDIO_SRC
    }
    audio.play().then(
      () => audio.pause(),
      () => {},
    )
  }, [])

  const cleanup = useCallback(() => {
    const audio = audioRef.current
    if (audio) {
      audio.pause()
      audio.onended = null
      audio.onerror = null
    }
    if (urlRef.current) {
      URL.revokeObjectURL(urlRef.current)
      urlRef.current = null
    }
  }, [])

  const stop = useCallback(() => {
    cleanup()
    setActiveId(null)
    setStatus('idle')
  }, [cleanup])

  const fail = useCallback(
    (id: string) => {
      cleanup()
      setStatus('error')
      setTimeout(() => {
        setActiveId((current) => (current === id ? null : current))
        setStatus((current) => (current === 'error' ? 'idle' : current))
      }, ERROR_DISPLAY_MS)
    },
    [cleanup],
  )

  const play = useCallback(
    async (id: string, text: string) => {
      if (activeId === id && (status === 'playing' || status === 'loading')) {
        stop()
        return
      }

      cleanup()
      setActiveId(id)
      setStatus('loading')

      let blob: Blob
      try {
        blob = await synthesizeSpeech(text)
      } catch (err) {
        console.error('Failed to synthesize speech', err)
        fail(id)
        return
      }

      const url = URL.createObjectURL(blob)
      urlRef.current = url
      const audio = getAudio()
      audio.src = url

      audio.onended = () => {
        cleanup()
        setActiveId((current) => (current === id ? null : current))
        setStatus((current) => (current === 'playing' ? 'idle' : current))
      }
      audio.onerror = () => fail(id)

      try {
        await audio.play()
        setStatus('playing')
      } catch (err) {
        console.error('Failed to play speech audio', err)
        fail(id)
      }
    },
    [activeId, status, stop, cleanup, fail],
  )

  return { activeId, status, play, stop, unlock }
}
