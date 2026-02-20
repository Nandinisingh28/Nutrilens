import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { History as HistoryIcon, ChevronRight, Search } from 'lucide-react';
import VerdictBadge from '../components/VerdictBadge';
import { scansAPI } from '../api/client';

function History() {
    const navigate = useNavigate();
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const response = await scansAPI.getHistory();
                setScans(response.data);
            } catch (err) {
                setError('Failed to load scan history');
            }
            setLoading(false);
        };

        fetchHistory();
    }, []);

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getCategoryLabel = (category) => {
        const labels = {
            PROTEIN_BAR: '🥜 Protein Bar',
            BREAKFAST_CEREAL: '🥣 Cereal',
            BISCUITS_COOKIES: '🍪 Biscuits',
            SNACKS: '🍿 Snacks',
            CHOCOLATES_CONFECTIONERY: '🍫 Chocolate',
            BEVERAGES: '🥤 Beverages',
            ENERGY_DRINKS: '⚡ Energy Drinks',
            DAIRY_PRODUCTS: '🥛 Dairy',
            INSTANT_NOODLES_RTE: '🍜 Noodles/RTE',
            SAUCES_SPREADS: '🫙 Sauces',
            HEALTH_SUPPLEMENTS: '💊 Supplements',
            FROZEN_FOODS: '🧊 Frozen',
        };
        return labels[category] || category;
    };

    if (loading) {
        return (
            <div className="loading-overlay" style={{ position: 'static', minHeight: '400px' }}>
                <div className="spinner spinner-lg"></div>
                <p className="loading-text">Loading history...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-error">
                {error}
            </div>
        );
    }

    return (
        <div className="animate-fadeIn">
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: 'var(--spacing-8)'
            }}>
                <div>
                    <h1 style={{ marginBottom: 'var(--spacing-2)' }}>Scan History</h1>
                    <p style={{ color: 'var(--color-neutral-400)', marginBottom: 0 }}>
                        {scans.length} scan{scans.length !== 1 ? 's' : ''} completed
                    </p>
                </div>
                <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
                    New Scan
                </button>
            </div>

            {scans.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">
                        <Search size={80} />
                    </div>
                    <h3 className="empty-state-title">No scans yet</h3>
                    <p className="empty-state-text">
                        You haven't analyzed any products yet. Start by scanning a food label!
                    </p>
                    <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
                        Start Your First Scan
                    </button>
                </div>
            ) : (
                <div className="history-list">
                    {scans.map((scan) => (
                        <div
                            key={scan.scan_id}
                            className="history-item"
                            onClick={() => navigate(`/results/${scan.scan_id}`)}
                        >
                            <div className="history-item-main">
                                <div className="history-item-claim">
                                    "{scan.user_claim}"
                                </div>
                                <div className="history-item-meta">
                                    <span>{getCategoryLabel(scan.category)}</span>
                                    <span>•</span>
                                    <span>{scan.scan_mode} Scan</span>
                                    <span>•</span>
                                    <span>{formatDate(scan.created_at)}</span>
                                </div>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-4)' }}>
                                {scan.score !== null && (
                                    <span className="history-item-score">
                                        {Math.round(scan.score)}%
                                    </span>
                                )}
                                {scan.final_verdict && (
                                    <VerdictBadge verdict={scan.final_verdict} />
                                )}
                                <ChevronRight size={20} color="var(--color-neutral-500)" />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default History;
