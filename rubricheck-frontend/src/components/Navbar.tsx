import { Rocket, Upload, FileText, BarChart2, ArrowLeft, User, LogOut, LogIn } from 'lucide-react'
import { useAuthContext } from '../contexts/AuthContext'
import { useState } from 'react'
import AuthModal from './AuthModal'

interface NavbarProps {
  onViewChange: (view: 'main' | 'student-results') => void
  currentView: 'main' | 'student-results'
}

export default function Navbar({ onViewChange, currentView }: NavbarProps) {
  const { user, profile, signOut } = useAuthContext()
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const handleSignOut = async () => {
    await signOut()
    setShowUserMenu(false)
  }
  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur border-b border-gray-100">
      <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {currentView === 'student-results' && (
            <button
              onClick={() => onViewChange('main')}
              className="mr-2 p-1 text-gray-600 hover:text-gray-900 transition-colors"
              title="Back to main view"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
          )}
          <Rocket className="h-6 w-6 text-primary-600" />
          <span className="font-semibold">RubriCheck</span>
          {currentView === 'student-results' && (
            <span className="text-sm text-gray-500 ml-2">— Student View</span>
          )}
        </div>
        <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
          {currentView === 'main' ? (
            <>
              <a className="hover:text-gray-900 inline-flex items-center gap-1" href="#rubric"><Upload className="h-4 w-4" />Rubric</a>
              <a className="hover:text-gray-900 inline-flex items-center gap-1" href="#essay"><FileText className="h-4 w-4" />Essay</a>
              <a className="hover:text-gray-900 inline-flex items-center gap-1" href="#results"><BarChart2 className="h-4 w-4" />Results</a>
            </>
          ) : (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <User className="h-4 w-4" />
              <span>Student Results View</span>
            </div>
          )}
        </nav>

        {/* Auth Section */}
        <div className="flex items-center gap-4">
          {user ? (
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900"
              >
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-blue-600" />
                </div>
                <span className="hidden sm:block">{user.email}</span>
                {profile && (
                  <span className="hidden sm:block text-xs bg-gray-100 px-2 py-1 rounded-full">
                    {profile.subscription_tier}
                  </span>
                )}
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 py-1 z-50">
                  <div className="px-4 py-2 text-xs text-gray-500 border-b">
                    {user.email}
                  </div>
                  {profile && (
                    <div className="px-4 py-2 text-xs text-gray-500 border-b">
                      Plan: {profile.subscription_tier}
                    </div>
                  )}
                  <button
                    onClick={handleSignOut}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                  >
                    <LogOut className="h-4 w-4" />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900"
            >
              <LogIn className="h-4 w-4" />
              <span className="hidden sm:block">Sign In</span>
            </button>
          )}
        </div>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </header>
  )
}
