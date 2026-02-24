import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Target, Loader2, CheckCircle, AlertTriangle, X } from 'lucide-react';
import ImageUploadZone from '../components/ImageUploadZone';
import * as api from '../utils/api';

const pageVariants = {
    initial: { opacity: 0, y: 16 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -16 },
};

// Backend accepts PROTEIN_BAR or BREAKFAST_CEREAL; show friendly names mapped to those values
const CATEGORIES = [
    { label: 'Protein Bar', value: 'PROTEIN_BAR' },
    { label: 'Breakfast Cereal', value: 'BREAKFAST_CEREAL' },
];

const PrecisionScan = () => {
    const navigate = useNavigate();
    const [nutritionImage, setNutritionImage] = useState(null);
    const [ingredientsImage, setIngredientsImage] = useState(null);
    const [nutritionPreview, setNutritionPreview] = useState(null);
    const [ingredientsPreview, setIngredientsPreview] = useState(null);
    const [category, setCategory] = useState('PROTEIN_BAR');
    const [claim, setClaim] = useState('');
    const [errors, setErrors] = useState({});
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [serverError, setServerError] = useState('');

    const readFile = (file) =>
        new Promise((res) => {
            const reader = new FileReader();
            reader.onload = (e) => res(e.target.result);
            reader.readAsDataURL(file);
        });

    const handleNutritionChange = async (file) => {
        setNutritionImage(file);
        setNutritionPreview(await readFile(file));
        setErrors((p) => ({ ...p, nutritionImage: '' }));
    };

    const handleIngredientsChange = async (file) => {
        setIngredientsImage(file);
        setIngredientsPreview(await readFile(file));
        setErrors((p) => ({ ...p, ingredientsImage: '' }));
    };

    const validate = () => {
        const errs = {};
        if (!nutritionImage) errs.nutritionImage = 'Nutrition facts image is required';
        if (!ingredientsImage) errs.ingredientsImage = 'Ingredients image is required';
        if (!claim.trim()) errs.claim = 'Please enter at least one claim to verify';
        return errs;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const errs = validate();
        if (Object.keys(errs).length) { setErrors(errs); return; }

        setIsAnalyzing(true);
        setServerError('');
        try {
            const result = await api.precisionScan({
                nutritionImage,
                ingredientsImage,
                claim,
                category,
            });
            navigate(`/results/${result.id}`, { state: { result } });
        } catch (err) {
            setServerError(err.message || 'Analysis failed. Please try again.');
        } finally {
            setIsAnalyzing(false);
        }
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
            <div className="absolute top-40 right-1/4 w-[400px] h-[400px] bg-nutri-mint/8 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-3xl mx-auto relative z-10">
                {/* Back */}
                <motion.button
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center gap-2 text-gray-400 hover:text-white mb-7 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                </motion.button>

                {/* Header */}
                <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-4">
                        <Target className="w-3.5 h-3.5 text-nutri-mint" />
                        <span className="text-xs font-semibold text-nutri-mint">Precision Scan</span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">Upload Two Images</h1>
                    <p className="text-gray-400">Provide the Nutrition Facts and Ingredients list separately for the most accurate analysis.</p>
                </motion.div>

                {serverError && (
                    <motion.div
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-6 px-4 py-3 rounded-xl bg-nutri-red/10 border border-nutri-red/30 text-nutri-red text-sm text-center"
                    >
                        {serverError}
                    </motion.div>
                )}

                <form onSubmit={handleSubmit} className="space-y-7">
                    {/* Category */}
                    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Product Category</label>
                        <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full bg-black/30 border border-white/10 rounded-xl py-3 px-4 text-white focus:outline-none focus:border-nutri-mint/50 focus:ring-1 focus:ring-nutri-mint/30 transition-all appearance-none cursor-pointer"
                        >
                            {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
                        </select>
                    </motion.div>

                    {/* Image uploads */}
                    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid md:grid-cols-2 gap-5">
                        <ImageUploadZone
                            label="1. Nutrition Facts Label"
                            preview={nutritionPreview}
                            onChange={handleNutritionChange}
                            onRemove={() => { setNutritionImage(null); setNutritionPreview(null); }}
                            error={errors.nutritionImage}
                        />
                        <ImageUploadZone
                            label="2. Ingredients List"
                            preview={ingredientsPreview}
                            onChange={handleIngredientsChange}
                            onRemove={() => { setIngredientsImage(null); setIngredientsPreview(null); }}
                            error={errors.ingredientsImage}
                        />
                    </motion.div>

                    {/* Claim */}
                    <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Health Claims to Verify</label>
                        <textarea
                            value={claim}
                            onChange={(e) => { setClaim(e.target.value); setErrors((p) => ({ ...p, claim: '' })); }}
                            placeholder="e.g. High Protein and Low Sugar"
                            rows={3}
                            className={`w-full bg-white/[0.03] border rounded-2xl p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-1 transition-all resize-none ${errors.claim ? 'border-nutri-red/60 focus:border-nutri-red focus:ring-nutri-red/30' : 'border-white/10 focus:border-nutri-mint/50 focus:ring-nutri-mint/30'}`}
                        />
                        {errors.claim && <p className="mt-1.5 text-xs text-nutri-red">{errors.claim}</p>}
                        <p className="text-gray-500 text-xs mt-2">Separate multiple claims with commas.</p>
                    </motion.div>

                    {/* Submit */}
                    <motion.button
                        type="submit"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        disabled={isAnalyzing}
                        className="w-full py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 bg-gradient-to-r from-nutri-mint to-teal-400 text-black shadow-lg shadow-nutri-mint/25 hover:shadow-nutri-mint/40 transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {isAnalyzing ? (
                            <><Loader2 className="w-6 h-6 animate-spin" /> Analyzing...</>
                        ) : (
                            <><CheckCircle className="w-6 h-6" /> Run Precision Analysis</>
                        )}
                    </motion.button>
                </form>

                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="mt-6 p-4 rounded-xl bg-white/[0.02] border border-white/10">
                    <p className="text-sm text-gray-400">
                        <span className="text-nutri-mint font-medium">Tip:</span> For best accuracy, ensure both images are well-lit and text is clearly visible.
                    </p>
                </motion.div>
            </div>
        </motion.div>
    );
};

export default PrecisionScan;
