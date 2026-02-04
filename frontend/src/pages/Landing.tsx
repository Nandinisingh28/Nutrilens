import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Scan, Shield, History, Sparkles, ArrowRight, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/app/authStore'

export default function Landing() {
    const { isAuthenticated } = useAuthStore()

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-teal-50">
            {/* Hero Section */}
            <header className="sticky top-0 z-50 glass border-b border-gray-200/50">
                <div className="container flex items-center justify-between h-16">
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-teal-500 flex items-center justify-center">
                            <Scan className="w-5 h-5 text-white" />
                        </div>
                        <span className="font-bold text-xl gradient-text">NutriLens</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        {isAuthenticated ? (
                            <Button asChild>
                                <Link to="/app">Go to App</Link>
                            </Button>
                        ) : (
                            <>
                                <Button variant="ghost" asChild>
                                    <Link to="/login">Login</Link>
                                </Button>
                                <Button asChild>
                                    <Link to="/signup">Get Started</Link>
                                </Button>
                            </>
                        )}
                    </div>
                </div>
            </header>

            {/* Hero */}
            <section className="container py-20 md:py-32">
                <div className="max-w-4xl mx-auto text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.6 }}
                    >
                        <div className="inline-flex items-center space-x-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-6">
                            <Sparkles className="w-4 h-4" />
                            <span>AI-Powered Nutrition Analysis</span>
                        </div>
                        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
                            Know What You're Eating{' '}
                            <span className="gradient-text">Instantly</span>
                        </h1>
                        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                            Scan any nutrition label with your camera and get instant health insights.
                            Make informed food choices with AI-powered analysis.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Button size="lg" asChild className="w-full sm:w-auto">
                                <Link to="/signup">
                                    Start Scanning Free
                                    <ArrowRight className="w-5 h-5 ml-2" />
                                </Link>
                            </Button>
                            <Button size="lg" variant="outline" asChild className="w-full sm:w-auto">
                                <a href="#features">Learn More</a>
                            </Button>
                        </div>
                    </motion.div>

                    {/* Hero Image Placeholder - SVG Illustration */}
                    <motion.div
                        className="mt-16 relative"
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.2 }}
                    >
                        <div className="glass-card p-8 max-w-2xl mx-auto">
                            <ScanIllustration />
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Features */}
            <section id="features" className="container py-20">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        Everything You Need
                    </h2>
                    <p className="text-muted-foreground max-w-2xl mx-auto">
                        Advanced nutrition scanning with instant health insights
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard
                        icon={<Scan className="w-8 h-8 text-primary" />}
                        title="Instant OCR Scanning"
                        description="Point your camera at any nutrition label and get results in seconds using advanced OCR technology."
                        delay={0.1}
                    />
                    <FeatureCard
                        icon={<Shield className="w-8 h-8 text-primary" />}
                        title="Health Verdicts"
                        description="Get clear healthy, moderate, or unhealthy verdicts based on scientific nutrition guidelines."
                        delay={0.2}
                    />
                    <FeatureCard
                        icon={<History className="w-8 h-8 text-primary" />}
                        title="Scan History"
                        description="Keep track of all your scans and monitor your food choices over time."
                        delay={0.3}
                    />
                </div>
            </section>

            {/* Benefits */}
            <section className="container py-20">
                <div className="grid md:grid-cols-2 gap-12 items-center">
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                    >
                        <h2 className="text-3xl md:text-4xl font-bold mb-6">
                            Make Healthier Choices Every Day
                        </h2>
                        <ul className="space-y-4">
                            {[
                                'Understand complex nutrition labels instantly',
                                'Identify hidden sugars and unhealthy ingredients',
                                'Get personalized recommendations',
                                'Track your progress over time',
                                'Compare products easily',
                            ].map((benefit, index) => (
                                <li key={index} className="flex items-start space-x-3">
                                    <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                                        <Check className="w-4 h-4 text-primary" />
                                    </div>
                                    <span className="text-muted-foreground">{benefit}</span>
                                </li>
                            ))}
                        </ul>
                    </motion.div>
                    <motion.div
                        className="glass-card p-8"
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                    >
                        <ChartIllustration />
                    </motion.div>
                </div>
            </section>

            {/* CTA */}
            <section className="container py-20">
                <div className="bg-gradient-to-r from-primary to-teal-500 rounded-3xl p-12 text-center text-white">
                    <h2 className="text-3xl md:text-4xl font-bold mb-4">
                        Ready to Eat Smarter?
                    </h2>
                    <p className="text-white/80 mb-8 max-w-xl mx-auto">
                        Join thousands of health-conscious users making better food choices every day.
                    </p>
                    <Button size="lg" variant="secondary" asChild>
                        <Link to="/signup">
                            Get Started for Free
                            <ArrowRight className="w-5 h-5 ml-2" />
                        </Link>
                    </Button>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-gray-200 py-8">
                <div className="container text-center text-muted-foreground text-sm">
                    <p>© 2024 NutriLens. All rights reserved.</p>
                </div>
            </footer>
        </div>
    )
}

function FeatureCard({
    icon,
    title,
    description,
    delay,
}: {
    icon: React.ReactNode
    title: string
    description: string
    delay: number
}) {
    return (
        <motion.div
            className="glass-card p-6"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay }}
        >
            <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                {icon}
            </div>
            <h3 className="text-xl font-semibold mb-2">{title}</h3>
            <p className="text-muted-foreground">{description}</p>
        </motion.div>
    )
}

// SVG Illustrations
function ScanIllustration() {
    return (
        <svg viewBox="0 0 400 250" className="w-full h-auto" fill="none">
            <rect x="120" y="20" width="160" height="210" rx="12" fill="#f0fdf4" stroke="#22c55e" strokeWidth="2" />
            <text x="200" y="55" textAnchor="middle" className="text-xs font-semibold" fill="#166534">Nutrition Facts</text>
            <line x1="135" y1="65" x2="265" y2="65" stroke="#d1d5db" strokeWidth="1" />
            <text x="140" y="85" className="text-xs" fill="#6b7280">Calories</text>
            <text x="255" y="85" textAnchor="end" className="text-xs font-medium" fill="#374151">250</text>
            <text x="140" y="105" className="text-xs" fill="#6b7280">Total Fat</text>
            <text x="255" y="105" textAnchor="end" className="text-xs font-medium" fill="#374151">12g</text>
            <text x="140" y="125" className="text-xs" fill="#6b7280">Sodium</text>
            <text x="255" y="125" textAnchor="end" className="text-xs font-medium" fill="#374151">470mg</text>
            <text x="140" y="145" className="text-xs" fill="#6b7280">Total Carbs</text>
            <text x="255" y="145" textAnchor="end" className="text-xs font-medium" fill="#374151">31g</text>
            <text x="140" y="165" className="text-xs" fill="#6b7280">Sugars</text>
            <text x="255" y="165" textAnchor="end" className="text-xs font-medium" fill="#374151">5g</text>
            <text x="140" y="185" className="text-xs" fill="#6b7280">Protein</text>
            <text x="255" y="185" textAnchor="end" className="text-xs font-medium" fill="#374151">5g</text>
            {/* Scan lines */}
            <line x1="110" y1="100" x2="290" y2="100" stroke="#22c55e" strokeWidth="2" opacity="0.5">
                <animate attributeName="y1" values="40;200;40" dur="2s" repeatCount="indefinite" />
                <animate attributeName="y2" values="40;200;40" dur="2s" repeatCount="indefinite" />
            </line>
        </svg>
    )
}

function ChartIllustration() {
    return (
        <svg viewBox="0 0 300 200" className="w-full h-auto" fill="none">
            {/* Bars */}
            <rect x="30" y="140" width="30" height="40" rx="4" fill="#22c55e" />
            <rect x="80" y="100" width="30" height="80" rx="4" fill="#22c55e" />
            <rect x="130" y="60" width="30" height="120" rx="4" fill="#eab308" />
            <rect x="180" y="80" width="30" height="100" rx="4" fill="#22c55e" />
            <rect x="230" y="40" width="30" height="140" rx="4" fill="#ef4444" />
            {/* Labels */}
            <text x="45" y="195" textAnchor="middle" className="text-xs" fill="#6b7280">Mon</text>
            <text x="95" y="195" textAnchor="middle" className="text-xs" fill="#6b7280">Tue</text>
            <text x="145" y="195" textAnchor="middle" className="text-xs" fill="#6b7280">Wed</text>
            <text x="195" y="195" textAnchor="middle" className="text-xs" fill="#6b7280">Thu</text>
            <text x="245" y="195" textAnchor="middle" className="text-xs" fill="#6b7280">Fri</text>
        </svg>
    )
}
