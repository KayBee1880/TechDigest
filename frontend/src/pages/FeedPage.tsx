import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useArticles } from '../api/articles'

export function FeedPage() {
  const [page, setPage] = useState(1)
  const [q, setQ] = useState('')
  const { data, isLoading, isError, error } = useArticles({
    page,
    per_page: 10,
    q: q || undefined,
  })

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-2xl font-semibold">Feed</h1>

      <input
        type="search"
        placeholder="Search articles…"
        value={q}
        onChange={(event) => {
          setQ(event.target.value)
          setPage(1)
        }}
        className="mb-6 w-full rounded border border-slate-800 bg-slate-900 p-2 text-slate-100"
      />

      {isLoading && <p>Loading…</p>}
      {isError && <p className="text-red-400">Error: {error.message}</p>}

      {data && (
        <>
          {data.items.length === 0 && <p className="text-slate-400">No articles found.</p>}

          <ul className="space-y-3">
            {data.items.map((article) => (
              <li key={article.id} className="rounded border border-slate-800 p-4">
                <Link to={`/articles/${article.id}`} className="text-lg font-medium hover:underline">
                  {article.title}
                </Link>
                <p className="text-sm text-slate-400">
                  {article.source.name} · {new Date(article.published_at).toLocaleDateString()}
                </p>
                {article.summary && <p className="mt-2 text-slate-300">{article.summary.content}</p>}
              </li>
            ))}
          </ul>

          {data.pages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <button
                disabled={page <= 1}
                onClick={() => setPage((current) => current - 1)}
                className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40"
              >
                Previous
              </button>
              <span className="text-sm text-slate-400">
                Page {data.page} of {data.pages}
              </span>
              <button
                disabled={page >= data.pages}
                onClick={() => setPage((current) => current + 1)}
                className="rounded border border-slate-700 px-3 py-1 disabled:opacity-40"
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
