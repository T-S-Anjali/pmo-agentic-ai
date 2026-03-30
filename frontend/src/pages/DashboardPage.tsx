import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { workflowApi, WorkflowStartRequest } from '../services/api';

export default function DashboardPage() {
  const navigate = useNavigate();

  const startMutation = useMutation({
    mutationFn: (request: WorkflowStartRequest) => workflowApi.start(request),
    onSuccess: (response) => {
      const data = response.data;
      navigate(`/workflows/${data.workflow_id}`);
    },
    onError: (error) => {
      console.error('Failed to start workflow:', error);
      alert('Failed to start workflow. Check console for details.');
    }
  });

  const handleStart = (type: WorkflowStartRequest['workflow_type']) => {
    startMutation.mutate({
      workflow_type: type,
      input_payload: { project_name: "New PMO Project" },
      user_context: { user_id: 'u1', role: 'pm' }
    });
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-extrabold mb-4">PMO Dashboard</h1>
      <p className="text-secondary mb-8">Welcome to the PMO Agentic AI command center.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-2xl shadow-sm border border-border">
          <h2 className="text-xl font-bold mb-2">Project Intake</h2>
          <p className="text-sm text-secondary mb-4">Initiate new projects and generate charters automatically.</p>
          <button 
            onClick={() => handleStart('project_intake_to_charter')}
            disabled={startMutation.isPending}
            className="bg-accent text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
          >
            {startMutation.isPending ? 'Starting...' : 'Start Workflow'}
          </button>
        </div>
        <div className="glass p-6 rounded-2xl shadow-sm border border-border">
          <h2 className="text-xl font-bold mb-2">Status Reporting</h2>
          <p className="text-sm text-secondary mb-4">Generate weekly status reports from various inputs.</p>
          <button 
            onClick={() => handleStart('weekly_status_report')}
            disabled={startMutation.isPending}
            className="bg-accent text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
          >
            {startMutation.isPending ? 'Starting...' : 'Start Workflow'}
          </button>
        </div>
        <div className="glass p-6 rounded-2xl shadow-sm border border-border">
          <h2 className="text-xl font-bold mb-2">RAID Registry</h2>
          <p className="text-sm text-secondary mb-4">Extract and update risks, actions, issues, and decisions.</p>
          <button 
            onClick={() => handleStart('raid_update')}
            disabled={startMutation.isPending}
            className="bg-accent text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
          >
            {startMutation.isPending ? 'Starting...' : 'Start Workflow'}
          </button>
        </div>
      </div>
    </div>
  );
}
