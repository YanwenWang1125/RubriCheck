import { Rocket, Upload, FileText, BarChart2, ArrowLeft, User } from 'lucide-react'

interface NavbarProps {
  onViewChange: (view: 'main' | 'student-results') => void
  currentView: 'main' | 'student-results'
}

export default function Navbar({ onViewChange, currentView }: NavbarProps) {
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
      </div>
    </header>
  )
}
