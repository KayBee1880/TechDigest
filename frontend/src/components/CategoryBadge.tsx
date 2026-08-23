const CATEGORY_STYLES: Record<string, string> = {
  'AI & Machine Learning':
    'bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300',
  Security: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  'Web Development': 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',
  'Systems & Infrastructure': 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300',
  Mobile: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
  'Data & Databases': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300',
  'Programming Languages': 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300',
  Hardware: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  Other: 'bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-400',
}

const DEFAULT_STYLE = 'bg-stone-100 text-stone-700 dark:bg-stone-800 dark:text-stone-400'

export function CategoryBadge({ category }: { category: string | null }) {
  if (!category) return null

  const style = CATEGORY_STYLES[category] ?? DEFAULT_STYLE

  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {category}
    </span>
  )
}
