import { Link } from 'react-router-dom'
import { useBookmarks, useDeleteBookmark } from '../api/bookmarks'
import { useAuth } from '../auth/useAuth'

export function SavedPage() {
  const { token } = useAuth()
  const { data, isLoading, isError, error } = useBookmarks(token)
  const deleteBookmark = useDeleteBookmark(token)

  if (!token) {
    return (
      <p className="p-6">
        You need to{' '}
        <Link to="/login" className="text-sky-400 hover:underline">
          log in
        </Link>{' '}
        to see saved articles.
      </p>
    )
  }

  if (isLoading) return <p className="p-6">Loading…</p>
  if (isError) return <p className="p-6 text-red-400">Error: {error.message}</p>

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-2xl font-semibold">Saved</h1>
      {data?.items.length === 0 && <p className="text-slate-400">No saved articles yet.</p>}
      <ul className="space-y-3">
        {data?.items.map((bookmark) => (
          <li
            key={bookmark.id}
            className="flex items-center justify-between rounded border border-slate-800 p-4"
          >
            <Link to={`/articles/${bookmark.article.id}`} className="font-medium hover:underline">
              {bookmark.article.title}
            </Link>
            <button
              onClick={() => deleteBookmark.mutate(bookmark.id)}
              disabled={deleteBookmark.isPending}
              className="text-sm text-red-400 hover:underline disabled:opacity-50"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
