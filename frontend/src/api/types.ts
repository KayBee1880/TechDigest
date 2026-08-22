export interface ArticleSource {
  id: number
  name: string
}

export interface Summary {
  content: string
  provider: string
}

export interface Article {
  id: number
  title: string
  url: string
  category: string | null
  published_at: string
  summary_status: 'pending' | 'completed' | 'failed' | 'unavailable'
  source: ArticleSource
  summary: Summary | null
}

export interface Paginated<T> {
  items: T[]
  page: number
  per_page: number
  total: number
  pages: number
}

export interface User {
  id: number
  email: string
  created_at: string
}

export interface Bookmark {
  id: number
  created_at: string
  article: Article
}

export interface AuthResponse {
  user: User
  token: string
}
