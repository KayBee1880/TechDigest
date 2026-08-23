import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useBookmarks, useDeleteBookmark, useUpdateBookmarkNotes } from '../api/bookmarks'
import { useAuth } from '../auth/useAuth'
import { CategoryBadge } from '../components/CategoryBadge'
import type { Bookmark } from '../api/types'

function SavedBookmarkItem({ bookmark }: { bookmark: Bookmark }) {
  const { token } = useAuth()
  const updateNotes = useUpdateBookmarkNotes(token)
  const deleteBookmark = useDeleteBookmark(token)
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(bookmark.notes ?? '')

  function handleSave() {
    updateNotes.mutate(
      { bookmarkId: bookmark.id, notes: draft },
      { onSuccess: () => setIsEditing(false) },
    )
  }

  return (
    <li className="py-4 first:pt-0">
      <div className="flex items-center justify-between gap-4">
        <div>
          {bookmark.article.category && (
            <div className="mb-1">
              <CategoryBadge category={bookmark.article.category} />
            </div>
          )}
          <Link to={`/articles/${bookmark.article.id}`} className="font-medium hover:underline">
            {bookmark.article.title}
          </Link>
        </div>
        <button
          type="button"
          onClick={() => deleteBookmark.mutate(bookmark.id)}
          disabled={deleteBookmark.isPending}
          className="shrink-0 text-sm text-red-600 hover:underline disabled:opacity-50 dark:text-red-400"
        >
          Remove
        </button>
      </div>

      {isEditing ? (
        <div className="mt-2 space-y-2">
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Why did you save this?"
            rows={3}
            className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm placeholder:text-stone-400 focus:border-stone-500 focus:outline-none dark:border-stone-700 dark:bg-stone-900 dark:placeholder:text-stone-500"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleSave}
              disabled={updateNotes.isPending}
              className="rounded-md border border-stone-300 px-3 py-1 text-sm hover:bg-stone-100 disabled:opacity-50 dark:border-stone-700 dark:hover:bg-stone-900"
            >
              Save note
            </button>
            <button
              type="button"
              onClick={() => {
                setDraft(bookmark.notes ?? '')
                setIsEditing(false)
              }}
              className="text-sm text-stone-500 hover:underline dark:text-stone-400"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : bookmark.notes ? (
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="mt-2 block text-left text-sm text-stone-600 hover:underline dark:text-stone-400"
        >
          {bookmark.notes}
        </button>
      ) : (
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="mt-2 text-sm text-stone-500 underline hover:text-stone-700 dark:text-stone-500 dark:hover:text-stone-300"
        >
          + Add a note
        </button>
      )}
    </li>
  )
}

export function SavedPage() {
  const { token } = useAuth()
  const { data, isLoading, isError, error } = useBookmarks(token)

  if (!token) {
    return (
      <p className="px-6 py-10 text-stone-600 dark:text-stone-400">
        You need to{' '}
        <Link to="/login" className="text-stone-900 underline dark:text-stone-100">
          log in
        </Link>{' '}
        to see saved articles.
      </p>
    )
  }

  if (isLoading) return <p className="px-6 py-10 text-stone-500 dark:text-stone-400">Loading…</p>
  if (isError)
    return <p className="px-6 py-10 text-red-600 dark:text-red-400">Error: {error.message}</p>

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <h1 className="mb-6 font-serif text-3xl font-semibold tracking-tight">Saved</h1>
      {data?.items.length === 0 && (
        <p className="text-stone-500 dark:text-stone-400">No saved articles yet.</p>
      )}
      <ul className="divide-y divide-stone-200 dark:divide-stone-800">
        {data?.items.map((bookmark) => (
          <SavedBookmarkItem key={bookmark.id} bookmark={bookmark} />
        ))}
      </ul>
    </div>
  )
}
