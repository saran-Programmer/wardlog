import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { LoginPage } from './features/auth/LoginPage'
import { RegisterPage } from './features/auth/RegisterPage'
import { ChatPage } from './features/chat/ChatPage'
import { TimesheetPage } from './features/timesheet/TimesheetPage'
import { UserProvider } from './hooks/useUser'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/chat"
          element={
            <UserProvider>
              <ChatPage />
            </UserProvider>
          }
        />
        <Route
          path="/timesheet"
          element={
            <UserProvider>
              <TimesheetPage />
            </UserProvider>
          }
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
