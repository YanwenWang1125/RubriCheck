import { Rocket, Upload, FileText, BarChart2 } from 'lucide-react'

export default function Navbar() {
  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur border-b border-gray-100">
      <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Rocket className="h-6 w-6 text-primary-600" />
          <span className="font-semibold">RubriCheck</span>
        </div>
        <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
          <a className="hover:text-gray-900 inline-flex items-center gap-1" href="#rubric"><Upload className="h-4 w-4" />Rubric</a>
          <a className="hover:text-gray-900 inline-flex items-center gap-1" href="#essay"><FileText className="h-4 w-4" />Essay</a>
          <a className="hover:text-gray-900 inline-flex items-center gap-1" href="#results"><BarChart2 className="h-4 w-4" />Results</a>
        </nav>
      </div>
    </header>
  )
}
