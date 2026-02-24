import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { Upload, Camera, X, FileImage, ArrowLeft, CheckCircle, Loader2, AlertTriangle } from 'lucide-react';

const Scan = () => {
    const { categoryId } = useParams();
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const [selectedImage, setSelectedImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [claims, setClaims] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const [showUnclearPopup, setShowUnclearPopup] = useState(false);

    const categoryNames = {
        'protein-powder': 'Protein Powder',
        'protein-bars': 'Protein Bars',
        'dairy-products': 'Dairy Products',
        'energy-drinks': 'Energy Drinks'
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileInput = (e) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        if (file.type.startsWith('image/')) {
            setSelectedImage(file);
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const removeImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // Simulate image clarity check (in real app, this would use image processing)
    const checkImageClarity = () => {
        // Simulate: randomly determine if image is unclear (30% chance for demo)
        // In production, this would use actual image analysis
        return Math.random() > 0.3;
    };

    const handleCheck = async () => {
        if (!selectedImage) return;

        setIsAnalyzing(true);
        // Simulate analysis delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Check image clarity
        const isImageClear = checkImageClarity();

        if (!isImageClear) {
            setIsAnalyzing(false);
            setShowUnclearPopup(true);
            return;
        }

        setIsAnalyzing(false);
        // Navigate to results page (to be implemented)
        // navigate('/dashboard/results');
        alert('Analysis complete! Results page coming soon.');
    };

    const handleRetryUpload = () => {
        setShowUnclearPopup(false);
        removeImage();
    };

    const handleTryAnyway = () => {
        setShowUnclearPopup(false);
        alert('Analysis complete! Results page coming soon.');
    };

    return (
        <div className="min-h-screen py-8 px-6 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-40 right-1/4 w-[400px] h-[400px] bg-nutri-mint/10 rounded-full blur-[100px] pointer-events-none" />

            <div className="max-w-3xl mx-auto relative z-10">
                {/* Back Button */}
                <motion.button
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center gap-2 text-gray-400 hover:text-white mb-6 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5" />
                    <span>Back to Categories</span>
                </motion.button>

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="mb-8"
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-nutri-mint/10 border border-nutri-mint/30 mb-4">
                        <span className="text-xs font-medium text-nutri-mint">
                            {categoryNames[categoryId] || 'Product'}
                        </span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
                        Scan Ingredients
                    </h1>
                    <p className="text-gray-400">
                        Upload an image of the ingredient list and enter any health claims to verify
                    </p>
                </motion.div>

                {/* Upload Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="mb-8"
                >
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                        Ingredient Image
                    </label>

                    <AnimatePresence mode="wait">
                        {!imagePreview ? (
                            <motion.div
                                key="upload"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                onDragEnter={handleDrag}
                                onDragLeave={handleDrag}
                                onDragOver={handleDrag}
                                onDrop={handleDrop}
                                className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${dragActive
                                    ? 'border-nutri-mint bg-nutri-mint/5'
                                    : 'border-white/20 hover:border-white/40 bg-white/[0.02]'
                                    }`}
                            >
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileInput}
                                    className="hidden"
                                />

                                <div className="flex flex-col items-center">
                                    <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mb-4">
                                        <Upload className="w-8 h-8 text-gray-400" />
                                    </div>
                                    <p className="text-white font-medium mb-2">
                                        Drag and drop your image here
                                    </p>
                                    <p className="text-gray-500 text-sm mb-6">
                                        or
                                    </p>
                                    <div className="flex gap-4">
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={() => fileInputRef.current?.click()}
                                            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-colors"
                                        >
                                            <FileImage className="w-5 h-5" />
                                            Upload image
                                        </motion.button>
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-nutri-mint/10 border border-nutri-mint/30 text-nutri-mint hover:bg-nutri-mint/20 transition-colors"
                                        >
                                            <Camera className="w-5 h-5" />
                                            Take Photo
                                        </motion.button>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="preview"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                className="relative rounded-2xl overflow-hidden bg-white/5 border border-white/10"
                            >
                                <img
                                    src={imagePreview}
                                    alt="Selected ingredient"
                                    className="w-full h-64 object-contain bg-black/50"
                                />
                                <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={removeImage}
                                    className="absolute top-4 right-4 w-10 h-10 rounded-full bg-red-500/80 backdrop-blur-sm flex items-center justify-center text-white hover:bg-red-500 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </motion.button>
                                <div className="p-4 border-t border-white/10">
                                    <p className="text-sm text-gray-400">
                                        <span className="text-white font-medium">{selectedImage.name}</span>
                                        {' '}({(selectedImage.size / 1024).toFixed(1)} KB)
                                    </p>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>

                {/* Claims Input */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="mb-8"
                >
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                        Product Claims
                    </label>
                    <div className="relative">
                        <textarea
                            value={claims}
                            onChange={(e) => setClaims(e.target.value)}
                            placeholder="Enter the health claims made by this product (e.g., 'High protein, low sugar, no artificial colors')"
                            rows={4}
                            className="w-full bg-white/[0.03] border border-white/10 rounded-2xl p-4 text-white placeholder-gray-500 focus:outline-none focus:border-nutri-mint/50 focus:ring-1 focus:ring-nutri-mint/50 transition-all resize-none"
                        />
                    </div>
                    <p className="text-gray-500 text-sm mt-2">
                        We'll verify these claims against the actual ingredients
                    </p>
                </motion.div>

                {/* Check Button */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                >
                    <motion.button
                        whileHover={{ scale: selectedImage ? 1.02 : 1 }}
                        whileTap={{ scale: selectedImage ? 0.98 : 1 }}
                        onClick={handleCheck}
                        disabled={!selectedImage || isAnalyzing}
                        className={`w-full py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-3 transition-all duration-300 ${selectedImage
                            ? 'bg-gradient-to-r from-nutri-mint to-teal-400 text-black shadow-lg shadow-nutri-mint/30 hover:shadow-nutri-mint/50'
                            : 'bg-white/10 text-gray-500 cursor-not-allowed'
                            }`}
                    >
                        {isAnalyzing ? (
                            <>
                                <Loader2 className="w-6 h-6 animate-spin" />
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <CheckCircle className="w-6 h-6" />
                                Check Ingredients
                            </>
                        )}
                    </motion.button>
                </motion.div>

                {/* Tips */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="mt-8 p-4 rounded-xl bg-white/[0.02] border border-white/10"
                >
                    <p className="text-sm text-gray-400">
                        <span className="text-nutri-mint font-medium">Tip:</span> For best results, ensure the ingredient list is clearly visible and well-lit in the image.
                    </p>
                </motion.div>
            </div>

            {/* Unclear Image Popup Modal */}
            <AnimatePresence>
                {showUnclearPopup && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowUnclearPopup(false)}
                            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
                        />

                        {/* Modal */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            transition={{ type: "spring", damping: 25, stiffness: 300 }}
                            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md mx-4"
                        >
                            <div className="bg-gray-900 border border-white/10 rounded-3xl p-8 shadow-2xl">
                                {/* Icon */}
                                <div className="flex justify-center mb-6">
                                    <motion.div
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
                                        className="w-20 h-20 rounded-full bg-amber-500/20 flex items-center justify-center"
                                    >
                                        <AlertTriangle className="w-10 h-10 text-amber-500" />
                                    </motion.div>
                                </div>

                                {/* Content */}
                                <div className="text-center mb-8">
                                    <h3 className="text-2xl font-bold text-white mb-3">
                                        Image Not Clear
                                    </h3>
                                    <p className="text-gray-400 leading-relaxed">
                                        The uploaded image appears to be blurry, dark, or the ingredient list is not clearly visible. Please upload a clearer image for accurate analysis.
                                    </p>
                                </div>

                                {/* Actions */}
                                <div className="flex flex-col gap-3">
                                    <motion.button
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={handleRetryUpload}
                                        className="w-full py-4 rounded-xl bg-gradient-to-r from-nutri-mint to-teal-400 text-black font-bold text-lg shadow-lg shadow-nutri-mint/20"
                                    >
                                        Upload New Image
                                    </motion.button>
                                    <motion.button
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={handleTryAnyway}
                                        className="w-full py-4 rounded-xl bg-white/10 border border-white/20 text-white font-medium hover:bg-white/20 transition-colors"
                                    >
                                        Try Anyway
                                    </motion.button>
                                </div>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Scan;
