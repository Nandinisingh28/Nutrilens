import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Target, ArrowLeft } from 'lucide-react';
import ImageUpload from '../components/ImageUpload';
import { CATEGORIES, CLAIM_ICONS } from '../utils/icons';
import { scansAPI } from '../api/client';

function PrecisionScan() {
    const navigate = useNavigate();
    const [nutritionImage, setNutritionImage] = useState(null);
    const [ingredientsImage, setIngredientsImage] = useState(null);
    const [claim, setClaim] = useState('');
    const [category, setCategory] = useState('PROTEIN_BAR');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validate inputs
        if (!nutritionImage) {
            setError('Please upload a nutrition facts image');
            return;
        }
        if (!ingredientsImage) {
            setError('Please upload an ingredients image');
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
            formData.append('nutrition_image', nutritionImage);
            formData.append('ingredients_image', ingredientsImage);
            formData.append('claim', claim);
            formData.append('category', category);

            // Submit scan
            const response = await scansAPI.precisionScan(formData);

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
                        background: 'var(--gradient-primary)',
                        borderRadius: 'var(--radius-xl)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto var(--spacing-4)'
                    }}>
                        <Target size={32} color="white" />
                    </div>
                    <h1 style={{ marginBottom: 'var(--spacing-2)' }}>Precision Scan</h1>
                    <p style={{ color: 'var(--color-neutral-400)' }}>
                        Upload separate images for the most accurate analysis
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

                    {/* Image Uploads */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: 'var(--spacing-4)',
                        marginBottom: 'var(--spacing-6)'
                    }}>
                        <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Nutrition Facts Image</label>
                            <ImageUpload
                                label="Upload Nutrition Facts"
                                hint="Clear photo of the nutrition table"
                                onFileSelect={setNutritionImage}
                            />
                        </div>

                        <div className="form-group" style={{ marginBottom: 0 }}>
                            <label className="form-label">Ingredients Image</label>
                            <ImageUpload
                                label="Upload Ingredients List"
                                hint="Clear photo of the ingredients"
                                onFileSelect={setIngredientsImage}
                            />
                        </div>
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
                                <Target size={20} />
                                Analyze Product
                            </>
                        )}
                    </button>
                </form>
            </div>
        </div >
    );
}

export default PrecisionScan;
