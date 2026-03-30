import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { approvalApi, WorkflowStatus } from '../services/api';
import { Check, X, Eye, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ApprovalsPage() {
  const queryClient = useQueryClient();
  const reviewerId = 'u1'; // Hardcoded for this scaffold

  const { data: response, isLoading } = useQuery({
    queryKey: ['approvals', reviewerId],
    queryFn: () => approvalApi.listPending(reviewerId),
  });

  const approvals = response?.data?.items || [];

  const decideMutation = useMutation({
    mutationFn: ({ id, decision }: { id: string, decision: 'approved' | 'rejected' }) => 
      approvalApi.decide(id, {
        checkpoint_name: 'human_review', // Default for MVP
        reviewer_decision: decision,
        reviewer_id: reviewerId,
        comments: 'Approved via PMO Portal'
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
    }
  });

  if (isLoading) return <div className="p-8 animate-pulse font-medium">Loading approvals...</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link to="/" className="flex items-center text-sm text-secondary hover:text-foreground mb-6 transition-colors">
        <ArrowLeft className="h-4 w-4 mr-1" /> Back to Dashboard
      </Link>

      <header className="mb-8">
        <h1 className="text-3xl font-extrabold mb-2">Approvals Portal</h1>
        <p className="text-secondary text-lg">Review and govern AI-generated project artifacts.</p>
      </header>

      {approvals.length === 0 ? (
        <div className="glass p-12 rounded-3xl border border-dashed border-border text-center">
          <p className="text-secondary font-medium">No pending approvals at this time.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {approvals.map((item: any) => (
            <div key={item.id} className="glass p-6 rounded-2xl border border-border flex items-center justify-between hover:border-accent transition-colors">
              <div className="flex items-center space-x-4">
                <div className="h-10 w-10 bg-blue-50 text-accent rounded-full flex items-center justify-center font-bold">
                  {item.workflow_type?.charAt(0).toUpperCase() || 'W'}
                </div>
                <div>
                  <h3 className="font-bold text-lg">{item.checkpoint_name.replace(/_/g, ' ')}</h3>
                  <p className="text-sm text-secondary">
                    Workflow: <span className="font-mono text-xs">{item.workflow_id}</span>
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <button className="p-2 text-secondary hover:text-foreground hover:bg-slate-100 rounded-lg transition-colors">
                  <Eye className="h-5 w-5" />
                </button>
                <div className="h-6 w-px bg-border mx-2"></div>
                <button 
                  onClick={() => decideMutation.mutate({ id: item.id, decision: 'rejected' })}
                  disabled={decideMutation.isPending}
                  className="px-4 py-2 border border-red-200 text-red-600 rounded-lg text-sm font-bold hover:bg-red-50 disabled:opacity-50"
                >
                  Reject
                </button>
                <button 
                  onClick={() => decideMutation.mutate({ id: item.id, decision: 'approved' })}
                  disabled={decideMutation.isPending}
                  className="px-4 py-2 bg-accent text-white rounded-lg text-sm font-bold hover:bg-blue-600 disabled:opacity-50 flex items-center"
                >
                  <Check className="h-4 w-4 mr-1" /> Approve
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
