import React, { ReactNode } from 'react'
import { useAuthContext } from '../contexts/AuthContext'
import AuthModal from './AuthModal'

interface ProtectedRouteProps {
  children: ReactNode
  fallback?: ReactNode
}

export default function ProtectedRoute({ children, fallback }: ProtectedRouteProps) {
  const { user, loading } = useAuthContext()
  const [showAuthModal, setShowAuthModal] = React.useState(false)

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (!user) {
    if (fallback) {
      return <>{fallback}</>
    }

    return (
      <>
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Sign in to RubriCheck
            </h2>
            <p className="mt-2 text-center text-sm text-gray-600">
              Access your essays, rubrics, and evaluations
            </p>
          </div>

          <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
            <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
              <div className="space-y-6">
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Sign In / Sign Up
                </button>
                
                <div className="text-center">
                  <p className="text-sm text-gray-600">
                    Or continue as guest to try RubriCheck
                  </p>
                  <button
                    onClick={() => window.location.reload()}
                    className="mt-2 text-sm text-blue-600 hover:text-blue-500"
                  >
                    Continue as Guest
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
    )
  }

  return <>{children}</>
}
