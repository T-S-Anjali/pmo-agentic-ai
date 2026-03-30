import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { workflowApi } from '../services/api';
import { CheckCircle2, Clock, AlertCircle, ArrowLeft } from 'lucide-react';

export default function WorkflowPage() {
  const { workflowId } = useParams<{ workflowId: string }>();

  const { data: response, isLoading, error } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => workflowApi.getStatus(workflowId!),
    enabled: !!workflowId,
    refetchInterval: (query) => {
      const status = query.state.data?.data.status;
      return (status === 'completed' || status === 'failed' || status === 'awaiting_review') ? false : 3000;
    }
  });

  const workflow = response?.data;

  if (isLoading) {
    return <div className="p-8 font-medium animate-pulse">Loading status...</div>;
  }

  if (error || !workflow) {
    return (
      <div className="p-8 text-red-500">
        <h2 className="text-xl font-bold mb-2">Error Loading Workflow</h2>
        <p>Could not find or load workflow data for {workflowId}.</p>
        <Link to="/" className="text-accent mt-4 inline-block underline">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <Link to="/" className="flex items-center text-sm text-secondary hover:text-foreground mb-6 transition-colors">
        <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
      </Link>

      <header className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-extrabold">{workflow.workflow_type.replace(/_/g, ' ')}</h1>
          <StatusBadge status={workflow.status} />
        </div>
        <p className="text-secondary">ID: <span className="font-mono text-xs">{workflow.id}</span></p>
      </header>
      
      <div className="glass p-8 rounded-2xl border border-border">
        <h3 className="text-lg font-bold mb-6">Execution Log</h3>
        
        <div className="space-y-6">
          <LogItem 
            title="Workflow Started" 
            time={new Date(workflow.created_at).toLocaleTimeString()} 
            status="completed" 
          />
          
          <LogItem 
            title="Agent Processing" 
            time={workflow.status === 'pending' ? '--' : 'In Progress'} 
            status={workflow.status === 'pending' ? 'pending' : 'active'} 
          />

          {workflow.status === 'awaiting_review' && (
            <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-xl flex items-center justify-between">
              <span className="text-blue-700 font-medium">Artifact ready for review</span>
              <Link to="/approvals" className="bg-accent text-white px-4 py-2 rounded-lg text-sm font-bold">Open Approval Portal</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    pending: 'bg-slate-100 text-slate-700',
    running: 'bg-blue-100 text-blue-700',
    awaiting_review: 'bg-amber-100 text-amber-700',
    completed: 'bg-emerald-100 text-emerald-700',
    failed: 'bg-red-100 text-red-700',
  };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${colors[status] || colors.pending}`}>
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function LogItem({ title, time, status }: { title: string, time: string, status: 'completed' | 'active' | 'pending' }) {
  return (
    <div className="flex items-start">
      <div className="mr-4 mt-1">
        {status === 'completed' && <CheckCircle2 className="h-5 w-5 text-emerald-500" />}
        {status === 'active' && <Clock className="h-5 w-5 text-accent animate-spin" />}
        {status === 'pending' && <Clock className="h-5 w-5 text-slate-300" />}
      </div>
      <div>
        <h4 className="font-bold text-sm">{title}</h4>
        <p className="text-xs text-secondary">{time}</p>
      </div>
    </div>
  );
}
