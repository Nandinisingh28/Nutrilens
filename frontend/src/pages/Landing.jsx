import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Target, CheckCircle, ArrowRight, Zap, Shield, Sparkles } from 'lucide-react';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Hero from '../components/Hero';
import { CATEGORIES, CLAIM_ICONS, getClaimIcon } from '../utils/icons';

function Landing() {
    const navigate = useNavigate();
    const location = useLocation();
    const { isAuthenticated } = useAuth();
    const { theme, toggleTheme } = useTheme();

    // Redirect to dashboard if already logged in
    useEffect(() => {
        if (isAuthenticated) {
            navigate('/dashboard');
        }
    }, [isAuthenticated, navigate]);

    // Handle jump to hash on mount
    useEffect(() => {
        if (location.hash) {
            const id = location.hash.replace('#', '');
            const element = document.getElementById(id);
            if (element) {
                setTimeout(() => {
                    element.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            }
        }
    }, [location.hash]);

    return (
        <div className="animate-fadeIn">
            {/* Hero Section */}
            <Hero />

            {/* How It Works */}
            <section id="features" className="container" style={{ padding: 'var(--spacing-20) 0' }}>
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
                        20+ claim types verified against strict FSSAI guidelines
                    </p>

                    <div style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        justifyContent: 'center',
                        gap: 'var(--spacing-3)',
                        maxWidth: '900px',
                        margin: '0 auto'
                    }}>
                        {Object.keys(CLAIM_ICONS).map((label) => {
                            const CIcon = getClaimIcon(label);
                            return (
                                <span
                                    key={label}
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
                                    <CIcon size={16} />
                                    {label}
                                </span>
                            );
                        })}
                    </div>
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
                    {CATEGORIES.map(({ key, Icon, labelFull }) => (
                        <div
                            key={labelFull}
                            style={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: 'var(--spacing-2)',
                                padding: 'var(--spacing-5) var(--spacing-3)',
                                background: 'rgba(34, 197, 94, 0.06)',
                                border: '1px solid rgba(34, 197, 94, 0.2)',
                                borderRadius: 'var(--radius-xl)',
                                transition: 'all var(--transition-base)',
                                cursor: 'default'
                            }}
                        >
                            <Icon size={32} />
                            <span style={{
                                fontSize: 'var(--font-size-sm)',
                                fontWeight: '600',
                                color: 'var(--color-neutral-200)',
                                textAlign: 'center'
                            }}>
                                {labelFull}
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
            {/* Footer is already rendered via PublicLayout in App.jsx */}
        </div>
    );
}

export default Landing;
