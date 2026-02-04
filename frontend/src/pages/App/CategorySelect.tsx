import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Loader2, ChevronRight } from 'lucide-react'
import { categoryApi, Category } from '@/app/api'

// Get emoji and colors for category
function getCategoryDisplay(slug: string): { emoji: string; bg: string; border: string } {
    switch (slug) {
        case 'protein-bars':
            return { emoji: '💪', bg: 'bg-orange-500', border: 'border-orange-300' }
        case 'breakfast-cereals':
            return { emoji: '🥣', bg: 'bg-amber-500', border: 'border-amber-300' }
        case 'dairy':
            return { emoji: '🥛', bg: 'bg-blue-500', border: 'border-blue-300' }
        case 'snacks':
            return { emoji: '🍎', bg: 'bg-pink-500', border: 'border-pink-300' }
        case 'beverages':
            return { emoji: '☕', bg: 'bg-purple-500', border: 'border-purple-300' }
        case 'supplements':
            return { emoji: '💊', bg: 'bg-emerald-500', border: 'border-emerald-300' }
        default:
            return { emoji: '🌿', bg: 'bg-teal-500', border: 'border-teal-300' }
    }
}

export default function CategorySelect() {
    const navigate = useNavigate()

    const { data, isLoading, error } = useQuery({
        queryKey: ['categories'],
        queryFn: async () => {
            const response = await categoryApi.getAll()
            return response.data.data
        },
    })

    const handleSelectCategory = (category: Category) => {
        navigate(`/app/scan?category=${category.id}`)
    }

    return (
        <div className="max-w-4xl mx-auto px-4">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-10"
            >
                <h1 className="text-3xl font-bold mb-3">What are you scanning?</h1>
                <p className="text-muted-foreground text-lg">
                    Choose a product category to get started
                </p>
            </motion.div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
                    <p className="text-muted-foreground">Loading categories...</p>
                </div>
            ) : error ? (
                <div className="text-center py-20">
                    <p className="text-destructive mb-4">Failed to load categories</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 rounded-lg bg-primary text-primary-foreground"
                    >
                        Try Again
                    </button>
                </div>
            ) : data && data.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                    {data.map((category, index) => {
                        const display = getCategoryDisplay(category.slug)

                        return (
                            <motion.button
                                key={category.id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                onClick={() => handleSelectCategory(category)}
                                className="group relative overflow-hidden rounded-2xl bg-white dark:bg-slate-800 shadow-lg hover:shadow-xl border border-gray-200 dark:border-slate-700 p-6 text-left transition-all duration-300 hover:-translate-y-1"
                            >
                                {/* Colored accent bar at top */}
                                <div className={`absolute top-0 left-0 right-0 h-1.5 ${display.bg}`} />

                                {/* Emoji icon in colored circle */}
                                <div
                                    className={`w-14 h-14 rounded-full ${display.bg} flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}
                                >
                                    <span className="text-2xl" role="img" aria-hidden="true">
                                        {display.emoji}
                                    </span>
                                </div>

                                {/* Content */}
                                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                                    {category.title}
                                </h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm line-clamp-2 pr-8">
                                    {category.description || 'Scan and verify nutrition claims'}
                                </p>

                                {/* Arrow indicator */}
                                <div className="absolute bottom-6 right-6 w-8 h-8 rounded-full bg-gray-100 dark:bg-slate-700 flex items-center justify-center group-hover:bg-primary transition-colors duration-300">
                                    <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-white transition-colors" />
                                </div>
                            </motion.button>
                        )
                    })}
                </div>
            ) : (
                <EmptyState />
            )}
        </div>
    )
}

function EmptyState() {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
        >
            <div className="w-20 h-20 bg-gray-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">🌿</span>
            </div>
            <h3 className="text-lg font-semibold mb-2">No categories yet</h3>
            <p className="text-muted-foreground">
                Categories will appear here once they're added.
            </p>
        </motion.div>
    )
}
