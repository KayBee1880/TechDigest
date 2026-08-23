import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useArticles, useCategories } from '../api/articles'
import { CategoryBadge } from '../components/CategoryBadge'

export function FeedPage() {
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const [category, setCategory] = useState('')
  const { data: categories } = useCategories()
  const { data, isLoading, isError, error } = useArticles({
    page,
    per_page: 10,
    q: q || undefined,
    category: category || undefined,
  })

  function selectCategory(next: string) {
    setCategory(next)
    setPage(1)
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="mb-6 font-serif text-3xl font-semibold tracking-tight">Feed</h1>

      <div className="mb-8 space-y-4">
        <input
          type="search"
          placeholder="Search articles…"
          value={q}
          onChange={(event) => {
            setQ(event.target.value)
            setPage(1)
          }}
          className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm placeholder:text-stone-400 focus:border-stone-500 focus:outline-none dark:border-stone-700 dark:bg-stone-900 dark:placeholder:text-stone-500"
        />

        {categories && categories.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => selectCategory('')}
              className={
                category === ''
                  ? 'rounded-full border border-stone-900 bg-stone-900 px-3 py-1 text-xs font-medium text-white dark:border-stone-100 dark:bg-stone-100 dark:text-stone-900'
                  : 'rounded-full border border-stone-300 px-3 py-1 text-xs font-medium text-stone-600 hover:border-stone-400 dark:border-stone-700 dark:text-stone-400'
              }
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => selectCategory(cat)}
                className={
                  category === cat
                    ? 'rounded-full border border-stone-900 bg-stone-900 px-3 py-1 text-xs font-medium text-white dark:border-stone-100 dark:bg-stone-100 dark:text-stone-900'
                    : 'rounded-full border border-stone-300 px-3 py-1 text-xs font-medium text-stone-600 hover:border-stone-400 dark:border-stone-700 dark:text-stone-400'
                }
              >
                {cat}
              </button>
            ))}
          </div>
        )}
      </div>

      {isLoading && <p className="text-stone-500 dark:text-stone-400">Loading…</p>}
      {isError && <p className="text-red-600 dark:text-red-400">Error: {error.message}</p>}

      {data && (
        <>
          {data.items.length === 0 && (
            <p className="text-stone-500 dark:text-stone-400">No articles found.</p>
          )}

          <ul className="divide-y divide-stone-200 dark:divide-stone-800">
            {data.items.map((article) => (
              <li key={article.id} className="py-6 first:pt-0">
                {article.category && (
                  <div className="mb-2">
                    <CategoryBadge category={article.category} />
                  </div>
                )}
                <Link
                  to={`/articles/${article.id}`}
                  className="font-serif text-xl font-semibold leading-snug hover:underline"
                >
                  {article.title}
                </Link>
                <p className="mt-1 text-sm text-stone-500 dark:text-stone-400">
                  {article.source.name} · {new Date(article.published_at).toLocaleDateString()}
                </p>
                {article.summary && (
                  <p className="mt-3 text-stone-700 dark:text-stone-300">
                    {article.summary.content}
                  </p>
                )}
              </li>
            ))}
          </ul>

          {data.pages > 1 && (
            <div className="mt-8 flex items-center justify-between border-t border-stone-200 pt-6 dark:border-stone-800">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => setPage((current) => current - 1)}
                className="rounded-md border border-stone-300 px-3 py-1.5 text-sm disabled:opacity-40 dark:border-stone-700"
              >
                Previous
              </button>
              <span className="text-sm text-stone-500 dark:text-stone-400">
                Page {data.page} of {data.pages}
              </span>
              <button
                type="button"
                disabled={page >= data.pages}
                onClick={() => setPage((current) => current + 1)}
                className="rounded-md border border-stone-300 px-3 py-1.5 text-sm disabled:opacity-40 dark:border-stone-700"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
