import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />
      <div className="flex flex-col items-center justify-center py-32 px-4 text-center">
        <p className="text-7xl font-extrabold bg-brand-gradient bg-clip-text text-transparent mb-4">404</p>
        <h1 className="text-2xl font-bold dark:text-white text-slate-900 mb-2">Page not found</h1>
        <p className="dark:text-slate-400 text-slate-500 mb-8">
          The page you're looking for doesn't exist or was moved.
        </p>
        <Link to="/" className="btn-primary">Back to home</Link>
      </div>
    </div>
  )
}
