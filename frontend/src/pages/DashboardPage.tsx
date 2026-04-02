import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { workflowApi, WorkflowStartRequest } from '../services/api';
import WorkflowStartModal from '../components/WorkflowStartModal';
import { FileText, BarChart2, Shield, ArrowRight } from 'lucide-react';

const workflows = [
  {
    id: 'project_intake_to_charter' as const,
    tag: 'Intake',
    Icon: FileText,
    title: 'Project Intake to Charter',
    description:
      'Initiate new projects with AI-driven charter generation. Our agent synthesises business cases, budgets, and governance requirements into a structured PMO charter.',
    features: ['Auto-generates Project Charter', 'Budget & Risk Assessment', 'Sponsor Approval Flow'],
  },
  {
    id: 'weekly_status_report' as const,
    tag: 'Reporting',
    Icon: BarChart2,
    title: 'Weekly Status Report',
    description:
      'Generate executive-ready status reports instantly. The agent synthesises narrative updates, RAG health metrics, and stakeholder-ready summaries automatically.',
    features: ['Narrative Summary Generation', 'RAG Health Indicators', 'Stakeholder Distribution'],
  },
  {
    id: 'raid_update' as const,
    tag: 'RAID',
    Icon: Shield,
    title: 'RAID Registry Update',
    description:
      'Extract Risks, Actions, Issues, and Decisions from raw meeting notes. Intelligent parsing converts unstructured text into a structured, traceable RAID log.',
    features: ['NLP Meeting Note Parsing', 'Risk Prioritisation Matrix', 'Action Owner Assignment'],
  },
];

export default function DashboardPage() {
  const navigate = useNavigate();
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowStartRequest['workflow_type'] | null>(null);

  const startMutation = useMutation({
    mutationFn: (request: WorkflowStartRequest) => workflowApi.start(request),
    onSuccess: (response) => {
      setSelectedWorkflow(null);
      navigate(`/workflows/${response.data.workflow_id}`);
    },
    onError: (error) => {
      console.error('Failed to start workflow:', error);
      alert('Failed to start workflow. Check console for details.');
    },
  });

  return (
    <>
      <div className="app-bg" />

      <div className="page-wrapper">
        {/* ── NAVBAR ── */}
        <header className="navbar">
          <div className="navbar-brand">
            <svg 
              width="140" 
              height="28" 
              viewBox="0 0 340.16 69.52" 
              fill="var(--ntt-blue)" 
              xmlns="http://www.w3.org/2000/svg"
              className="navbar-logo-svg"
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

        {/* ── MAIN ── */}
        <main className="main-content">
          {/* Hero */}
          <div className="hero-header">
            <h1 className="hero-title">
              PMO Agentic<br />
              <span>AI Platform</span>
            </h1>
            <div className="hero-divider" />
            <p className="hero-subtitle">
              AI-driven workflows that automate the full project lifecycle —
              from intake to charter, reporting, and RAID governance.
            </p>
          </div>

          {/* Cards */}
          <div className="workflow-grid">
            {workflows.map((wf) => (
              <div key={wf.id} className="workflow-card">
                <div className="card-stripe" />

                <div className="card-icon-wrap">
                  <wf.Icon size={24} strokeWidth={1.8} />
                </div>

                <p className="card-tag">{wf.tag}</p>
                <h2 className="card-title">{wf.title}</h2>
                <p className="card-description">{wf.description}</p>

                <ul className="card-features">
                  {wf.features.map((f) => (
                    <li key={f} className="card-feature-item">
                      <span className="feature-check">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>

                <button
                  className="btn btn-primary"
                  onClick={() => setSelectedWorkflow(wf.id)}
                >
                  Launch Workflow
                  <ArrowRight size={15} />
                </button>
              </div>
            ))}
          </div>
        </main>
      </div>

      <WorkflowStartModal
        isOpen={selectedWorkflow !== null}
        type={selectedWorkflow}
        onClose={() => setSelectedWorkflow(null)}
        onSubmit={(req) => startMutation.mutate(req)}
        isLoading={startMutation.isPending}
      />
    </>
  );
}
