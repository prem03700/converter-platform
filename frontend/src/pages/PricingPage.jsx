import { Link } from 'react-router-dom'
import { CheckCircle2 } from 'lucide-react'
import Navbar from '../components/Navbar'

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    cta: 'Get started',
    to: '/register',
    features: [
      '5 conversions / day',
      'Files up to 25 MB',
      'All format categories',
      'Community support',
    ],
    highlight: false,
  },
  {
    name: 'Pro',
    price: '$9',
    period: 'per month',
    cta: 'Start Pro — coming soon',
    to: '/register',
    features: [
      'Unlimited conversions',
      'Files up to 200 MB',
      'AI features (OCR, summarise, translate)',
      'Batch upload',
      'Priority processing',
      'Email support',
    ],
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'contact us',
    cta: 'Contact sales',
    to: 'mailto:sales@example.com',
    features: [
      'Everything in Pro',
      'On-premise deployment',
      'API access with high rate limits',
      'SSO / SAML',
      'SLA & dedicated support',
      'Custom conversion engines',
    ],
    highlight: false,
  },
]

export default function PricingPage() {
  return (
    <div className="min-h-screen dark:bg-surface-dark bg-slate-50">
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-20 space-y-12">
        <div className="text-center space-y-3">
          <h1 className="text-4xl font-extrabold dark:text-white text-slate-900">
            Simple, honest pricing
          </h1>
          <p className="dark:text-slate-400 text-slate-500">
            Start for free. Upgrade when you need more power.
          </p>
        </div>

        <div className="grid sm:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`relative flex flex-col rounded-2xl p-6 border ${
                plan.highlight
                  ? 'border-brand-500/60 bg-brand-gradient shadow-glow'
                  : 'dark:border-white/10 border-slate-200 dark:glass-card glass-card-light'
              }`}
            >
              {plan.highlight && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 text-xs font-bold
                  bg-white text-brand-600 rounded-full shadow">
                  Most popular
                </span>
              )}
              <div className="mb-6">
                <p className={`text-sm font-semibold mb-1 ${plan.highlight ? 'text-white/80' : 'dark:text-slate-400 text-slate-500'}`}>
                  {plan.name}
                </p>
                <div className="flex items-end gap-1">
                  <span className={`text-4xl font-extrabold ${plan.highlight ? 'text-white' : 'dark:text-white text-slate-900'}`}>
                    {plan.price}
                  </span>
                  <span className={`text-sm mb-1 ${plan.highlight ? 'text-white/60' : 'dark:text-slate-500 text-slate-400'}`}>
                    {plan.period}
                  </span>
                </div>
              </div>

              <ul className="flex-1 space-y-3 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5">
                    <CheckCircle2 className={`w-4 h-4 shrink-0 mt-0.5 ${plan.highlight ? 'text-white' : 'text-brand-400'}`} />
                    <span className={`text-sm ${plan.highlight ? 'text-white/90' : 'dark:text-slate-300 text-slate-600'}`}>
                      {f}
                    </span>
                  </li>
                ))}
              </ul>

              <Link
                to={plan.to}
                className={`text-center text-sm font-semibold py-2.5 rounded-xl transition-all ${
                  plan.highlight
                    ? 'bg-white text-brand-600 hover:bg-blue-50'
                    : 'btn-ghost dark:text-slate-300'
                }`}
              >
                {plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
