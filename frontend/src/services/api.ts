/**
 * API service layer — wraps axios calls to the PMO backend.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// ── Types ─────────────────────────────────────────────────────────────

export interface UserContext {
  user_id: string
  role: string
}

export interface WorkflowStartRequest {
  workflow_type: 'project_intake_to_charter' | 'weekly_status_report' | 'raid_update'
  project_id?: string
  input_payload: Record<string, unknown>
  user_context: UserContext
}

export interface WorkflowStartResponse {
  workflow_id: string
  thread_id: string
  status: string
}

export interface WorkflowStatus {
  id: string
  thread_id: string
  workflow_type: string
  project_id: string | null
  status: string
  user_id: string
  user_role: string
  created_at: string
  updated_at: string
}

export interface ApprovalDecision {
  checkpoint_name: string
  reviewer_decision: 'approved' | 'rejected'
  reviewer_id: string
  comments?: string
}

// ── Workflow API ──────────────────────────────────────────────────────

export const workflowApi = {
  start: (body: WorkflowStartRequest) =>
    api.post<WorkflowStartResponse>('workflows/start', body),

  getStatus: (workflowId: string) =>
    api.get<WorkflowStatus>(`workflows/${workflowId}`),

  resume: (workflowId: string, body: ApprovalDecision) =>
    api.post(`workflows/${workflowId}/resume`, body),

  cancel: (workflowId: string) =>
    api.post(`workflows/${workflowId}/cancel`),
}

// ── Approval API ──────────────────────────────────────────────────────

export const approvalApi = {
  listPending: (reviewerId: string) =>
    api.get('approvals/pending', { params: { reviewer_id: reviewerId } }),

  decide: (approvalId: string, body: ApprovalDecision) =>
    api.post(`approvals/${approvalId}/decide`, body),
}

// ── Document API ──────────────────────────────────────────────────────

export const documentApi = {
  uploadProjectDocs: (files: File[]) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return api.post('documents/upload/project', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  uploadGovernanceDocs: (files: File[]) => {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    return api.post('documents/upload/governance', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
