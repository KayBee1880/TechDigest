import { useQuery } from '@tanstack/react-query'
import { apiRequest } from './client'
import type { Article, Paginated } from './types'

interface ListArticlesParams {
  page?: number
  per_page?: number
  source_id?: number
  q?: string
}

function buildQueryString(params: object): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }
  const query = search.toString()
  return query ? `?${query}` : ''
}

export function fetchArticles(params: ListArticlesParams = {}): Promise<Paginated<Article>> {
  return apiRequest(`/articles${buildQueryString(params)}`)
}

export function fetchArticle(id: number): Promise<Article> {
  return apiRequest(`/articles/${id}`)
}

export function useArticles(params: ListArticlesParams = {}) {
  return useQuery({
    queryKey: ['articles', params],
    queryFn: () => fetchArticles(params),
  })
}

export function useArticle(id: number) {
  return useQuery({
    queryKey: ['article', id],
    queryFn: () => fetchArticle(id),
    enabled: Number.isFinite(id),
  })
}
