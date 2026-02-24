import React, { useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileImage, X } from 'lucide-react';

const ImageUploadZone = ({ label, preview, onChange, onRemove, error }) => {
    const fileInputRef = useRef(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(e.type === 'dragenter' || e.type === 'dragover');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        const file = e.dataTransfer.files?.[0];
        if (file?.type.startsWith('image/')) onChange(file);
    };

    const handleFileInput = (e) => {
        const file = e.target.files?.[0];
        if (file) { onChange(file); e.target.value = ''; }
    };

    return (
        <div>
            {label && (
                <p className="text-sm font-medium text-gray-300 mb-3">{label}</p>
            )}
            <AnimatePresence mode="wait">
                {!preview ? (
                    <motion.div
                        key="dropzone"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        className={`relative border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-200 ${
                            error
                                ? 'border-nutri-red/50 bg-nutri-red/5'
                                : dragActive
                                ? 'border-nutri-mint bg-nutri-mint/5'
                                : 'border-white/20 hover:border-white/40 bg-white/[0.02] hover:bg-white/[0.04]'
                        }`}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleFileInput}
                            className="hidden"
                        />
                        <div className="flex flex-col items-center gap-3">
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${dragActive ? 'bg-nutri-mint/20' : 'bg-white/5'}`}>
                                <Upload className={`w-6 h-6 ${dragActive ? 'text-nutri-mint' : 'text-gray-400'}`} />
                            </div>
                            <div>
                                <p className="text-white text-sm font-medium">Drop image here or click to upload</p>
                                <p className="text-gray-500 text-xs mt-1">PNG, JPG, WEBP up to 10MB</p>
                            </div>
                            <motion.span
                                whileHover={{ scale: 1.05 }}
                                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-sm text-white hover:bg-white/20 transition-colors"
                            >
                                <FileImage className="w-4 h-4" /> Browse
                            </motion.span>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="preview"
                        initial={{ opacity: 0, scale: 0.96 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.96 }}
                        className="relative rounded-2xl overflow-hidden bg-white/5 border border-white/10"
                    >
                        <img
                            src={preview}
                            alt="Uploaded"
                            className="w-full h-48 object-contain bg-black/40"
                        />
                        <button
                            type="button"
                            onClick={onRemove}
                            className="absolute top-3 right-3 w-8 h-8 rounded-full bg-red-500/80 hover:bg-red-500 flex items-center justify-center text-white transition-colors"
                        >
                            <X className="w-4 h-4" />
                        </button>
                        <div className="px-4 py-2 border-t border-white/10">
                            <p className="text-xs text-nutri-mint font-medium flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-nutri-mint inline-block" />
                                Image ready
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
            {error && <p className="mt-1.5 text-xs text-nutri-red">{error}</p>}
        </div>
    );
};

export default ImageUploadZone;
