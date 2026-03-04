import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Target, CheckCircle, ArrowRight, Zap, Shield, Sparkles } from 'lucide-react';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Hero from '../components/Hero';

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
                        25+ claim types verified against strict FSSAI guidelines
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
                            { label: 'Source of Protein', icon: '🥩' },
                            { label: 'Low Sugar', icon: '🍬' },
                            { label: 'Sugar Free', icon: '🚫' },
                            { label: 'No Added Sugar', icon: '⛔' },
                            { label: 'High Fiber', icon: '🌾' },
                            { label: 'Source of Fiber', icon: '🥦' },
                            { label: 'Low Fat', icon: '🥑' },
                            { label: 'Fat Free', icon: '🫙' },
                            { label: 'Low Saturated Fat', icon: '🧈' },
                            { label: 'Trans Fat Free', icon: '❌' },
                            { label: 'Low Energy', icon: '🔋' },
                            { label: 'Cholesterol Free', icon: '🫀' },
                            { label: 'Low Cholesterol', icon: '💊' },
                            { label: 'Gluten Free', icon: '🌾' },
                            { label: 'Vegan', icon: '🌱' },
                            { label: 'No Preservatives', icon: '🧪' },
                            { label: 'No Artificial Colors', icon: '🎨' },
                            { label: 'No Artificial Flavors', icon: '👅' },
                            { label: 'No Palm Oil', icon: '🌴' },
                            { label: 'Lactose Free', icon: '🥛' },
                            { label: 'Eggless', icon: '🥚' },
                            { label: 'Whole Grain', icon: '🌾' },
                            { label: 'No Added MSG', icon: '🫗' },
                            { label: 'Clean Ingredients', icon: '✨' },
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
                        Compound claims like "High Protein and No Added Sugar" are also supported
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
            {/* Footer is already rendered via PublicLayout in App.jsx */}
        </div>
    );
}

export default Landing;
