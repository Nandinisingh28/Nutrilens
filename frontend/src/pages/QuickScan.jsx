import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, ArrowLeft } from 'lucide-react';
import ImageUpload from '../components/ImageUpload';
import { CATEGORIES, TipIcon, CLAIM_ICONS } from '../utils/icons';
import { scansAPI } from '../api/client';

function QuickScan() {
    const navigate = useNavigate();
    const [image, setImage] = useState(null);
    const [claim, setClaim] = useState('');
    const [category, setCategory] = useState('PROTEIN_BAR');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validate inputs
        if (!image) {
            setError('Please upload an image');
            return;
        }
        if (!claim.trim()) {
            setError('Please enter a claim to verify');
            return;
        }

        setLoading(true);

        try {
            // Create form data
            const formData = new FormData();
            formData.append('image', image);
            formData.append('claim', claim);
            formData.append('category', category);

            // Submit scan
            const response = await scansAPI.quickScan(formData);

            // Navigate to results
            navigate(`/results/${response.data.scan_id}`);
        } catch (err) {
            const message = err.response?.data?.detail || 'Failed to process scan. Please try again.';
            setError(message);
        }

        setLoading(false);
    };

    return (
        <div className="animate-fadeIn">
            <button
                className="btn btn-ghost"
                onClick={() => navigate('/dashboard')}
                style={{ marginBottom: 'var(--spacing-6)' }}
            >
                <ArrowLeft size={18} />
                Back to Dashboard
            </button>

            <div className="card">
                <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-8)' }}>
                    <div style={{
                        width: '64px',
                        height: '64px',
                        background: 'var(--gradient-secondary)',
                        borderRadius: 'var(--radius-xl)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto var(--spacing-4)'
                    }}>
                        <Zap size={32} color="white" />
                    </div>
                    <h1 style={{ marginBottom: 'var(--spacing-2)' }}>Quick Scan</h1>
                    <p style={{ color: 'var(--color-neutral-400)' }}>
                        Upload a single image containing both nutrition and ingredients
                    </p>
                </div>

                {error && (
                    <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    {/* Category Selection */}
                    <div className="form-group">
                        <label className="form-label">Product Category</label>
                        <div className="category-select" style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(3, 1fr)',
                            gap: 'var(--spacing-2)',
                            maxHeight: '240px',
                            overflowY: 'auto',
                        }}>
                            {CATEGORIES.map(({ key, Icon, label }) => (
                                <div
                                    key={key}
                                    className={`category-option ${category === key ? 'active' : ''}`}
                                    onClick={() => setCategory(key)}
                                >
                                    <span style={{ display: 'block', marginBottom: '4px' }}><Icon size={24} /></span>
                                    <span className="category-option-label">{label}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Claim Input */}
                    <div className="form-group">
                        <label className="form-label" htmlFor="claim">Claim to Verify</label>
                        <select
                            id="claim"
                            className="form-input"
                            value={claim}
                            onChange={(e) => setClaim(e.target.value)}
                            required
                        >
                            <option value="">Select a claim to verify</option>
                            {Object.keys(CLAIM_ICONS).sort().map((claimName) => (
                                <option key={claimName} value={claimName}>
                                    {claimName}
                                </option>
                            ))}
                        </select>
                        <p style={{
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--color-neutral-500)',
                            marginTop: 'var(--spacing-2)'
                        }}>
                            Select the marketing claim from the package you want to verify
                        </p>
                    </div>

                    {/* Image Upload */}
                    <div className="form-group">
                        <label className="form-label">Product Label Image</label>
                        <ImageUpload
                            label="Upload Product Label"
                            hint="Photo showing both nutrition facts and ingredients"
                            onFileSelect={setImage}
                        />
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        className="btn btn-primary btn-lg w-full"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <div className="spinner"></div>
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <Zap size={20} />
                                Quick Analyze
                            </>
                        )}
                    </button>
                </form>

                <div className="alert alert-info" style={{ marginTop: 'var(--spacing-6)' }}>
                    <p style={{ margin: 0, fontSize: 'var(--font-size-sm)' }}>
                        <TipIcon size={14} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 4 }} /> <strong>Tip:</strong> For best results, make sure both the nutrition table and ingredients list are visible and in focus. Consider using Precision Scan for more accurate results.
                    </p>
                </div>
            </div>
        </div >
    );
}

export default QuickScan;
