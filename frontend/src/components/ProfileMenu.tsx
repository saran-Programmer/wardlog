import { LogOut, Settings } from 'lucide-react'

interface ProfileMenuProps {
  onSettingsClick: () => void
  onLogoutClick: () => void
}

export function ProfileMenu({ onSettingsClick, onLogoutClick }: ProfileMenuProps) {
  return (
    <div className="absolute bottom-14 left-0 z-20 w-52 rounded-xl border border-white/5 bg-surface-raised p-1.5 shadow-lg">
      <button
        type="button"
        onClick={onSettingsClick}
        className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm text-text hover:bg-white/5"
      >
        <Settings size={16} />
        Settings
      </button>
      <div className="my-1 h-px bg-white/5" />
      <button
        type="button"
        onClick={onLogoutClick}
        className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm text-text hover:bg-white/5"
      >
        <LogOut size={16} />
        Log out
      </button>
    </div>
  )
}
