import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Clock, ChevronRight, Target, Zap, ArrowLeft } from 'lucide-react';
import VerdictBadge from '../components/VerdictBadge';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
};

const History = () => {
    const navigate = useNavigate();
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        api.getScanHistory()
            .then(setScans)
            .catch((err) => setError(err.message || 'Failed to load scan history.'))
            .finally(() => setLoading(false));
    }, []);

    const formatDate = (iso) => {
        if (!iso) return '';
        return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    };

    return (
        <motion.div
            variants={pageVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.4 }}
            className="min-h-screen py-10 px-6 relative overflow-hidden"
        >
            <div className="absolute top-20 right-1/4 w-[400px] h-[400px] bg-nutri-mint/6 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-3xl mx-auto relative z-10">
                {/* Header */}
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-4">
                        <Clock className="w-3.5 h-3.5 text-nutri-mint" />
                        <span className="text-xs font-semibold text-nutri-mint">Scan History</span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Past Scans</h1>
                    <p className="text-gray-400">Review your previous ingredient analyses.</p>
                </motion.div>

                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <span className="w-8 h-8 border-2 border-nutri-mint/40 border-t-nutri-mint rounded-full animate-spin" />
                    </div>
                ) : error ? (
                    <div className="text-center py-16">
                        <p className="text-nutri-red mb-4">{error}</p>
                        <motion.button
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => window.location.reload()}
                            className="px-6 py-3 rounded-xl bg-white/10 text-white font-medium"
                        >
                            Retry
                        </motion.button>
                    </div>
                ) : scans.length === 0 ? (
                    <div className="text-center py-20">
                        <Clock className="w-14 h-14 text-gray-700 mx-auto mb-4" />
                        <p className="text-gray-500 text-lg">No scans yet.</p>
                        <motion.button
                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/dashboard')}
                            className="mt-6 px-6 py-3 rounded-xl bg-nutri-mint text-black font-bold hover:bg-nutri-mint-light transition-colors"
                        >
                            Start Scanning
                        </motion.button>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {scans.map((scan, i) => (
                            <motion.button
                                key={scan.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.08 }}
                                whileHover={{ y: -2, transition: { duration: 0.15 } }}
                                whileTap={{ scale: 0.99 }}
                                onClick={() => navigate(`/results/${scan.id}`)}
                                className="w-full p-5 rounded-2xl bg-white/[0.03] border border-white/10 hover:border-white/20 hover:bg-white/[0.05] transition-all text-left group"
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1 min-w-0">
                                        <div className="flex flex-wrap items-center gap-2 mb-2">
                                            <VerdictBadge verdict={scan.final_verdict} size="sm" />
                                            <span className="flex items-center gap-1 text-xs text-gray-500 bg-white/5 border border-white/10 px-2 py-0.5 rounded-full">
                                                {scan.scan_mode === 'PRECISION' ? <Target className="w-3 h-3" /> : <Zap className="w-3 h-3" />}
                                                {scan.scan_mode === 'PRECISION' ? 'Precision' : 'Quick'}
                                            </span>
                                        </div>
                                        <p className="text-white font-semibold text-sm mb-1 truncate">{scan.user_claim}</p>
                                        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                                            <span className="bg-white/5 px-2 py-0.5 rounded-full">{scan.category}</span>
                                            <span>{formatDate(scan.created_at)}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3 flex-shrink-0">
                                        <div className="text-right">
                                            <p className="text-xs text-gray-500">Score</p>
                                            <p className="text-lg font-bold text-white">{scan.score != null ? `${scan.score}%` : '—'}</p>
                                        </div>
                                        <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-nutri-mint group-hover:translate-x-1 transition-all" />
                                    </div>
                                </div>
                            </motion.button>
                        ))}
                    </div>
                )}
            </div>
        </motion.div>
    );
};

export default History;
