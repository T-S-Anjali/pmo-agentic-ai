import { create } from 'zustand'
import type { WorkflowStatus } from '../services/api'

interface WorkflowStore {
  activeWorkflows: WorkflowStatus[]
  selectedWorkflowId: string | null
  setSelectedWorkflow: (id: string | null) => void
  upsertWorkflow: (wf: WorkflowStatus) => void
  clearWorkflows: () => void
}

export const useWorkflowStore = create<WorkflowStore>((set) => ({
  activeWorkflows: [],
  selectedWorkflowId: null,
  setSelectedWorkflow: (id) => set({ selectedWorkflowId: id }),
  upsertWorkflow: (wf) =>
    set((state) => {
      const existing = state.activeWorkflows.findIndex((w) => w.id === wf.id)
      if (existing >= 0) {
        const updated = [...state.activeWorkflows]
        updated[existing] = wf
        return { activeWorkflows: updated }
      }
      return { activeWorkflows: [...state.activeWorkflows, wf] }
    }),
  clearWorkflows: () => set({ activeWorkflows: [] }),
}))
