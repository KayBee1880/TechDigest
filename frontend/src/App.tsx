import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ArticleDetailPage } from './pages/ArticleDetailPage'
import { FeedPage } from './pages/FeedPage'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { SavedPage } from './pages/SavedPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<FeedPage />} />
          <Route path="articles/:id" element={<ArticleDetailPage />} />
          <Route path="saved" element={<SavedPage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="register" element={<RegisterPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
