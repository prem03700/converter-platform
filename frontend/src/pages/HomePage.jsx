import { Link } from 'react-router-dom'
import {
  FileText, Image, Music, Video, Archive, BookOpen,
  Code, Zap, Shield, Cpu, ArrowRight, CheckCircle2
} from 'lucide-react'
import Navbar from '../components/Navbar'
import UploadCard from '../components/UploadCard'
import { useAuth } from '../context/AuthContext'

const CATEGORIES = [
  { icon: FileText, label: 'Documents', formats: ['PDF', 'DOCX', 'TXT', 'Markdown', 'HTML', 'ODT'] },
  { icon: Image,    label: 'Images',    formats: ['PNG', 'JPG', 'WEBP', 'GIF', 'SVG', 'ICO'] },
  { icon: Music,    label: 'Audio',     formats: ['MP3', 'WAV', 'AAC', 'FLAC', 'OGG'] },
  { icon: Video,    label: 'Video',     formats: ['MP4', 'AVI', 'MOV', 'MKV', 'WEBM'] },
  { icon: Archive,  label: 'Archives',  formats: ['ZIP', 'TAR', 'GZ', '7Z'] },
  { icon: BookOpen, label: 'Ebooks',    formats: ['EPUB', 'MOBI', 'AZW3'] },
  { icon: Code,     label: 'Code/Data', formats: ['JSON', 'YAML', 'XML', 'Python', 'JS'] },
]

const FEATURES = [
  { icon: Zap,         title: 'Lightning fast',     desc: 'Files processed in seconds using optimised native engines.' },
  { icon: Shield,      title: 'Secure by default',  desc: 'Every upload is validated, scanned, and encrypted in transit.' },
  { icon: Cpu,         title: 'AI-powered cleanup', desc: 'Optional AI post-processing: OCR, summarise, extract tables, translate.' },
]

export default function HomePage() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />

      {/* Hero */}
      <section className="relative overflow-hidden py-24 px-4 text-center">
        {/* Background decoration */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-brand-500/10 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-3xl mx-auto space-y-6">
          <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold
            bg-brand-500/20 text-brand-400 border border-brand-500/30 mb-2">
            Free · No signup required for basic conversions
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight dark:text-white text-slate-900">
            Convert any file<br />
            <span className="bg-brand-gradient bg-clip-text text-transparent">intelligently</span>
          </h1>
          <p className="text-lg dark:text-slate-400 text-slate-600 max-w-xl mx-auto">
            Universal AI File Converter handles documents, images, audio, video, archives,
            ebooks, and code — powered by best-in-class open-source engines.
          </p>

          <div className="flex flex-wrap justify-center gap-3 pt-2">
            {user ? (
              <Link to="/dashboard" className="btn-primary flex items-center gap-2">
                Open Dashboard <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn-primary flex items-center gap-2">
                  Get started free <ArrowRight className="w-4 h-4" />
                </Link>
                <Link to="/login" className="btn-ghost dark:text-slate-300 text-slate-600">
                  Sign in
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Quick upload (for logged-in users right on the landing page) */}
      {user && (
        <section className="max-w-2xl mx-auto px-4 pb-16">
          <UploadCard />
        </section>
      )}

      {/* Supported formats */}
      <section className="max-w-6xl mx-auto px-4 pb-20">
        <h2 className="text-2xl font-bold dark:text-white text-slate-900 text-center mb-10">
          Supported formats
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {CATEGORIES.map(({ icon: Icon, label, formats }) => (
            <div key={label} className="dark:glass-card glass-card-light p-4 space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-brand-gradient flex items-center justify-center">
                  <Icon className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="text-sm font-semibold dark:text-white text-slate-900">{label}</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {formats.map((f) => (
                  <span key={f} className="px-2 py-0.5 text-xs rounded dark:bg-white/10 bg-slate-100
                    dark:text-slate-300 text-slate-600 font-mono">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto px-4 pb-24">
        <div className="grid sm:grid-cols-3 gap-6">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="dark:glass-card glass-card-light p-6 space-y-3">
              <div className="w-10 h-10 rounded-xl bg-brand-gradient flex items-center justify-center">
                <Icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="font-semibold dark:text-white text-slate-900">{title}</h3>
              <p className="text-sm dark:text-slate-400 text-slate-600">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t dark:border-white/10 border-slate-200 py-8 text-center text-sm dark:text-slate-500 text-slate-400">
        <p>© {new Date().getFullYear()} Universal AI File Converter. Built with FastAPI + React.</p>
      </footer>
    </div>
  )
}
