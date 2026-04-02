import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { workflowApi } from '../services/api';
import { CheckCircle2, Clock, AlertCircle, ArrowLeft, Cpu } from 'lucide-react';

export default function WorkflowPage() {
  const { workflowId } = useParams<{ workflowId: string }>();

  const { data: response, isLoading, error } = useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => workflowApi.getStatus(workflowId!),
    enabled: !!workflowId,
    refetchInterval: (query) => {
      const status = query.state.data?.data.status;
      return (status === 'completed' || status === 'failed' || status === 'awaiting_review') ? false : 3000;
    },
  });

  const workflow = response?.data;

  if (isLoading) {
    return (
      <>
        <div className="app-bg" />
        <div className="page-wrapper">
          <NavBar />
          <main className="main-content" style={{ paddingTop: '4rem' }}>
            <div style={{ color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Clock size={18} className="animate-spin" /> Loading workflow status…
            </div>
          </main>
        </div>
      </>
    );
  }

  if (error || !workflow) {
    return (
      <>
        <div className="app-bg" />
        <div className="page-wrapper">
          <NavBar />
          <main className="main-content" style={{ paddingTop: '4rem' }}>
            <div style={{ color: '#ff4d6a' }}>
              <h2 style={{ marginBottom: '0.5rem' }}>Error loading workflow</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                Could not find data for workflow: <code style={{ fontSize: '0.8rem' }}>{workflowId}</code>
              </p>
              <Link to="/" className="back-btn">
                <ArrowLeft size={14} /> Back to Dashboard
              </Link>
            </div>
          </main>
        </div>
      </>
    );
  }

  const statusClass: Record<string, string> = {
    pending: 'status-badge--waiting',
    running: 'status-badge--running',
    awaiting_review: 'status-badge--waiting',
    completed: 'status-badge--success',
    failed: 'status-badge--error',
  };

  return (
    <>
      <div className="app-bg" />
      <div className="page-wrapper">
        <NavBar />
        <main className="main-content">
          {/* Back link */}
          <Link to="/" className="back-btn" style={{ marginBottom: '2rem', display: 'inline-flex' }}>
            <ArrowLeft size={14} /> Back to Dashboard
          </Link>

          {/* Page header */}
          <div style={{ marginBottom: '2.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <h1 style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em', color: 'var(--text-primary)' }}>
                {workflow.workflow_type.replace(/_/g, ' ')}
              </h1>
              <span className={`status-badge ${statusClass[workflow.status] || 'status-badge--waiting'}`}>
                {workflow.status.replace(/_/g, ' ')}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
              ID: {workflow.id}
            </p>
          </div>

          {/* Execution log */}
          <div className="log-card">
            <h3 style={{ fontWeight: 700, marginBottom: '1.5rem', color: 'var(--text-primary)', fontSize: '1rem', letterSpacing: '-0.01em' }}>
              Execution Log
            </h3>

            <div className="log-item">
              <div className="log-icon log-icon--done">
                <CheckCircle2 size={14} />
              </div>
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Workflow Started</p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                  {new Date(workflow.created_at + (workflow.created_at.endsWith('Z') ? '' : 'Z')).toLocaleTimeString()}
                </p>
              </div>
            </div>

            <div className="log-item">
              <div className={`log-icon ${workflow.status === 'pending' ? 'log-icon--pending' : 'log-icon--running'}`}>
                <Clock size={14} className={workflow.status !== 'pending' && workflow.status !== 'completed' && workflow.status !== 'failed' ? 'animate-spin' : ''} />
              </div>
              <div>
                <p style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>Agent Processing</p>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                  {workflow.status === 'pending' ? 'Queued' : 'In Progress'}
                </p>
              </div>
            </div>

            {workflow.status === 'completed' && (
              <div className="log-item">
                <div className="log-icon log-icon--done">
                  <CheckCircle2 size={14} />
                </div>
                <div>
                  <p style={{ fontWeight: 600, fontSize: '0.9rem', color: '#4ddd88' }}>Completed Successfully</p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Workflow finished</p>
                </div>
              </div>
            )}

            {workflow.status === 'failed' && (
              <div className="log-item">
                <div className="log-icon" style={{ background: 'rgba(228,0,43,0.15)', color: '#ff4d6a' }}>
                  <AlertCircle size={14} />
                </div>
                <div>
                  <p style={{ fontWeight: 600, fontSize: '0.9rem', color: '#ff4d6a' }}>Workflow Failed</p>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Check logs for details</p>
                </div>
              </div>
            )}

            {workflow.status === 'awaiting_review' && (
              <div style={{
                marginTop: '1.5rem',
                padding: '1.25rem 1.5rem',
                borderRadius: '14px',
                background: 'rgba(79, 127, 255, 0.08)',
                border: '1px solid rgba(79, 127, 255, 0.25)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '1rem',
              }}>
                <div>
                  <p style={{ fontWeight: 600, color: '#7aa6ff', fontSize: '0.9rem' }}>📋 Artifact ready for PM review</p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    The charter draft is awaiting your approval before finalising.
                  </p>
                </div>
                <Link to="/approvals" style={{
                  background: 'linear-gradient(135deg, #4f7fff, #2d5dcc)',
                  color: '#fff',
                  padding: '0.65rem 1.25rem',
                  borderRadius: '10px',
                  textDecoration: 'none',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                }}>
                  Open Approval Portal →
                </Link>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
}

function NavBar() {
  return (
    <header className="navbar">
      <div className="navbar-brand">
        <svg 
          width="120" 
          height="24" 
          viewBox="0 0 340.16 69.52" 
          fill="var(--ntt-blue)" 
          xmlns="http://www.w3.org/2000/svg"
        >
          <path 
            fillRule="evenodd" 
            d="M45.64,0c-3.32,0-6.59.72-8.9,1.67-2.31-.95-5.58-1.67-8.9-1.67C13.21,0,0,13.84,0,32.82c0,20.7,16.91,36.7,36.74,36.7s36.74-16,36.74-36.7C73.48,13.84,60.27,0,45.64,0h0ZM36.74,11.27c2.82,1.68,6.54,6.54,6.54,12.02,0,4.02-2.65,7.19-6.54,7.19s-6.54-3.16-6.54-7.19c0-5.48,3.72-10.34,6.54-12.02h0ZM36.74,60.48c-15.17,0-27.71-12.2-27.71-27.84,0-14.28,10.31-24.04,18.41-23.68-3.84,3.82-6.16,9.39-6.16,14.79,0,9.27,7.36,15.77,15.47,15.77s15.47-6.5,15.47-15.77c0-5.39-2.33-10.96-6.16-14.79,8.1-.36,18.41,9.39,18.41,23.68,0,15.64-12.55,27.84-27.71,27.84Z" 
          />
          <g>
            <path d="M114.87,43.21c-.17-.33-11.08-21.59-12.42-23.68-1.54-2.42-3.41-4.1-7-4.1-3.33,0-7.28,1.48-7.28,9.48v26.87h8.05v-22.41c0-1.61-.1-3.99-.12-4.47-.02-.39,0-.77.2-.88.23-.13.46.08.62.38.16.3,10.27,20.3,12.42,23.68,1.54,2.42,3.41,4.1,7,4.1,3.33,0,7.28-1.48,7.28-9.48V15.83h-8.05v22.41c0,1.61.1,3.99.12,4.47.02.39,0,.77-.2.88-.23.13-.46-.08-.62-.38Z" />
            <path d="M126.39,15.84v7.56h11.53v28.38h8.16v-28.38h11.53v-7.56h-31.22Z" />
            <path d="M160.2,15.84v7.56h11.53v28.38h8.17v-28.38h11.53v-7.56h-31.23Z" />
            <path d="M235.1,39.18v-10.75c0-9.42-3.65-12.59-11.89-12.59h-21.86v35.93h22.24c8.74,0,11.51-4.34,11.51-12.59ZM226.76,39.34c0,3.44-1.16,4.78-4.1,4.78h-13.15v-20.63h13.15c2.93,0,4.1,1.34,4.1,4.78v11.07Z" />
            <path d="M260.76,15.84h-20.56v7.62h20.01c2.93,0,4.08,1.34,4.08,4.78v1.27h-16.58c-6.31,0-9.44,3.15-9.44,10.28v1.7c0,7.33,3.25,10.28,9.79,10.28h24.32v-23.62c0-9.05-2.99-12.31-11.62-12.31ZM248.91,44.09c-1.24,0-2.62-.63-2.62-3.71s1.37-3.62,2.62-3.62h15.39v7.34h-15.39Z" />
            <path d="M274.02,15.84v7.56h11.53v28.38h8.17v-28.38h11.53v-7.56h-31.22Z" />
            <path d="M328.54,15.84h-20.55v7.62h20.01c2.94,0,4.08,1.34,4.08,4.78,0,.02,0,.98,0,1.27h-16.59c-6.31,0-9.44,3.15-9.44,10.28v1.7c0,7.33,3.25,10.28,9.79,10.28h24.32v-23.62c0-9.05-2.99-12.31-11.62-12.31ZM316.69,44.09c-1.24,0-2.62-.63-2.62-3.71s1.37-3.62,2.62-3.62h15.39v7.34h-15.39Z" />
          </g>
        </svg>
      </div>
      <div className="navbar-right">
        <div className="status-pill">
          <span className="status-dot" />
          AI Agents Online
        </div>
      </div>
    </header>
  );
}
