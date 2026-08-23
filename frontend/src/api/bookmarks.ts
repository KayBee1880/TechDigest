import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiRequest } from './client'
import type { Bookmark, Paginated } from './types'

export function fetchBookmarks(token: string, page = 1, perPage = 20): Promise<Paginated<Bookmark>> {
  return apiRequest(`/bookmarks?page=${page}&per_page=${perPage}`, { token })
}

export function createBookmark(token: string, articleId: number): Promise<Bookmark> {
  return apiRequest('/bookmarks', { method: 'POST', body: { article_id: articleId }, token })
}

export function updateBookmarkNotes(
  token: string,
  bookmarkId: number,
  notes: string,
): Promise<Bookmark> {
  return apiRequest(`/bookmarks/${bookmarkId}`, { method: 'PATCH', body: { notes }, token })
}

export function deleteBookmark(token: string, bookmarkId: number): Promise<void> {
  return apiRequest(`/bookmarks/${bookmarkId}`, { method: 'DELETE', token })
}

export function useBookmarks(token: string | null, perPage = 20) {
  return useQuery({
    queryKey: ['bookmarks', perPage],
    queryFn: () => fetchBookmarks(token as string, 1, perPage),
    enabled: Boolean(token),
  })
}

export function useCreateBookmark(token: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (articleId: number) => createBookmark(token as string, articleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookmarks'] }),
  })
}

export function useUpdateBookmarkNotes(token: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ bookmarkId, notes }: { bookmarkId: number; notes: string }) =>
      updateBookmarkNotes(token as string, bookmarkId, notes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookmarks'] }),
  })
}

export function useDeleteBookmark(token: string | null) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (bookmarkId: number) => deleteBookmark(token as string, bookmarkId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['bookmarks'] }),
  })
}
