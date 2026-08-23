import { X, Layers, Cpu, Award, Database, FileText, CheckCircle2 } from 'lucide-react'

export default function ResearchArchitectureModal({ isOpen, onClose }) {
  if (!isOpen) return null

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20 }}>
      <div className="fade-in card" style={{ width: '100%', maxWidth: 840, maxHeight: '90vh', overflowY: 'auto', padding: 32, borderRadius: 16, border: '1px solid var(--border)', background: 'var(--bg-elevated)', position: 'relative' }}>
        <button onClick={onClose} style={{ position: 'absolute', top: 20, right: 20, background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <X size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: 'var(--color-primary-muted)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Layers size={24} />
          </div>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 800, color: 'var(--text)', margin: 0 }}>
              System Architecture & ML Research Specifications
            </h2>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
              SLIIT Final-Year Research Project · AI-Driven Recruitment Ecosystem
            </div>
          </div>
        </div>

        {/* Pipeline Architecture Diagram */}
        <div style={{ padding: 20, background: 'var(--bg)', borderRadius: 12, border: '1px solid var(--border)', marginBottom: 24 }}>
          <h4 style={{ fontSize: 13, fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent)', letterSpacing: 1, marginBottom: 14 }}>
            System Dataflow Architecture
          </h4>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, textAlign: 'center' }}>
            <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, fontWeight: 700 }}>
              <FileText size={16} style={{ color: 'var(--accent)', margin: '0 auto 4px' }} /> Resume Document
            </div>
            <span style={{ color: 'var(--text-muted)' }}>→</span>
            <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, fontWeight: 700 }}>
              <Cpu size={16} style={{ color: 'var(--color-primary)', margin: '0 auto 4px' }} /> Component 1 (CV Screening)
            </div>
            <span style={{ color: 'var(--text-muted)' }}>→</span>
            <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, fontWeight: 700 }}>
              <Cpu size={16} style={{ color: 'var(--color-info)', margin: '0 auto 4px' }} /> Component 2 (AI Interview)
            </div>
            <span style={{ color: 'var(--text-muted)' }}>→</span>
            <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, fontWeight: 700 }}>
              <Cpu size={16} style={{ color: 'var(--color-warning)', margin: '0 auto 4px' }} /> Component 3 (Candidate Ranking)
            </div>
            <span style={{ color: 'var(--text-muted)' }}>→</span>
            <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12, fontWeight: 700 }}>
              <Cpu size={16} style={{ color: 'var(--color-success)', margin: '0 auto 4px' }} /> Component 4 (Skill Gap & Career)
            </div>
          </div>
        </div>

        {/* Model Metrics Table */}
        <div style={{ marginBottom: 24 }}>
          <h4 style={{ fontSize: 14, fontWeight: 700, color: 'var(--text)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Award size={16} style={{ color: 'var(--accent)' }} /> Machine Learning Component Benchmarks
          </h4>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, background: 'var(--bg)', borderRadius: 10, overflow: 'hidden', border: '1px solid var(--border)' }}>
            <thead>
              <tr style={{ background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
                <th style={{ padding: '10px 14px' }}>Component</th>
                <th style={{ padding: '10px 14px' }}>Primary Algorithm</th>
                <th style={{ padding: '10px 14px' }}>Dataset Size</th>
                <th style={{ padding: '10px 14px' }}>Benchmark Performance</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '10px 14px', fontWeight: 700 }}>Component 1</td>
                <td style={{ padding: '10px 14px' }}>LogisticRegression + TF-IDF Vectorizer</td>
                <td style={{ padding: '10px 14px' }}>4,000 Resumes</td>
                <td style={{ padding: '10px 14px', color: 'var(--color-success)', fontWeight: 700 }}>98.57% Accuracy (F1: 0.985)</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '10px 14px', fontWeight: 700 }}>Component 2</td>
                <td style={{ padding: '10px 14px' }}>NLP Keyword & Sentiment Matrix</td>
                <td style={{ padding: '10px 14px' }}>20 IT Domains</td>
                <td style={{ padding: '10px 14px', color: 'var(--color-success)', fontWeight: 700 }}>100% MCQ & Descriptive Pipeline</td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '10px 14px', fontWeight: 700 }}>Component 3</td>
                <td style={{ padding: '10px 14px' }}>Multi-Criteria Learning-to-Rank (LTR)</td>
                <td style={{ padding: '10px 14px' }}>Applicant Pipeline</td>
                <td style={{ padding: '10px 14px', color: 'var(--color-success)', fontWeight: 700 }}>NDCG@5 Ranking Precision</td>
              </tr>
              <tr>
                <td style={{ padding: '10px 14px', fontWeight: 700 }}>Component 4</td>
                <td style={{ padding: '10px 14px' }}>Weighted Jaccard + Priority Score Formula</td>
                <td style={{ padding: '10px 14px' }}>10,000 Records</td>
                <td style={{ padding: '10px 14px', color: 'var(--color-success)', fontWeight: 700 }}>AUC 0.9936 / Top-3 Acc: 80%</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Literature References */}
        <div style={{ padding: 16, background: 'var(--bg)', borderRadius: 10, border: '1px solid var(--border)' }}>
          <h4 style={{ fontSize: 13, fontWeight: 700, color: 'var(--text)', marginBottom: 8 }}>Academic Literature Citations</h4>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: 4 }}>
            <div>• <em>PLOS One (2021)</em>: Skill-driven job transition recommender using skill-set distance.</div>
            <div>• <em>EAAI (2024)</em>: <strong>JobEdKG</strong> knowledge-graph course recommendation framework.</div>
            <div>• <em>Research Paper (2026)</em>: <strong>"An AI-Powered Hybrid Framework for Career Readiness"</strong>.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
