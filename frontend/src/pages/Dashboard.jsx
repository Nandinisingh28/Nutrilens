import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Target, Zap, Shield, History, ChevronRight, Sparkles } from 'lucide-react';

function Dashboard() {
    const { user } = useAuth();
    const navigate = useNavigate();

    return (
        <div className="animate-fadeIn">
            {/* Hero Section */}
            <div className="hero" style={{ margin: '-2rem -1.5rem 2rem', borderRadius: 'var(--radius-xl)' }}>
                <div className="hero-content">
                    <h1 className="hero-title">
                        Hey, {user?.name?.split(' ')[0] || 'there'}! 👋
                    </h1>
                    <p className="hero-subtitle">
                        Ready to verify food claims? Upload a product label and we'll analyze
                        whether those "High Protein" or "Low Sugar" claims are actually true.
                    </p>
                    <div className="hero-actions">
                        <button
                            className="btn btn-primary btn-lg"
                            onClick={() => navigate('/scan/precision')}
                        >
                            <Target size={20} />
                            Precision Scan
                        </button>
                        <button
                            className="btn btn-secondary btn-lg"
                            onClick={() => navigate('/scan/quick')}
                        >
                            <Zap size={20} />
                            Quick Scan
                        </button>
                    </div>
                </div>
            </div>

            {/* Scan Mode Selection */}
            <h2 style={{ textAlign: 'center', marginBottom: 'var(--spacing-6)' }}>
                Choose Your Scan Mode
            </h2>

            <div className="scan-mode-grid">
                <div
                    className="scan-mode-card"
                    onClick={() => navigate('/scan/precision')}
                >
                    <div className="scan-mode-icon">
                        <Target size={64} />
                    </div>
                    <h3 className="scan-mode-title">Precision Scan</h3>
                    <p className="scan-mode-description">
                        Upload separate photos of the nutrition facts and ingredients list for the most accurate analysis.
                    </p>
                    <button className="btn btn-primary" style={{ marginTop: 'var(--spacing-4)' }}>
                        Start Precision Scan
                        <ChevronRight size={16} />
                    </button>
                </div>

                <div
                    className="scan-mode-card"
                    onClick={() => navigate('/scan/quick')}
                >
                    <div className="scan-mode-icon">
                        <Zap size={64} />
                    </div>
                    <h3 className="scan-mode-title">Quick Scan</h3>
                    <p className="scan-mode-description">
                        Upload a single image containing both sections. Faster but may be less accurate for complex labels.
                    </p>
                    <button className="btn btn-secondary" style={{ marginTop: 'var(--spacing-4)' }}>
                        Start Quick Scan
                        <ChevronRight size={16} />
                    </button>
                </div>
            </div>

            {/* Features */}
            <h2 style={{ textAlign: 'center', margin: 'var(--spacing-12) 0 var(--spacing-6)' }}>
                How NutriLens Works
            </h2>

            <div className="features-grid">
                <div className="feature-card">
                    <div className="feature-icon">
                        <Sparkles size={48} />
                    </div>
                    <h3 className="feature-title">AI-Powered OCR</h3>
                    <p className="feature-description">
                        Our advanced OCR extracts nutrition facts and ingredients from your photos with high accuracy.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">
                        <Shield size={48} />
                    </div>
                    <h3 className="feature-title">FSSAI Standards</h3>
                    <p className="feature-description">
                        We verify claims against official Indian food safety guidelines for accurate results.
                    </p>
                </div>

                <div className="feature-card">
                    <div className="feature-icon">
                        <History size={48} />
                    </div>
                    <h3 className="feature-title">Scan History</h3>
                    <p className="feature-description">
                        All your scans are saved so you can review past products anytime you want.
                    </p>
                </div>
            </div>

            {/* Supported Claims */}
            <div className="card" style={{ marginTop: 'var(--spacing-8)' }}>
                <h3 style={{ marginBottom: 'var(--spacing-4)' }}>Supported Claim Types</h3>
                <div style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 'var(--spacing-2)'
                }}>
                    {[
                        { label: 'High Protein', icon: '💪' },
                        { label: 'Low Sugar', icon: '🍬' },
                        { label: 'No Sugar / Sugar Free', icon: '🚫' },
                        { label: 'High Fiber', icon: '🌾' },
                        { label: 'Low Fat', icon: '🥑' },
                        { label: 'No Trans Fat', icon: '❌' },
                        { label: 'Low Calorie', icon: '🔥' },
                        { label: 'Low Sodium', icon: '🧂' },
                        { label: 'High Calcium', icon: '🦴' },
                        { label: 'No Preservatives', icon: '🧪' },
                        { label: 'No Artificial Colors', icon: '🎨' },
                        { label: 'No Artificial Flavors', icon: '👅' },
                        { label: 'Natural', icon: '🌿' },
                        { label: 'Organic', icon: '🌱' },
                        { label: 'Whole Grain', icon: '🌾' },
                    ].map((claim) => (
                        <span
                            key={claim.label}
                            style={{
                                padding: 'var(--spacing-2) var(--spacing-3)',
                                background: 'rgba(34, 197, 94, 0.06)',
                                border: '1px solid rgba(34, 197, 94, 0.2)',
                                borderRadius: 'var(--radius-full)',
                                fontSize: 'var(--font-size-sm)',
                                color: 'var(--color-neutral-300)',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: 'var(--spacing-2)'
                            }}
                        >
                            <span>{claim.icon}</span>
                            {claim.label}
                        </span>
                    ))}
                </div>
                <p style={{
                    color: 'var(--color-neutral-500)',
                    fontSize: 'var(--font-size-xs)',
                    marginTop: 'var(--spacing-3)',
                    marginBottom: 0
                }}>
                    Compound claims like "High Protein and Low Sugar" are also supported
                </p>
            </div>

            {/* Supported Categories */}
            <div className="card" style={{ marginTop: 'var(--spacing-4)' }}>
                <h3 style={{ marginBottom: 'var(--spacing-4)' }}>Supported Product Categories</h3>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                    gap: 'var(--spacing-3)'
                }}>
                    {[
                        { label: 'Protein Bars', icon: '🥜', bg: 'rgba(234, 179, 8, 0.1)', border: 'rgba(234, 179, 8, 0.25)' },
                        { label: 'Cereals', icon: '🥣', bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.25)' },
                        { label: 'Biscuits', icon: '🍪', bg: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.25)' },
                        { label: 'Snacks', icon: '🍿', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.25)' },
                        { label: 'Chocolates', icon: '🍫', bg: 'rgba(168, 85, 247, 0.1)', border: 'rgba(168, 85, 247, 0.25)' },
                        { label: 'Beverages', icon: '🥤', bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.25)' },
                        { label: 'Energy Drinks', icon: '⚡', bg: 'rgba(234, 179, 8, 0.1)', border: 'rgba(234, 179, 8, 0.25)' },
                        { label: 'Dairy', icon: '🥛', bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.25)' },
                        { label: 'Noodles/RTE', icon: '🍜', bg: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.25)' },
                        { label: 'Sauces', icon: '🫙', bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.25)' },
                        { label: 'Supplements', icon: '💊', bg: 'rgba(168, 85, 247, 0.1)', border: 'rgba(168, 85, 247, 0.25)' },
                        { label: 'Frozen Foods', icon: '🧊', bg: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.25)' },
                    ].map((cat) => (
                        <div
                            key={cat.label}
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: 'var(--spacing-1)',
                                padding: 'var(--spacing-3)',
                                background: cat.bg,
                                border: `1px solid ${cat.border}`,
                                borderRadius: 'var(--radius-lg)',
                                textAlign: 'center'
                            }}
                        >
                            <span style={{ fontSize: '1.5rem' }}>{cat.icon}</span>
                            <span style={{
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: '600',
                                color: 'var(--color-neutral-200)'
                            }}>
                                {cat.label}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
