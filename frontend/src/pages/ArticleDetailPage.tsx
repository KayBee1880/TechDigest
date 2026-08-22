import { Link, useParams } from 'react-router-dom'
import { useArticle } from '../api/articles'
import { useCreateBookmark } from '../api/bookmarks'
import { useAuth } from '../auth/AuthContext'
import type { Article } from '../api/types'

const NO_SUMMARY_MESSAGE: Record<Exclude<Article['summary_status'], 'completed'>, string> = {
  pending: 'Summarizing… check back shortly.',
  failed: 'Summarization failed after several attempts.',
  unavailable: 'No summary available — this source provided no article text to summarize.',
}

export function ArticleDetailPage() {
  const { id } = useParams()
  const articleId = Number(id)
  const { data: article, isLoading, isError, error } = useArticle(articleId)
  const { token } = useAuth()
  const createBookmark = useCreateBookmark(token)

  if (isLoading) return <p className="p-6">Loading…</p>
  if (isError) return <p className="p-6 text-red-400">Error: {error.message}</p>
  if (!article) return null

  return (
    <div className="mx-auto max-w-2xl p-6">
      <Link to="/" className="text-sm text-slate-400 hover:underline">
        ← Back to feed
      </Link>
      <h1 className="mt-2 text-2xl font-semibold">{article.title}</h1>
      <p className="mt-1 text-sm text-slate-400">
        {article.source.name} · {new Date(article.published_at).toLocaleDateString()}
      </p>

      {article.summary ? (
        <p className="mt-4 text-slate-200">{article.summary.content}</p>
      ) : (
        <p className="mt-4 italic text-slate-500">
          {NO_SUMMARY_MESSAGE[article.summary_status as Exclude<Article['summary_status'], 'completed'>]}
        </p>
      )}

      <div className="mt-6 flex gap-3">
        <a
          href={article.url}
          target="_blank"
          rel="noreferrer"
          className="rounded border border-slate-700 px-3 py-1.5 hover:bg-slate-800"
        >
          Read original
        </a>
        {token && (
          <button
            onClick={() => createBookmark.mutate(article.id)}
            disabled={createBookmark.isPending}
            className="rounded bg-sky-600 px-3 py-1.5 hover:bg-sky-500 disabled:opacity-50"
          >
            {createBookmark.isSuccess ? 'Saved' : 'Save for later'}
          </button>
        )}
      </div>
    </div>
  )
}
