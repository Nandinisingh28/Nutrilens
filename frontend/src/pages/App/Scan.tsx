import { useState, useCallback, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { useMutation } from '@tanstack/react-query'
import { toast } from 'sonner'
import {
    Upload,
    Image as ImageIcon,
    X,
    Loader2,
    Camera,
    Sparkles,
    ArrowLeft,
    Check,
    FileSearch,
    ListChecks,
    Brain,
    Beaker,
} from 'lucide-react'
import { scanApi } from '@/app/api'

const processingSteps = [
    { id: 'upload', label: 'Uploading image', icon: Upload, duration: 800 },
    { id: 'ocr', label: 'Running OCR', icon: FileSearch, duration: 2000 },
    { id: 'parse', label: 'Parsing ingredients', icon: ListChecks, duration: 1500 },
    { id: 'analyze', label: 'Analyzing claims', icon: Brain, duration: 2000 },
    { id: 'generate', label: 'Generating results', icon: Beaker, duration: 1000 },
]

function ProcessingOverlay({ isProcessing, error, onRetry }: { isProcessing: boolean; error: any; onRetry: () => void }) {
    const [currentStep, setCurrentStep] = useState(0)
    const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set())
    const [failedStep, setFailedStep] = useState<number | null>(null)

    const isOcrError = error?.response?.data?.error?.code === 'OCR_QUALITY_LOW' ||
        error?.response?.data?.error?.code === 'LOW_RESOLUTION'

    useEffect(() => {
        // Reset everything if not processing and no error (clean exit)
        if (!isProcessing && !error) {
            setCurrentStep(0)
            setCompletedSteps(new Set())
            setFailedStep(null)
            return
        }

        // If we have an error, stop everything and mark the failure
        if (error) {
            setFailedStep(currentStep)
            return
        }

        // Only start the animation if we are processing and have no error and haven't failed yet
        if (!isProcessing || failedStep !== null) return

        let active = true
        let step = currentStep

        const advance = () => {
            if (!active || step >= processingSteps.length) return

            setCurrentStep(step)
            const timer = setTimeout(() => {
                if (!active) return

                setCompletedSteps(prev => {
                    const next = new Set(prev)
                    next.add(step)
                    return next
                })

                step++
                if (step < processingSteps.length && active) {
                    advance()
                }
            }, processingSteps[step].duration)

            timers.push(timer)
        }

        const timers: NodeJS.Timeout[] = []
        advance()

        return () => {
            active = false
            timers.forEach(t => clearTimeout(t))
        }
    }, [isProcessing, !!error])

    return (
        <AnimatePresence>
            {isProcessing && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center"
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="bg-white dark:bg-gray-900 rounded-3xl p-8 max-w-md w-full mx-4 shadow-2xl"
                    >
                        <div className="text-center mb-8">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                                className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-tr from-primary to-teal-400 flex items-center justify-center"
                            >
                                <Sparkles className="w-8 h-8 text-white" />
                            </motion.div>
                            <h2 className="text-xl font-bold mb-1">Analyzing Your Label</h2>
                            <p className="text-muted-foreground text-sm">
                                Please wait while we process your image
                            </p>
                        </div>

                        <div className="space-y-3">
                            {processingSteps.map((step, index) => {
                                const Icon = step.icon
                                const isFailed = failedStep === index
                                const isCompleted = completedSteps.has(index) && !isFailed
                                const isActive = currentStep === index && !isFailed && !isCompleted

                                return (
                                    <motion.div
                                        key={step.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className={`flex items-center gap-4 p-3 rounded-xl transition-all ${isActive
                                            ? 'bg-primary/10 border border-primary/20'
                                            : isCompleted
                                                ? 'bg-green-50 dark:bg-green-900/20'
                                                : isFailed
                                                    ? 'bg-red-50 dark:bg-red-900/20 border border-red-200'
                                                    : 'bg-gray-50 dark:bg-gray-800/50'
                                            }`}
                                    >
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${isCompleted
                                            ? 'bg-green-500 text-white'
                                            : isFailed
                                                ? 'bg-red-500 text-white'
                                                : isActive
                                                    ? 'bg-primary text-white'
                                                    : 'bg-gray-200 dark:bg-gray-700 text-gray-400'
                                            }`}>
                                            {isCompleted ? (
                                                <motion.div
                                                    initial={{ scale: 0 }}
                                                    animate={{ scale: 1 }}
                                                    transition={{ type: 'spring', stiffness: 500 }}
                                                >
                                                    <Check className="w-5 h-5" />
                                                </motion.div>
                                            ) : isFailed ? (
                                                <X className="w-5 h-5" />
                                            ) : isActive ? (
                                                <motion.div
                                                    animate={{ rotate: 360 }}
                                                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                                                >
                                                    <Loader2 className="w-5 h-5" />
                                                </motion.div>
                                            ) : (
                                                <Icon className="w-5 h-5" />
                                            )}
                                        </div>
                                        <div className="flex flex-col">
                                            <span className={`font-medium transition-all ${isCompleted
                                                ? 'text-green-600 dark:text-green-400'
                                                : isFailed
                                                    ? 'text-red-600 dark:text-red-400'
                                                    : isActive
                                                        ? 'text-primary'
                                                        : 'text-muted-foreground'
                                                }`}>
                                                {step.label}
                                                {isCompleted && ' ✓'}
                                            </span>
                                            {isFailed && (
                                                <span className="text-[11px] text-red-500 dark:text-red-400 line-clamp-1">
                                                    {(error?.response?.data?.message ||
                                                        error?.response?.data?.error?.message ||
                                                        error?.response?.data?.detail ||
                                                        error?.message ||
                                                        'Processing failed')}
                                                </span>
                                            )}
                                        </div>
                                    </motion.div>
                                )
                            })}
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800"
                            >
                                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl mb-4 border border-red-100 dark:border-red-900/50">
                                    <p className="text-sm text-red-700 dark:text-red-400 font-medium mb-1">
                                        {isOcrError ? 'Image Quality Issue' : 'Analysis Interrupted'}
                                    </p>
                                    <p className="text-xs text-red-600/80 dark:text-red-400/80">
                                        {(error?.response?.data?.message ||
                                            error?.response?.data?.error?.message ||
                                            error?.response?.data?.detail ||
                                            error?.message)}
                                    </p>
                                </div>
                                <button
                                    onClick={onRetry}
                                    className="w-full py-3 rounded-xl bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 font-semibold hover:opacity-90 transition-all flex items-center justify-center gap-2"
                                >
                                    <X className="w-4 h-4" />
                                    Close and Retake Photo
                                </button>
                            </motion.div>
                        )}

                        <motion.div
                            className={`mt-6 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden ${error ? 'opacity-30' : ''}`}
                        >
                            <motion.div
                                className={`h-full ${error ? 'bg-red-500' : 'bg-gradient-to-r from-primary to-teal-400'}`}
                                initial={{ width: '0%' }}
                                animate={{
                                    width: error
                                        ? `${(currentStep / processingSteps.length) * 100}%`
                                        : `${((completedSteps.size) / processingSteps.length) * 100}%`
                                }}
                                transition={{ duration: 0.5 }}
                            />
                        </motion.div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

export default function Scan() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const categoryId = Number(searchParams.get('category')) || 1

    const [mode, setMode] = useState<'single' | 'dual'>('dual')

    // Single mode state
    const [file, setFile] = useState<File | null>(null)
    const [preview, setPreview] = useState<string | null>(null)

    // Dual mode state
    const [ingredientsFile, setIngredientsFile] = useState<File | null>(null)
    const [ingredientsPreview, setIngredientsPreview] = useState<string | null>(null)
    const [nutritionFile, setNutritionFile] = useState<File | null>(null)
    const [nutritionPreview, setNutritionPreview] = useState<string | null>(null)

    const [claimText, setClaimText] = useState('')
    const [productName, setProductName] = useState('')
    const [brand, setBrand] = useState('')

    const onDropSingle = useCallback((acceptedFiles: File[]) => {
        const selectedFile = acceptedFiles[0]
        if (selectedFile) {
            setFile(selectedFile)
            setPreview(URL.createObjectURL(selectedFile))
        }
    }, [])

    const onDropIngredients = useCallback((acceptedFiles: File[]) => {
        const selectedFile = acceptedFiles[0]
        if (selectedFile) {
            setIngredientsFile(selectedFile)
            setIngredientsPreview(URL.createObjectURL(selectedFile))
        }
    }, [])

    const onDropNutrition = useCallback((acceptedFiles: File[]) => {
        const selectedFile = acceptedFiles[0]
        if (selectedFile) {
            setNutritionFile(selectedFile)
            setNutritionPreview(URL.createObjectURL(selectedFile))
        }
    }, [])

    const singleDropzone = useDropzone({
        onDrop: onDropSingle,
        accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024,
    })

    const ingredientsDropzone = useDropzone({
        onDrop: onDropIngredients,
        accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024,
    })

    const nutritionDropzone = useDropzone({
        onDrop: onDropNutrition,
        accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
        maxFiles: 1,
        maxSize: 10 * 1024 * 1024,
    })

    const removeFile = (type: 'single' | 'ingredients' | 'nutrition') => {
        if (type === 'single') {
            setFile(null)
            if (preview) URL.revokeObjectURL(preview)
            setPreview(null)
        } else if (type === 'ingredients') {
            setIngredientsFile(null)
            if (ingredientsPreview) URL.revokeObjectURL(ingredientsPreview)
            setIngredientsPreview(null)
        } else if (type === 'nutrition') {
            setNutritionFile(null)
            if (nutritionPreview) URL.revokeObjectURL(nutritionPreview)
            setNutritionPreview(null)
        }
    }

    const scanMutation = useMutation({
        mutationFn: async () => {
            if (mode === 'single' && !file) throw new Error('No file selected')
            if (mode === 'dual' && (!ingredientsFile || !nutritionFile)) throw new Error('Both images are required for split accuracy')

            return scanApi.create({
                image: mode === 'single' ? file! : undefined,
                ingredients_image: mode === 'dual' ? ingredientsFile! : undefined,
                nutrition_image: mode === 'dual' ? nutritionFile! : undefined,
                category_id: categoryId,
                claim_text: claimText || undefined,
                product_name: productName || undefined,
                brand: brand || undefined,
            })
        },
        onSuccess: (response) => {
            const scanId = response.data.data.id
            toast.success('Scan complete!')
            navigate(`/app/results/${scanId}`)
        },
        onError: (error: any) => {
            const responseData = error.response?.data
            const message = responseData?.message || 'Failed to analyze image'
            const code = responseData?.error?.code

            if (code === 'OCR_QUALITY_LOW' || code === 'LOW_RESOLUTION') {
                toast.error('Scan Optimization Required', {
                    description: message,
                })
            } else {
                toast.error(message)
            }
        },
    })

    const handleSubmit = () => {
        if (mode === 'single' && !file) {
            toast.error('Please upload an image')
            return
        }
        if (mode === 'dual' && (!ingredientsFile || !nutritionFile)) {
            toast.error('Please upload both ingredients and nutrition labels')
            return
        }
        scanMutation.mutate()
    }

    const canSubmit = mode === 'single' ? !!file : (!!ingredientsFile && !!nutritionFile)

    return (
        <>
            <ProcessingOverlay
                isProcessing={scanMutation.isPending || !!scanMutation.error}
                error={scanMutation.error}
                onRetry={() => scanMutation.reset()}
            />

            <div className="max-w-3xl mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="mb-8"
                >
                    <button
                        onClick={() => navigate('/app')}
                        className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors mb-4"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back to categories
                    </button>
                    <h1 className="text-3xl font-bold mb-2">Scan Label</h1>
                    <p className="text-muted-foreground">
                        Upload high-quality photos for the best analytical accuracy
                    </p>
                </motion.div>

                {/* Mode Toggle */}
                <div className="flex p-1 bg-gray-100 dark:bg-gray-800 rounded-2xl mb-8 w-full sm:w-80">
                    <button
                        onClick={() => setMode('dual')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all ${mode === 'dual'
                            ? 'bg-white dark:bg-gray-700 shadow-sm text-primary'
                            : 'text-muted-foreground hover:text-foreground'
                            }`}
                    >
                        <Sparkles className="w-4 h-4" />
                        Precision Scan
                    </button>
                    <button
                        onClick={() => setMode('single')}
                        className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all ${mode === 'single'
                            ? 'bg-white dark:bg-gray-700 shadow-sm text-primary'
                            : 'text-muted-foreground hover:text-foreground'
                            }`}
                    >
                        <Camera className="w-4 h-4" />
                        Quick Scan
                    </button>
                </div>

                <div className="space-y-6">
                    {/* Upload Areas */}
                    <AnimatePresence mode="wait">
                        {mode === 'dual' ? (
                            <motion.div
                                key="dual-mode"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="grid grid-cols-1 sm:grid-cols-2 gap-4"
                            >
                                {/* Ingredients Upload */}
                                <UploadCard
                                    title="Ingredients List"
                                    description="Focus on the ingredients text"
                                    file={ingredientsFile}
                                    preview={ingredientsPreview}
                                    dropzone={ingredientsDropzone}
                                    onRemove={() => removeFile('ingredients')}
                                />

                                {/* Nutrition Upload */}
                                <UploadCard
                                    title="Nutrition Facts"
                                    description="Focus on the nutrient table"
                                    file={nutritionFile}
                                    preview={nutritionPreview}
                                    dropzone={nutritionDropzone}
                                    onRemove={() => removeFile('nutrition')}
                                />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="single-mode"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                            >
                                <UploadCard
                                    title="Full Label Image"
                                    description="One photo containing all info"
                                    file={file}
                                    preview={preview}
                                    dropzone={singleDropzone}
                                    onRemove={() => removeFile('single')}
                                    larger
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Optional fields */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="glass-card p-6 space-y-4"
                    >
                        <h3 className="font-semibold flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-primary" />
                            Optional Details
                        </h3>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Product Name</label>
                                <input
                                    type="text"
                                    value={productName}
                                    onChange={(e) => setProductName(e.target.value)}
                                    placeholder="e.g., Protein Bar"
                                    className="w-full px-4 py-2.5 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Brand</label>
                                <input
                                    type="text"
                                    value={brand}
                                    onChange={(e) => setBrand(e.target.value)}
                                    placeholder="e.g., NutriBar"
                                    className="w-full px-4 py-2.5 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Claims to Verify</label>
                            <textarea
                                value={claimText}
                                onChange={(e) => setClaimText(e.target.value)}
                                placeholder="e.g., high protein, no added sugar, low fat"
                                rows={2}
                                className="w-full px-4 py-2.5 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none resize-none"
                            />
                        </div>
                    </motion.div>

                    {/* Submit button */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <button
                            onClick={handleSubmit}
                            disabled={!canSubmit || scanMutation.isPending}
                            className="w-full py-4 px-6 rounded-xl bg-primary text-primary-foreground font-semibold text-lg hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 shadow-lg shadow-primary/25"
                        >
                            <Sparkles className="w-6 h-6" />
                            {scanMutation.isPending ? 'Processing...' : 'Analyze Label'}
                        </button>
                    </motion.div>
                </div>
            </div>
        </>
    )
}

interface UploadCardProps {
    title: string
    description: string
    file: File | null
    preview: string | null
    dropzone: any
    onRemove: () => void
    larger?: boolean
}

function UploadCard({ title, description, file, preview, dropzone, onRemove, larger }: UploadCardProps) {
    const { getRootProps, getInputProps, isDragActive } = dropzone

    return (
        <div className="relative h-full">
            <AnimatePresence mode="wait">
                {!file ? (
                    <motion.div
                        key="dropzone"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="h-full"
                    >
                        <div
                            {...getRootProps()}
                            className={`
                                relative h-full border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[220px]
                                ${isDragActive
                                    ? 'border-primary bg-primary/5'
                                    : 'border-gray-200 dark:border-gray-700 hover:border-primary/50 hover:bg-gray-50 dark:hover:bg-gray-800/50 shadow-sm'
                                }
                                ${larger ? 'py-12' : ''}
                            `}
                        >
                            <input {...getInputProps()} />

                            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                                {isDragActive ? (
                                    <Upload className="w-6 h-6 text-primary animate-bounce" />
                                ) : (
                                    <Camera className="w-6 h-6 text-primary" />
                                )}
                            </div>

                            <h3 className="font-semibold mb-1 text-base">
                                {isDragActive ? 'Drop it here!' : title}
                            </h3>
                            <p className="text-muted-foreground text-xs">
                                {description}
                            </p>
                            <p className="text-[10px] text-muted-foreground mt-2 opacity-60">
                                JPG, PNG, WebP • Max 10MB
                            </p>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="preview"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="relative rounded-2xl overflow-hidden bg-gray-100 dark:bg-gray-800 shadow-md h-full min-h-[220px]"
                    >
                        <img
                            src={preview!}
                            alt="Preview"
                            className="w-full h-full min-h-[220px] object-cover"
                        />
                        <button
                            onClick={(e) => {
                                e.stopPropagation()
                                onRemove()
                            }}
                            className="absolute top-2 right-2 w-7 h-7 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-colors z-10"
                        >
                            <X className="w-3 link-4" />
                        </button>
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                            <div className="flex items-center gap-2 text-white">
                                <ImageIcon className="w-3.5 h-3.5" />
                                <span className="text-[10px] truncate max-w-[120px]">{file.name}</span>
                                <span className="text-[10px] opacity-75">
                                    ({(file.size / 1024 / 1024).toFixed(1)}MB)
                                </span>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
