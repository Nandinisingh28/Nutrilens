import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

export function LoadingScreen() {
    return (
        <div className="fixed inset-0 bg-background flex items-center justify-center z-50">
            <motion.div
                className="flex flex-col items-center space-y-4"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
            >
                <div className="relative">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-teal-500 flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-white animate-spin" />
                    </div>
                    <motion.div
                        className="absolute inset-0 rounded-2xl bg-primary/20"
                        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                    />
                </div>
                <p className="text-muted-foreground font-medium">Loading...</p>
            </motion.div>
        </div>
    )
}
