import { Link } from 'react-router-dom'
import { Heart } from 'lucide-react'

export function Footer() {
    return (
        <footer className="border-t border-gray-200/50 bg-white/50 backdrop-blur-sm">
            <div className="container py-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    {/* Brand */}
                    <div className="space-y-4">
                        <div className="flex items-center space-x-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-teal-500 flex items-center justify-center">
                                <Heart className="w-4 h-4 text-white" />
                            </div>
                            <span className="font-bold text-lg">NutriLens</span>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            Smart nutrition scanning powered by AI. Make healthier choices effortlessly.
                        </p>
                    </div>

                    {/* Product */}
                    <div>
                        <h4 className="font-semibold mb-4">Product</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><Link to="/app" className="hover:text-foreground transition-colors">Scan Labels</Link></li>
                            <li><Link to="/app/history" className="hover:text-foreground transition-colors">History</Link></li>
                            <li><a href="#features" className="hover:text-foreground transition-colors">Features</a></li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h4 className="font-semibold mb-4">Company</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><a href="#" className="hover:text-foreground transition-colors">About</a></li>
                            <li><a href="#" className="hover:text-foreground transition-colors">Contact</a></li>
                            <li><a href="#" className="hover:text-foreground transition-colors">Privacy</a></li>
                        </ul>
                    </div>

                    {/* Connect */}
                    <div>
                        <h4 className="font-semibold mb-4">Connect</h4>
                        <ul className="space-y-2 text-sm text-muted-foreground">
                            <li><a href="#" className="hover:text-foreground transition-colors">Twitter</a></li>
                            <li><a href="#" className="hover:text-foreground transition-colors">GitHub</a></li>
                            <li><a href="#" className="hover:text-foreground transition-colors">Discord</a></li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-200 mt-8 pt-8 text-center text-sm text-muted-foreground">
                    <p>© 2024 NutriLens. All rights reserved.</p>
                </div>
            </div>
        </footer>
    )
}
