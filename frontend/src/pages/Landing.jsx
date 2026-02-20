import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Leaf, Shield, Zap, Target, CheckCircle, ArrowRight, Sparkles, Sun, Moon } from 'lucide-react';
import { useEffect } from 'react';

function Landing() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const { theme, toggleTheme } = useTheme();

    // Redirect to dashboard if already logged in
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    return (
        <div className="animate-fadeIn">
            {/* Navigation */}
            <nav className="navbar" style={{ background: 'transparent', borderBottom: 'none' }}>
                <div className="container navbar-content">
                    <div className="navbar-logo">
                        <div className="navbar-logo-icon">
                            <Leaf size={20} />
                        </div>
                        NutriLens
                    </div>
                    <div className="navbar-nav">
                        {/* Theme Toggle */}
                        <button
                            onClick={toggleTheme}
                            className="btn btn-ghost"
                            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                            style={{ padding: 'var(--spacing-2)' }}
                        >
                            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        </button>
                        <button
                            className="btn btn-ghost"
                            onClick={() => navigate('/login')}
                        >
                            Sign In
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={() => navigate('/signup')}
                        >
                            Get Started
                        </button>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <section className="hero" style={{ marginTop: '-80px', paddingTop: 'calc(var(--spacing-20) + 80px)' }}>
                <div className="container">
                    <div className="hero-content">
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 'var(--spacing-2)',
                            padding: 'var(--spacing-2) var(--spacing-4)',
                            background: 'rgba(34, 197, 94, 0.1)',
                            border: '1px solid rgba(34, 197, 94, 0.3)',
                            borderRadius: 'var(--radius-full)',
                            marginBottom: 'var(--spacing-6)',
                            fontSize: 'var(--font-size-sm)',
                            color: 'var(--color-primary-400)'
                        }}>
                            <Sparkles size={16} />
                            Powered by AI & FSSAI Guidelines
                        </div>

                        <h1 className="hero-title">
                            Verify Food Claims <br />
                            <span style={{ color: 'var(--color-primary-400)' }}>Before You Buy</span>
                        </h1>

                        <p className="hero-subtitle">
                            Don't fall for misleading marketing! NutriLens uses AI-powered OCR to verify
                            claims like "High Protein", "Low Sugar", and "Healthy" against actual nutrition facts.
                        </p>

                        <div className="hero-actions">
                            <button
                                className="btn btn-primary btn-lg"
                                onClick={() => navigate('/signup')}
                            >
                                Start Free
                                <ArrowRight size={20} />
                            </button>
                            <button
                                className="btn btn-secondary btn-lg"
                                onClick={() => navigate('/login')}
                            >
                                Sign In
                            </button>
                        </div>

                        {/* Trust badges */}
                        <div style={{
                            display: 'flex',
                            justifyContent: 'center',
                            gap: 'var(--spacing-8)',
                            marginTop: 'var(--spacing-12)',
                            color: 'var(--color-neutral-400)',
                            fontSize: 'var(--font-size-sm)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
                                <CheckCircle size={16} color="var(--color-primary-400)" />
                                Free to Use
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
                                <CheckCircle size={16} color="var(--color-primary-400)" />
                                FSSAI Standards
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-2)' }}>
                                <CheckCircle size={16} color="var(--color-primary-400)" />
                                Instant Results
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* How It Works */}
            <section className="container" style={{ padding: 'var(--spacing-20) 0' }}>
                <h2 style={{ textAlign: 'center', marginBottom: 'var(--spacing-4)' }}>
                    How It Works
                </h2>
                <p style={{
                    textAlign: 'center',
                    color: 'var(--color-neutral-400)',
                    maxWidth: '600px',
                    margin: '0 auto var(--spacing-12)'
                }}>
                    Verify food claims in 3 simple steps
                </p>

                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon" style={{
                            width: '64px',
                            height: '64px',
                            background: 'rgba(34, 197, 94, 0.1)',
                            borderRadius: 'var(--radius-xl)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto var(--spacing-4)'
                        }}>
                            <Target size={32} />
                        </div>
                        <h3 className="feature-title">1. Upload Photo</h3>
                        <p className="feature-description">
                            Take a photo of the nutrition label and ingredients list on the food package.
                        </p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon" style={{
                            width: '64px',
                            height: '64px',
                            background: 'rgba(168, 85, 247, 0.1)',
                            borderRadius: 'var(--radius-xl)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto var(--spacing-4)'
                        }}>
                            <Zap size={32} color="var(--color-secondary-400)" />
                        </div>
                        <h3 className="feature-title">2. Enter Claim</h3>
                        <p className="feature-description">
                            Type the marketing claim you want to verify, like "High Protein" or "Low Sugar".
                        </p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon" style={{
                            width: '64px',
                            height: '64px',
                            background: 'rgba(34, 197, 94, 0.1)',
                            borderRadius: 'var(--radius-xl)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto var(--spacing-4)'
                        }}>
                            <Shield size={32} />
                        </div>
                        <h3 className="feature-title">3. Get Verdict</h3>
                        <p className="feature-description">
                            Receive an instant verdict: TRUE, FALSE, MISLEADING, or PARTIALLY TRUE with explanations.
                        </p>
                    </div>
                </div>
            </section>

            {/* Supported Claims */}
            <section style={{ background: 'var(--color-neutral-900)', padding: 'var(--spacing-16) 0' }}>
                <div className="container">
                    <h2 style={{ textAlign: 'center', marginBottom: 'var(--spacing-4)' }}>
                        Claims We Verify
                    </h2>
                    <p style={{
                        textAlign: 'center',
                        color: 'var(--color-neutral-400)',
                        marginBottom: 'var(--spacing-8)'
                    }}>
                        15 claim types verified against FSSAI &amp; WHO guidelines
                    </p>

                    <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        justifyContent: 'center',
                        gap: 'var(--spacing-3)',
                        maxWidth: '900px',
                        margin: '0 auto'
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
                                    padding: 'var(--spacing-2) var(--spacing-4)',
                                    background: 'rgba(34, 197, 94, 0.06)',
                                    border: '1px solid rgba(34, 197, 94, 0.2)',
                                    borderRadius: 'var(--radius-full)',
                                    fontSize: 'var(--font-size-sm)',
                                    color: 'var(--color-neutral-200)',
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: 'var(--spacing-2)',
                                    transition: 'all var(--transition-fast)',
                                    cursor: 'default'
                                }}
                            >
                                <span>{claim.icon}</span>
                                {claim.label}
                            </span>
                        ))}
                    </div>

                    <p style={{
                        textAlign: 'center',
                        color: 'var(--color-neutral-500)',
                        fontSize: 'var(--font-size-xs)',
                        marginTop: 'var(--spacing-6)'
                    }}>
                        Compound claims like "High Protein and Low Sugar" are also supported
                    </p>
                </div>
            </section>

            {/* Supported Categories */}
            <section className="container" style={{ padding: 'var(--spacing-16) 0' }}>
                <h2 style={{ textAlign: 'center', marginBottom: 'var(--spacing-4)' }}>
                    Supported Product Categories
                </h2>
                <p style={{
                    textAlign: 'center',
                    color: 'var(--color-neutral-400)',
                    marginBottom: 'var(--spacing-10)'
                }}>
                    Analyze any packaged food across 12 product categories
                </p>

                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                    gap: 'var(--spacing-4)',
                    maxWidth: '900px',
                    margin: '0 auto'
                }}>
                    {[
                        { label: 'Protein Bars', icon: '🥜', color: 'rgba(234, 179, 8, 0.1)', border: 'rgba(234, 179, 8, 0.25)' },
                        { label: 'Breakfast Cereals', icon: '🥣', color: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.25)' },
                        { label: 'Biscuits & Cookies', icon: '🍪', color: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.25)' },
                        { label: 'Snacks', icon: '🍿', color: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.25)' },
                        { label: 'Chocolates', icon: '🍫', color: 'rgba(168, 85, 247, 0.1)', border: 'rgba(168, 85, 247, 0.25)' },
                        { label: 'Beverages', icon: '🥤', color: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.25)' },
                        { label: 'Energy Drinks', icon: '⚡', color: 'rgba(234, 179, 8, 0.1)', border: 'rgba(234, 179, 8, 0.25)' },
                        { label: 'Dairy Products', icon: '🥛', color: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.25)' },
                        { label: 'Noodles & RTE', icon: '🍜', color: 'rgba(249, 115, 22, 0.1)', border: 'rgba(249, 115, 22, 0.25)' },
                        { label: 'Sauces & Spreads', icon: '🫙', color: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.25)' },
                        { label: 'Health Supplements', icon: '💊', color: 'rgba(168, 85, 247, 0.1)', border: 'rgba(168, 85, 247, 0.25)' },
                        { label: 'Frozen Foods', icon: '🧊', color: 'rgba(34, 197, 94, 0.1)', border: 'rgba(34, 197, 94, 0.25)' },
                    ].map((cat) => (
                        <div
                            key={cat.label}
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: 'var(--spacing-2)',
                                padding: 'var(--spacing-5) var(--spacing-3)',
                                background: cat.color,
                                border: `1px solid ${cat.border}`,
                                borderRadius: 'var(--radius-xl)',
                                transition: 'all var(--transition-base)',
                                cursor: 'default'
                            }}
                        >
                            <span style={{ fontSize: '2rem' }}>{cat.icon}</span>
                            <span style={{
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: '600',
                                color: 'var(--color-neutral-200)',
                                textAlign: 'center'
                            }}>
                                {cat.label}
                            </span>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="container" style={{ padding: 'var(--spacing-20) 0', textAlign: 'center' }}>
                <h2 style={{ marginBottom: 'var(--spacing-4)' }}>
                    Ready to Verify Your Food?
                </h2>
                <p style={{
                    color: 'var(--color-neutral-400)',
                    marginBottom: 'var(--spacing-8)',
                    maxWidth: '500px',
                    margin: '0 auto var(--spacing-8)'
                }}>
                    Join thousands of health-conscious consumers who verify before they buy.
                </p>
                <button
                    className="btn btn-primary btn-lg"
                    onClick={() => navigate('/signup')}
                >
                    Create Free Account
                    <ArrowRight size={20} />
                </button>
            </section>

            {/* Footer */}
            <footer style={{
                borderTop: '1px solid var(--color-neutral-800)',
                padding: 'var(--spacing-8) 0',
                textAlign: 'center'
            }}>
                <div className="container">
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: 'var(--spacing-2)',
                        marginBottom: 'var(--spacing-4)'
                    }}>
                        <div className="navbar-logo-icon" style={{ width: '28px', height: '28px' }}>
                            <Leaf size={14} />
                        </div>
                        <span style={{ fontWeight: '600' }}>NutriLens</span>
                    </div>
                    <p style={{
                        color: 'var(--color-neutral-500)',
                        fontSize: 'var(--font-size-sm)',
                        marginBottom: 'var(--spacing-2)'
                    }}>
                        Helping you make informed food choices
                    </p>
                    <p style={{
                        color: 'var(--color-neutral-600)',
                        fontSize: 'var(--font-size-xs)'
                    }}>
                        © 2024 NutriLens. Based on FSSAI Guidelines for Indian Food Products.
                    </p>
                </div>
            </footer>
        </div>
    );
}

export default Landing;
