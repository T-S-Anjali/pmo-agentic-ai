import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import DashboardPage from './pages/DashboardPage'
import WorkflowPage from './pages/WorkflowPage'
import ApprovalsPage from './pages/ApprovalsPage'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30_000 } },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/workflows/:workflowId" element={<WorkflowPage />} />
          <Route path="/approvals" element={<ApprovalsPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
