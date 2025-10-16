import React, { useState } from 'react'
import { AuthProvider } from './contexts/AuthContext'
import Navbar from './components/Navbar'
import UploadRubric from './pages/UploadRubric'
import UploadEssay from './pages/UploadEssay'
import RunEvaluation from './pages/RunEvaluation'
import Results from './pages/Results'
import StudentResults from './pages/StudentResults'
import { loadTestData } from './utils/loadTestData'

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('App Error Boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-red-50 flex items-center justify-center">
          <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-lg">
            <h1 className="text-xl font-bold text-red-600 mb-4">Something went wrong</h1>
            <p className="text-gray-700 mb-4">
              The application encountered an error. Please refresh the page to try again.
            </p>
            <details className="text-sm text-gray-600">
              <summary className="cursor-pointer font-medium">Error Details</summary>
              <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
                {this.state.error?.toString()}
              </pre>
            </details>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Refresh Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default function App() {
  const [currentView, setCurrentView] = useState<'main' | 'student-results'>('main')

  const handleViewChange = (view: 'main' | 'student-results') => {
    setCurrentView(view)
  }

  return (
    <ErrorBoundary>
      <AuthProvider>
        <div className="min-h-screen">
          <Navbar onViewChange={handleViewChange} currentView={currentView} />
          {currentView === 'main' ? (
            <main className="mx-auto max-w-6xl px-4 py-8 space-y-6">
              {/* Test Data Button - Remove in production */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-medium text-yellow-800">🧪 Development Mode</h3>
                    <p className="text-xs text-yellow-700 mt-1">Load test data to preview Student Results without running evaluation</p>
                  </div>
                  <button
                    onClick={loadTestData}
                    className="px-4 py-2 bg-yellow-600 text-white text-sm rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500"
                  >
                    Load Test Data
                  </button>
                </div>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <UploadRubric />
                <UploadEssay />
              </div>
              <RunEvaluation />
              <Results onViewChange={handleViewChange} />
              <footer className="text-xs text-gray-500 py-8">
                <div className="mx-auto max-w-6xl">RubriCheck · Frontend (React + Vite + Tailwind). </div>
              </footer>
            </main>
          ) : (
            <StudentResults onViewChange={handleViewChange} />
          )}
        </div>
      </AuthProvider>
    </ErrorBoundary>
  )
}
