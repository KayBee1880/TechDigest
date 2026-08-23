import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useArticle } from '../api/articles'
import { useBookmarks, useCreateBookmark, useUpdateBookmarkNotes } from '../api/bookmarks'
import { useAuth } from '../auth/useAuth'
import { CategoryBadge } from '../components/CategoryBadge'
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
  const { data: bookmarksData } = useBookmarks(token, 100)
  const createBookmark = useCreateBookmark(token)
  const updateNotes = useUpdateBookmarkNotes(token)

  const [showLoginPrompt, setShowLoginPrompt] = useState(false)
  const [showNoteInput, setShowNoteInput] = useState(false)
  const [noteDraft, setNoteDraft] = useState('')
  const [noteJustSaved, setNoteJustSaved] = useState(false)

  const existingBookmark = bookmarksData?.items.find((b) => b.article.id === articleId)
  const isSaved = Boolean(existingBookmark) || createBookmark.isSuccess
  const bookmarkId = existingBookmark?.id ?? createBookmark.data?.id
  const hasNote = Boolean(existingBookmark?.notes) || noteJustSaved

  if (isLoading) return <p className="px-6 py-10 text-stone-500 dark:text-stone-400">Loading…</p>
  if (isError)
    return <p className="px-6 py-10 text-red-600 dark:text-red-400">Error: {error.message}</p>
  if (!article) return null

  function handleSaveClick() {
    if (!token) {
      setShowLoginPrompt(true)
      return
    }
    createBookmark.mutate(article!.id)
  }

  function handleSaveNote() {
    if (!bookmarkId) return
    updateNotes.mutate(
      { bookmarkId, notes: noteDraft },
      {
        onSuccess: () => {
          setShowNoteInput(false)
          setNoteJustSaved(true)
        },
      },
    )
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/" className="text-sm text-stone-500 hover:underline dark:text-stone-400">
        ← Back to feed
      </Link>

      {article.category && (
        <div className="mt-4">
          <CategoryBadge category={article.category} />
        </div>
      )}

      <h1 className="mt-3 font-serif text-3xl font-semibold leading-tight tracking-tight">
        {article.title}
      </h1>
      <p className="mt-2 text-sm text-stone-500 dark:text-stone-400">
        {article.source.name} · {new Date(article.published_at).toLocaleDateString()}
      </p>

      {article.summary ? (
        <p className="mt-6 text-lg leading-relaxed text-stone-800 dark:text-stone-200">
          {article.summary.content}
        </p>
      ) : (
        <p className="mt-6 italic text-stone-500 dark:text-stone-500">
          {NO_SUMMARY_MESSAGE[article.summary_status as Exclude<Article['summary_status'], 'completed'>]}
        </p>
      )}

      <div className="mt-8 flex gap-3">
        <a
          href={article.url}
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-stone-300 px-4 py-2 text-sm hover:bg-stone-100 dark:border-stone-700 dark:hover:bg-stone-900"
        >
          Read original
        </a>
        <button
          type="button"
          onClick={handleSaveClick}
          disabled={createBookmark.isPending || isSaved}
          className="rounded-md bg-stone-900 px-4 py-2 text-sm text-white hover:bg-stone-700 disabled:opacity-50 dark:bg-stone-100 dark:text-stone-900 dark:hover:bg-stone-300"
        >
          {isSaved ? 'Saved' : 'Save for later'}
        </button>
      </div>

      {showLoginPrompt && !token && (
        <p className="mt-3 text-sm text-stone-500 dark:text-stone-400">
          <Link to="/login" className="underline">
            Log in
          </Link>{' '}
          or{' '}
          <Link to="/register" className="underline">
            create an account
          </Link>{' '}
          to save articles.
        </p>
      )}

      {token && isSaved && (
        <div className="mt-3">
          {showNoteInput ? (
            <div className="space-y-2">
              <textarea
                value={noteDraft}
                onChange={(event) => setNoteDraft(event.target.value)}
                placeholder="Why did you save this?"
                rows={3}
                className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm placeholder:text-stone-400 focus:border-stone-500 focus:outline-none dark:border-stone-700 dark:bg-stone-900 dark:placeholder:text-stone-500"
              />
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={handleSaveNote}
                  disabled={updateNotes.isPending}
                  className="rounded-md border border-stone-300 px-3 py-1.5 text-sm hover:bg-stone-100 disabled:opacity-50 dark:border-stone-700 dark:hover:bg-stone-900"
                >
                  Save note
                </button>
                <button
                  type="button"
                  onClick={() => setShowNoteInput(false)}
                  className="text-sm text-stone-500 hover:underline dark:text-stone-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : hasNote ? (
            <p className="text-sm text-stone-500 dark:text-stone-400">
              Note saved — edit it from the{' '}
              <Link to="/saved" className="underline">
                Saved
              </Link>{' '}
              page.
            </p>
          ) : (
            <button
              type="button"
              onClick={() => setShowNoteInput(true)}
              className="text-sm text-stone-500 underline hover:text-stone-700 dark:text-stone-400 dark:hover:text-stone-200"
            >
              + Add a note
            </button>
          )}
        </div>
      )}
    </div>
  )
}
