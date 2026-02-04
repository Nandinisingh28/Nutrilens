import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, Image, X, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileDropzoneProps {
    onFileSelect: (file: File) => void
    isLoading?: boolean
    accept?: Record<string, string[]>
    maxSize?: number
}

export function FileDropzone({
    onFileSelect,
    isLoading = false,
    accept = { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxSize = 10 * 1024 * 1024, // 10MB
}: FileDropzoneProps) {
    const [preview, setPreview] = useState<string | null>(null)
    const [error, setError] = useState<string | null>(null)

    const onDrop = useCallback(
        (acceptedFiles: File[], rejectedFiles: any[]) => {
            setError(null)

            if (rejectedFiles.length > 0) {
                const error = rejectedFiles[0].errors[0]
                if (error.code === 'file-too-large') {
                    setError('File is too large. Maximum size is 10MB.')
                } else if (error.code === 'file-invalid-type') {
                    setError('Invalid file type. Please upload an image.')
                } else {
                    setError('Failed to upload file.')
                }
                return
            }

            if (acceptedFiles.length > 0) {
                const file = acceptedFiles[0]
                const previewUrl = URL.createObjectURL(file)
                setPreview(previewUrl)
                onFileSelect(file)
            }
        },
        [onFileSelect]
    )

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept,
        maxSize,
        multiple: false,
        disabled: isLoading,
    })

    const clearPreview = () => {
        if (preview) {
            URL.revokeObjectURL(preview)
        }
        setPreview(null)
        setError(null)
    }

    return (
        <div className="w-full">
            <AnimatePresence mode="wait">
                {preview ? (
                    <motion.div
                        key="preview"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="relative rounded-xl overflow-hidden border-2 border-primary/20"
                    >
                        <img
                            src={preview}
                            alt="Preview"
                            className="w-full h-64 object-cover"
                        />
                        {!isLoading && (
                            <button
                                onClick={clearPreview}
                                className="absolute top-3 right-3 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        )}
                        {isLoading && (
                            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                                <Loader2 className="w-8 h-8 text-white animate-spin" />
                            </div>
                        )}
                    </motion.div>
                ) : (
                    <motion.div
                        key="dropzone"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    >
                        <div
                            {...getRootProps()}
                            className={cn(
                                'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200',
                                isDragActive
                                    ? 'border-primary bg-primary/5'
                                    : 'border-gray-300 hover:border-primary/50 hover:bg-gray-50',
                                isLoading && 'opacity-50 cursor-not-allowed'
                            )}
                        >
                            <input {...getInputProps()} />
                            <div className="flex flex-col items-center space-y-4">
                                <div className={cn(
                                    'w-16 h-16 rounded-2xl flex items-center justify-center transition-colors',
                                    isDragActive ? 'bg-primary/10' : 'bg-gray-100'
                                )}>
                                    {isDragActive ? (
                                        <Image className="w-8 h-8 text-primary" />
                                    ) : (
                                        <Upload className="w-8 h-8 text-gray-400" />
                                    )}
                                </div>
                                <div>
                                    <p className="font-medium text-foreground">
                                        {isDragActive ? 'Drop your image here' : 'Drag & drop your nutrition label'}
                                    </p>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        or click to browse (JPG, PNG, WebP up to 10MB)
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {error && (
                <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-sm text-red-500 mt-2"
                >
                    {error}
                </motion.p>
            )}
        </div>
    )
}
