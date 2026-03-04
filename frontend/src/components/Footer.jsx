import React from 'react';
import { Twitter, Linkedin, Github } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer className="bg-black pt-24 pb-12 border-t border-white/5 relative z-10">
            <div className="max-w-[1200px] mx-auto px-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">

                    <div className="col-span-1 md:col-span-1">
                        <Link to="/" className="flex items-center gap-3 mb-6 hover:opacity-80 transition-opacity">
                            <img src="/logo.png" alt="NutriLens Logo" className="h-8 w-auto brightness-0 invert opacity-90" />
                            <span className="text-xl font-bold text-white tracking-tight">
                                Nutri<span className="text-nutri-mint">Lens</span>
                            </span>
                        </Link>
                        <p className="text-gray-400 text-sm leading-relaxed font-light">
                            Making food transparency accessible to everyone. Scan, analyze, and eat smarter with AI-powered insights.
                        </p>
                    </div>

                    <div>
                        <h4 className="text-xs font-semibold text-gray-200 uppercase tracking-widest mb-6">Product</h4>
                        <ul className="space-y-4">
                            <li><a href="#" className="text-gray-500 hover:text-white transition-colors text-sm font-medium">Features</a></li>
                            <li><a href="#" className="text-gray-500 hover:text-white transition-colors text-sm font-medium">Use Cases</a></li>
                            <li><a href="#" className="text-gray-500 hover:text-white transition-colors text-sm font-medium">Pricing</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-xs font-semibold text-gray-200 uppercase tracking-widest mb-6">Company</h4>
                        <ul className="space-y-4">
                            <li><a href="#" className="text-gray-500 hover:text-white transition-colors text-sm font-medium">About</a></li>
                            <li><a href="#" className="text-gray-500 hover:text-white transition-colors text-sm font-medium">Contact</a></li>
                            <li><a href="#" className="text-gray-500 hover:text-white transition-colors text-sm font-medium">Privacy Policy</a></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-xs font-semibold text-gray-200 uppercase tracking-widest mb-6">Connect</h4>
                        <div className="flex space-x-5">
                            <a href="#" className="text-gray-500 hover:text-white transition-colors">
                                <span className="sr-only">Twitter</span>
                                <Twitter className="h-5 w-5" />
                            </a>
                            <a href="#" className="text-gray-500 hover:text-white transition-colors">
                                <span className="sr-only">LinkedIn</span>
                                <Linkedin className="h-5 w-5" />
                            </a>
                            <a href="#" className="text-gray-500 hover:text-white transition-colors">
                                <span className="sr-only">GitHub</span>
                                <Github className="h-5 w-5" />
                            </a>
                        </div>
                    </div>
                </div>

                <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-600 font-light">
                    <p>
                        &copy; {new Date().getFullYear()} NutriLens. All rights reserved.
                    </p>
                    <p className="mt-2 md:mt-0">
                        Designed for health-conscious living.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
