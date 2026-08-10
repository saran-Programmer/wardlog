import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import logo from '../../assets/logo-icon.png'
import messageIcon from '../../assets/message-icon.png'
import timesheetIcon from '../../assets/timesheet-icon.png'
import reportIcon from '../../assets/report-icon.png'
import { ProfileMenu } from './ProfileMenu'
import { SettingsModal } from './SettingsModal'
import { useUser } from '../hooks/useUser'
import { clearAccessToken } from '../lib/tokenStore'

const navItems = [
  { to: '/chat', icon: messageIcon, label: 'Chat' },
  { to: '/timesheet', icon: timesheetIcon, label: 'Timesheet' },
  { to: '/reports', icon: reportIcon, label: 'Reports' },
]

function getInitials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

interface IconRailProps {
  onChatIconClick?: () => void
}

export function IconRail({ onChatIconClick }: IconRailProps = {}) {
  const navigate = useNavigate()
  const { user, setUser } = useUser()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)

  function handleLogout() {
    clearAccessToken()
    navigate('/login')
  }

  return (
    <div className="relative flex w-[72px] flex-none flex-col items-center justify-between bg-bg py-4">
      <div className="flex flex-col items-center gap-6">
        <div className="flex h-9 w-9 flex-none items-center justify-center rounded-lg bg-accent" aria-label="WardLog">
          <span
            className="h-6 w-6 bg-white"
            style={{
              maskImage: `url(${logo})`,
              WebkitMaskImage: `url(${logo})`,
              maskSize: 'contain',
              WebkitMaskSize: 'contain',
              maskRepeat: 'no-repeat',
              WebkitMaskRepeat: 'no-repeat',
              maskPosition: 'center',
              WebkitMaskPosition: 'center',
            }}
          />
        </div>

        <nav className="flex flex-col gap-5">
          {navItems.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              aria-label={label}
              onClick={to === '/chat' ? onChatIconClick : undefined}
              className={({ isActive }) =>
                `flex h-10 w-10 items-center justify-center rounded-lg transition-colors ${
                  isActive ? 'text-accent' : 'text-text-muted hover:text-text'
                }`
              }
            >
              <span
                className="h-6 w-6 bg-current"
                style={{
                  maskImage: `url(${icon})`,
                  WebkitMaskImage: `url(${icon})`,
                  maskSize: 'contain',
                  WebkitMaskSize: 'contain',
                  maskRepeat: 'no-repeat',
                  WebkitMaskRepeat: 'no-repeat',
                  maskPosition: 'center',
                  WebkitMaskPosition: 'center',
                }}
              />
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="relative">
        <button
          type="button"
          onClick={() => setIsMenuOpen((prev) => !prev)}
          aria-label="Profile menu"
          className="flex h-10 w-10 items-center justify-center rounded-full bg-surface-raised text-sm font-semibold text-text-muted hover:text-text"
        >
          {user ? getInitials(user.name) : ''}
        </button>

        {isMenuOpen && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setIsMenuOpen(false)} />
            <ProfileMenu
              onSettingsClick={() => {
                setIsMenuOpen(false)
                setIsSettingsOpen(true)
              }}
              onLogoutClick={handleLogout}
            />
          </>
        )}
      </div>

      {isSettingsOpen && user && (
        <SettingsModal user={user} onClose={() => setIsSettingsOpen(false)} onSaved={setUser} />
      )}
    </div>
  )
}
