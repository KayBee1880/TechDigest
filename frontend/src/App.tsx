import { useArticles } from './api/articles'

function App() {
  const { data, isLoading, isError, error } = useArticles({ per_page: 5 })

  return (
    <div className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <h1 className="mb-4 text-2xl font-semibold">TechDigest — API check</h1>

      {isLoading && <p>Loading articles…</p>}
      {isError && <p className="text-red-400">Error: {error.message}</p>}

      {data && (
        <ul className="space-y-2">
          {data.items.map((article) => (
            <li key={article.id} className="rounded border border-slate-800 p-3">
              <p className="font-medium">{article.title}</p>
              <p className="text-sm text-slate-400">
                {article.source.name} — {article.summary_status}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default App
