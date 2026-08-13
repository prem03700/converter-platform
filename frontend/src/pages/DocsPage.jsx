import Navbar from '../components/Navbar'

const SECTIONS = [
  {
    title: 'Authentication',
    base: '/api/v1/auth',
    endpoints: [
      { method: 'POST', path: '/register',       desc: 'Create a new account. Returns access + refresh tokens.' },
      { method: 'POST', path: '/login',           desc: 'Exchange email+password for tokens.' },
      { method: 'POST', path: '/refresh',         desc: 'Get a new access token using a refresh token.' },
      { method: 'POST', path: '/logout',          desc: 'Invalidate the current session (client-side).' },
      { method: 'POST', path: '/forgot-password', desc: 'Request a password reset link (email delivery required).' },
    ],
  },
  {
    title: 'Files',
    base: '/api/v1/files',
    endpoints: [
      { method: 'POST',   path: '/upload',                   desc: 'Upload a single file. Returns file metadata.' },
      { method: 'POST',   path: '/upload-multiple',          desc: 'Upload multiple files at once.' },
      { method: 'GET',    path: '',                          desc: 'List uploaded files (paginated with ?skip&limit).' },
      { method: 'GET',    path: '/{file_id}/download',       desc: 'Download the original uploaded file.' },
      { method: 'GET',    path: '/{file_id}/preview',        desc: 'Inline preview for images and PDFs.' },
      { method: 'DELETE', path: '/{file_id}',                desc: 'Delete a file and its storage object.' },
    ],
  },
  {
    title: 'Conversions',
    base: '/api/v1/convert',
    endpoints: [
      { method: 'GET',  path: '/supported-targets/{file_id}', desc: 'List valid target formats for an uploaded file.' },
      { method: 'POST', path: '',                              desc: 'Start a conversion. Returns a conversion job object.' },
      { method: 'GET',  path: '/{id}/status',                 desc: 'Poll conversion status and progress.' },
      { method: 'POST', path: '/{id}/cancel',                 desc: 'Cancel a pending or processing job.' },
      { method: 'GET',  path: '/{id}/download',               desc: 'Download the converted output file.' },
    ],
  },
  {
    title: 'History & Stats',
    base: '/api/v1',
    endpoints: [
      { method: 'GET', path: '/history',       desc: 'Paginated list of past conversions.' },
      { method: 'GET', path: '/history/stats', desc: 'Aggregated stats: counts, storage, favourite formats.' },
    ],
  },
  {
    title: 'AI Features',
    base: '/api/v1/ai',
    endpoints: [
      { method: 'POST', path: '/ocr/image-to-text',   desc: 'Extract text from an image file via Tesseract OCR.' },
      { method: 'POST', path: '/ocr/searchable-pdf',  desc: 'Add invisible OCR text layer to a scanned PDF.' },
      { method: 'POST', path: '/summarize',            desc: 'Summarise a document (requires ANTHROPIC_API_KEY).' },
      { method: 'POST', path: '/tags',                 desc: 'Generate topical tags for a document.' },
      { method: 'POST', path: '/keywords',             desc: 'Extract keywords from a document.' },
      { method: 'POST', path: '/headings',             desc: 'Extract heading/section outline as Markdown.' },
      { method: 'POST', path: '/metadata',             desc: 'Generate title, author, summary, and topics as JSON.' },
      { method: 'POST', path: '/translate',            desc: 'Translate a document into a target language.' },
    ],
  },
]

const METHOD_COLOR = {
  GET:    'bg-blue-500/20 text-blue-300',
  POST:   'bg-green-500/20 text-green-300',
  PATCH:  'bg-yellow-500/20 text-yellow-300',
  DELETE: 'bg-red-500/20 text-red-300',
}

export default function DocsPage() {
  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 py-12 space-y-10">
        <div>
          <h1 className="text-3xl font-extrabold dark:text-white text-slate-900">API Documentation</h1>
          <p className="dark:text-slate-400 text-slate-500 mt-2 text-sm">
            All endpoints are under <code className="dark:bg-white/10 bg-slate-100 px-1.5 py-0.5 rounded text-xs">/api/v1</code> and
            require a Bearer token except for the auth endpoints.
            Interactive docs are also available at{' '}
            <a href="/docs" className="text-brand-400 hover:underline">/docs</a>
            {' '}(Swagger) and <a href="/redoc" className="text-brand-400 hover:underline">/redoc</a>.
          </p>
        </div>

        {SECTIONS.map((section) => (
          <section key={section.title} className="space-y-3">
            <h2 className="text-lg font-bold dark:text-white text-slate-900 flex items-center gap-2">
              {section.title}
              <code className="text-xs font-mono dark:bg-white/10 bg-slate-100 px-2 py-0.5 rounded dark:text-slate-300 text-slate-600">
                {section.base}
              </code>
            </h2>
            <div className="dark:glass-card glass-card-light divide-y dark:divide-white/10 divide-slate-100 overflow-hidden">
              {section.endpoints.map((ep) => (
                <div key={ep.path} className="flex items-start gap-4 px-5 py-4">
                  <span className={`shrink-0 text-xs font-bold font-mono px-2 py-0.5 rounded ${METHOD_COLOR[ep.method]}`}>
                    {ep.method}
                  </span>
                  <div className="min-w-0">
                    <code className="text-sm dark:text-slate-200 text-slate-800 break-all">
                      {section.base}{ep.path}
                    </code>
                    <p className="text-xs dark:text-slate-400 text-slate-500 mt-0.5">{ep.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        ))}
      </main>
    </div>
  )
}
