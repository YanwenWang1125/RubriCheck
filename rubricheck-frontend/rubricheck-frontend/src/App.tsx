import Navbar from './components/Navbar'
import UploadRubric from './pages/UploadRubric'
import UploadEssay from './pages/UploadEssay'
import RunEvaluation from './pages/RunEvaluation'
import Results from './pages/Results'

export default function App() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8 space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <UploadRubric />
          <UploadEssay />
        </div>
        <RunEvaluation />
        <Results />
        <footer className="text-xs text-gray-500 py-8">
          <div className="mx-auto max-w-6xl">RubriCheck · Frontend (React + Vite + Tailwind). Configure <code>.env</code> → <code>VITE_API_BASE_URL</code>.</div>
        </footer>
      </main>
    </div>
  )
}
