import React, { useState, useEffect } from 'react';
import { X, Sparkles, FileText, BarChart2, Shield } from 'lucide-react';
import { WorkflowStartRequest } from '../services/api';

interface Props {
  isOpen: boolean;
  type: WorkflowStartRequest['workflow_type'] | null;
  onClose: () => void;
  onSubmit: (request: WorkflowStartRequest) => void;
  isLoading: boolean;
}

const meta: Record<string, { title: string; subtitle: string; Icon: React.FC<any> }> = {
  project_intake_to_charter: {
    title: 'New Project Intake',
    subtitle: 'Provide project details to auto-generate a PMO Charter',
    Icon: FileText,
  },
  weekly_status_report: {
    title: 'Weekly Status Report',
    subtitle: 'Input current week data to generate an executive report',
    Icon: BarChart2,
  },
  raid_update: {
    title: 'RAID Registry Update',
    subtitle: 'Paste meeting notes — AI extracts risks, actions & decisions',
    Icon: Shield,
  },
};

export default function WorkflowStartModal({ isOpen, type, onClose, onSubmit, isLoading }: Props) {
  const [formData, setFormData] = useState<Record<string, any>>({});

  useEffect(() => {
    if (isOpen) setFormData({});
  }, [isOpen, type]);

  // Prevent body scroll when modal open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  if (!isOpen || !type) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      workflow_type: type,
      input_payload: formData,
      user_context: { user_id: 'u1', role: 'pm' },
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const { title, subtitle, Icon } = meta[type] || { title: 'Start Workflow', subtitle: '', Icon: Sparkles };

  const renderFields = () => {
    switch (type) {
      case 'project_intake_to_charter':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Project Name</label>
              <input
                required
                name="project_name"
                onChange={handleChange}
                className="form-input"
                placeholder="e.g. Phoenix Cloud Migration"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Business Case & Scope</label>
              <textarea
                required
                name="project_description"
                onChange={handleChange}
                rows={4}
                className="form-textarea"
                placeholder="Describe the core objectives, deliverables, and strategic rationale..."
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Executive Sponsor</label>
                <input
                  required
                  name="sponsor"
                  onChange={handleChange}
                  className="form-input"
                  placeholder="e.g. Jane Doe"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Budget (USD)</label>
                <input
                  type="number"
                  required
                  name="budget"
                  onChange={handleChange}
                  className="form-input"
                  placeholder="e.g. 500000"
                />
              </div>
            </div>
          </>
        );

      case 'weekly_status_report':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Project Name</label>
              <input
                required
                name="project_name"
                onChange={handleChange}
                className="form-input"
                placeholder="e.g. Phoenix Cloud Migration"
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Reporting Period</label>
                <input
                  required
                  name="reporting_period"
                  placeholder="e.g. Q3 Week 5"
                  onChange={handleChange}
                  className="form-input"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Overall Health</label>
                <select required name="health" onChange={handleChange} className="form-select">
                  <option value="">Select Status</option>
                  <option value="Green">🟢 Green — On Track</option>
                  <option value="Yellow">🟡 Yellow — At Risk</option>
                  <option value="Red">🔴 Red — Off Track</option>
                </select>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Key Updates & Accomplishments</label>
              <textarea
                required
                name="key_updates"
                onChange={handleChange}
                rows={4}
                className="form-textarea"
                placeholder="Bullet-point summary of this week's progress, milestones, and blockers..."
              />
            </div>
          </>
        );

      case 'raid_update':
        return (
          <>
            <div className="form-group">
              <label className="form-label">Project Name</label>
              <input
                required
                name="project_name"
                onChange={handleChange}
                className="form-input"
                placeholder="e.g. Phoenix Cloud Migration"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Meeting Notes / Raw Input</label>
              <textarea
                required
                name="meeting_notes"
                placeholder="Paste unformatted meeting notes — the AI will extract all RAID items automatically..."
                onChange={handleChange}
                rows={6}
                className="form-textarea"
              />
            </div>
          </>
        );

      default:
        return (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Form not configured for this workflow type.
          </p>
        );
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-title">

        {/* Top gradient line */}
        <div className="modal-top-bar" />

        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-left">
            <div className="modal-icon">
              <Icon size={22} strokeWidth={1.8} />
            </div>
            <div>
              <h2 id="modal-title" className="modal-title">{title}</h2>
              <p className="modal-subtitle">{subtitle}</p>
            </div>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close modal">
            <X size={16} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {renderFields()}
          </div>

          {/* Footer */}
          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading} style={{ width: 'auto', minWidth: '160px' }}>
              {isLoading ? (
                <>
                  <svg
                    className="animate-spin"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    style={{ width: 16, height: 16 }}
                  >
                    <circle className="opacity-50" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
                    <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Processing…
                </>
              ) : (
                <>
                  <Sparkles size={15} />
                  Launch Workflow
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
