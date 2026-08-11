import { useEffect, useRef, useState } from 'react'
import { Check, MoreHorizontal, Pencil, Plus, Trash2, X } from 'lucide-react'
import type { Conversation } from '../../../types/chat'

interface ConversationSidebarProps {
  conversations: Conversation[]
  activeConversationId: string | null
  isLoading: boolean
  isCreating: boolean
  isOpen: boolean
  onSelect: (conversationId: string) => void
  onNewChat: () => void
  onRename: (conversationId: string, title: string) => Promise<void>
  onDelete: (conversationId: string) => Promise<void>
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  isLoading,
  isCreating,
  isOpen,
  onSelect,
  onNewChat,
  onRename,
  onDelete,
}: ConversationSidebarProps) {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [draftTitle, setDraftTitle] = useState('')
  const [isSavingRename, setIsSavingRename] = useState(false)
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const editInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (editingId) {
      editInputRef.current?.focus()
      editInputRef.current?.select()
    }
  }, [editingId])

  function startRename(conversation: Conversation) {
    setOpenMenuId(null)
    setEditingId(conversation.id)
    setDraftTitle(conversation.title ?? '')
  }

  function cancelRename() {
    setEditingId(null)
    setDraftTitle('')
  }

  async function submitRename() {
    const title = draftTitle.trim()
    if (!title || !editingId || isSavingRename) return

    setIsSavingRename(true)
    try {
      await onRename(editingId, title)
      setEditingId(null)
      setDraftTitle('')
    } catch (err) {
      console.error('Failed to rename conversation', err)
    } finally {
      setIsSavingRename(false)
    }
  }

  function confirmDelete(conversationId: string) {
    setOpenMenuId(null)
    setDeleteError(null)
    setConfirmDeleteId(conversationId)
  }

  async function handleDeleteConfirmed() {
    if (!confirmDeleteId || isDeleting) return

    setIsDeleting(true)
    setDeleteError(null)
    try {
      await onDelete(confirmDeleteId)
      setConfirmDeleteId(null)
    } catch (err) {
      console.error('Failed to delete conversation', err)
      setDeleteError('Could not delete this conversation. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const conversationPendingDelete = conversations.find((c) => c.id === confirmDeleteId)

  return (
    <>
      <div
        className={`flex-none overflow-hidden transition-[width] duration-300 ease-in-out ${
          isOpen ? 'w-64' : 'w-0'
        }`}
      >
        <div
          className={`flex h-full w-64 flex-col border-r border-white/5 bg-surface p-4 transition-opacity duration-200 ${
            isOpen ? 'opacity-100 delay-100' : 'opacity-0'
          }`}
        >
          <button
            onClick={onNewChat}
            disabled={isCreating}
            className="flex items-center gap-2 rounded-lg bg-input px-4 py-2.5 text-sm font-medium text-text hover:opacity-90 disabled:opacity-60"
          >
            <Plus size={16} />
            New chat
          </button>

          <p className="mt-6 mb-2 text-xs font-medium tracking-wide text-text-subtle">RECENTS</p>

          <nav className="flex flex-col gap-1">
            {isLoading && <p className="px-3 py-2 text-sm text-text-subtle">Loading…</p>}

            {!isLoading && conversations.length === 0 && (
              <p className="px-3 py-2 text-sm text-text-subtle">No conversations yet</p>
            )}

            {conversations.map((conversation) => {
              const isEditing = editingId === conversation.id
              const isMenuOpen = openMenuId === conversation.id

              if (isEditing) {
                return (
                  <div
                    key={conversation.id}
                    className="flex items-center gap-1 rounded-lg bg-surface-raised px-2 py-1"
                  >
                    <input
                      ref={editInputRef}
                      value={draftTitle}
                      onChange={(e) => setDraftTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') submitRename()
                        if (e.key === 'Escape') cancelRename()
                      }}
                      onBlur={cancelRename}
                      className="min-w-0 flex-1 rounded-md border border-white/10 bg-input px-2 py-1 text-sm text-text focus:border-accent focus:outline-none"
                    />
                    <button
                      type="button"
                      aria-label="Save"
                      disabled={!draftTitle.trim() || isSavingRename}
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={submitRename}
                      className="flex h-6 w-6 flex-none items-center justify-center rounded text-accent hover:bg-white/5 disabled:opacity-40"
                    >
                      <Check size={14} />
                    </button>
                    <button
                      type="button"
                      aria-label="Cancel"
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={cancelRename}
                      className="flex h-6 w-6 flex-none items-center justify-center rounded text-text-muted hover:bg-white/5"
                    >
                      <X size={14} />
                    </button>
                  </div>
                )
              }

              return (
                <div key={conversation.id} className="group relative flex items-center">
                  <button
                    onClick={() => onSelect(conversation.id)}
                    className={`min-w-0 flex-1 truncate rounded-lg px-3 py-2 text-left text-sm ${
                      conversation.id === activeConversationId
                        ? 'text-text'
                        : 'text-text-muted hover:bg-surface-raised'
                    }`}
                  >
                    {conversation.title ?? 'New conversation'}
                  </button>

                  <button
                    type="button"
                    aria-label="Conversation actions"
                    onClick={() => setOpenMenuId(isMenuOpen ? null : conversation.id)}
                    className={`absolute right-1 flex h-7 w-7 flex-none items-center justify-center rounded-md text-text-subtle hover:bg-white/10 hover:text-text ${
                      isMenuOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                    }`}
                  >
                    <MoreHorizontal size={15} />
                  </button>

                  {isMenuOpen && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setOpenMenuId(null)} />
                      <div className="absolute right-0 top-full z-20 mt-1 w-36 rounded-xl border border-white/5 bg-surface-raised p-1.5 shadow-lg">
                        <button
                          type="button"
                          onClick={() => startRename(conversation)}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-text hover:bg-white/5"
                        >
                          <Pencil size={14} />
                          Rename
                        </button>
                        <button
                          type="button"
                          onClick={() => confirmDelete(conversation.id)}
                          className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm text-red-400 hover:bg-white/5"
                        >
                          <Trash2 size={14} />
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )
            })}
          </nav>
        </div>
      </div>

      {confirmDeleteId && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-sm rounded-2xl border border-white/5 bg-surface p-6">
            <h2 className="text-base font-semibold text-text">Delete this conversation?</h2>
            <p className="mt-2 text-sm text-text-muted">
              {conversationPendingDelete?.title ? `"${conversationPendingDelete.title}" ` : ''}
              This can't be undone.
            </p>

            {deleteError && <p className="mt-2 text-sm text-red-400">{deleteError}</p>}

            <div className="mt-5 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setConfirmDeleteId(null)}
                disabled={isDeleting}
                className="rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-text hover:bg-white/5 disabled:opacity-60"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteConfirmed}
                disabled={isDeleting}
                className="rounded-lg bg-red-500/90 px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-60"
              >
                {isDeleting ? 'Deleting…' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
