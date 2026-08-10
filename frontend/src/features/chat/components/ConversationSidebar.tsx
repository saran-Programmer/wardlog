import { Plus } from 'lucide-react'
import type { Conversation } from '../../../types/chat'

interface ConversationSidebarProps {
  conversations: Conversation[]
  activeConversationId: string | null
  isLoading: boolean
  isCreating: boolean
  isOpen: boolean
  onSelect: (conversationId: string) => void
  onNewChat: () => void
}

export function ConversationSidebar({
  conversations,
  activeConversationId,
  isLoading,
  isCreating,
  isOpen,
  onSelect,
  onNewChat,
}: ConversationSidebarProps) {
  return (
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

          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              onClick={() => onSelect(conversation.id)}
              className={`truncate rounded-lg px-3 py-2 text-left text-sm ${
                conversation.id === activeConversationId
                  ? 'text-text'
                  : 'text-text-muted hover:bg-surface-raised'
              }`}
            >
              {conversation.title ?? 'New conversation'}
            </button>
          ))}
        </nav>
      </div>
    </div>
  )
}
