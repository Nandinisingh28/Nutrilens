import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { format } from 'date-fns'
import {
    Search,
    Filter,
    Trash2,
    ChevronRight,
    Loader2,
    CheckCircle,
    AlertTriangle,
    XCircle,
    HelpCircle,
    History as HistoryIcon,
} from 'lucide-react'
import { scanApi, Scan } from '@/app/api'

const verdictConfig = {
    true: { label: 'Verified', color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-900/20', icon: CheckCircle },
    misleading: { label: 'Misleading', color: 'text-amber-600', bg: 'bg-amber-50 dark:bg-amber-900/20', icon: AlertTriangle },
    false: { label: 'False', color: 'text-red-600', bg: 'bg-red-50 dark:bg-red-900/20', icon: XCircle },
    mixed: { label: 'Mixed', color: 'text-orange-600', bg: 'bg-orange-50 dark:bg-orange-900/20', icon: AlertTriangle },
    unknown: { label: 'Unknown', color: 'text-gray-600', bg: 'bg-gray-50 dark:bg-gray-800', icon: HelpCircle },
}

export default function History() {
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const [search, setSearch] = useState('')
    const [verdictFilter, setVerdictFilter] = useState<string | null>(null)
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
    const [page, setPage] = useState(1)

    const { data, isLoading } = useQuery({
        queryKey: ['scans', page, verdictFilter],
        queryFn: async () => {
            const response = await scanApi.getAll({
                page,
                per_page: 20,
                verdict: verdictFilter || undefined,
            })
            return response.data
        },
    })

    const deleteMutation = useMutation({
        mutationFn: (ids: number[]) => scanApi.bulkDelete(ids),
        onSuccess: () => {
            toast.success('Scans deleted')
            setSelectedIds(new Set())
            queryClient.invalidateQueries({ queryKey: ['scans'] })
        },
        onError: () => {
            toast.error('Failed to delete scans')
        },
    })

    const singleDeleteMutation = useMutation({
        mutationFn: (id: number) => scanApi.delete(id),
        onSuccess: () => {
            toast.success('Scan deleted')
            queryClient.invalidateQueries({ queryKey: ['scans'] })
        },
        onError: () => {
            toast.error('Failed to delete scan')
        },
    })

    const handleSingleDelete = (id: number, e: React.MouseEvent) => {
        e.stopPropagation()
        if (confirm('Delete this scan?')) {
            singleDeleteMutation.mutate(id)
        }
    }

    const scans = data?.data || []
    const meta = data?.meta

    const filteredScans = search
        ? scans.filter(
            (s) =>
                s.product_name?.toLowerCase().includes(search.toLowerCase()) ||
                s.brand?.toLowerCase().includes(search.toLowerCase())
        )
        : scans

    const toggleSelect = (id: number) => {
        const newSelected = new Set(selectedIds)
        if (newSelected.has(id)) {
            newSelected.delete(id)
        } else {
            newSelected.add(id)
        }
        setSelectedIds(newSelected)
    }

    const handleDelete = () => {
        if (selectedIds.size === 0) return
        if (confirm(`Delete ${selectedIds.size} scan(s)?`)) {
            deleteMutation.mutate(Array.from(selectedIds))
        }
    }

    return (
        <div className="max-w-4xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
            >
                <h1 className="text-3xl font-bold mb-2">Scan History</h1>
                <p className="text-muted-foreground">
                    View and manage your previous scans
                </p>
            </motion.div>

            {/* Filters */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="glass-card p-4 mb-6"
            >
                <div className="flex flex-col sm:flex-row gap-4">
                    {/* Search */}
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Search by product or brand..."
                            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                        />
                    </div>

                    {/* Verdict filter */}
                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4 text-muted-foreground" />
                        <select
                            value={verdictFilter || ''}
                            onChange={(e) => setVerdictFilter(e.target.value || null)}
                            className="px-3 py-2.5 rounded-xl border border-input bg-background focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all outline-none"
                        >
                            <option value="">All verdicts</option>
                            <option value="true">Verified</option>
                            <option value="misleading">Misleading</option>
                            <option value="false">False</option>
                            <option value="unknown">Unknown</option>
                        </select>
                    </div>
                </div>

                {/* Selection actions */}
                <AnimatePresence>
                    {selectedIds.size > 0 && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="flex items-center justify-between mt-4 pt-4 border-t"
                        >
                            <span className="text-sm text-muted-foreground">
                                {selectedIds.size} selected
                            </span>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setSelectedIds(new Set())}
                                    className="text-sm text-muted-foreground hover:text-foreground"
                                >
                                    Clear
                                </button>
                                <button
                                    onClick={handleDelete}
                                    disabled={deleteMutation.isPending}
                                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-destructive/10 text-destructive hover:bg-destructive/20 transition-colors"
                                >
                                    {deleteMutation.isPending ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <Trash2 className="w-4 h-4" />
                                    )}
                                    Delete
                                </button>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>

            {/* Scans list */}
            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
                    <p className="text-muted-foreground">Loading scans...</p>
                </div>
            ) : filteredScans.length > 0 ? (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="space-y-3"
                >
                    {filteredScans.map((scan, index) => (
                        <ScanCard
                            key={scan.id}
                            scan={scan}
                            index={index}
                            isSelected={selectedIds.has(scan.id)}
                            onSelect={() => toggleSelect(scan.id)}
                            onClick={() => navigate(`/app/results/${scan.id}`)}
                            onDelete={(e) => handleSingleDelete(scan.id, e)}
                            isDeleting={singleDeleteMutation.isPending}
                        />
                    ))}

                    {/* Pagination */}
                    {meta && meta.total_pages > 1 && (
                        <div className="flex justify-center gap-2 mt-6">
                            <button
                                onClick={() => setPage((p) => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="px-4 py-2 rounded-lg border disabled:opacity-50"
                            >
                                Previous
                            </button>
                            <span className="px-4 py-2">
                                Page {page} of {meta.total_pages}
                            </span>
                            <button
                                onClick={() => setPage((p) => Math.min(meta.total_pages, p + 1))}
                                disabled={page === meta.total_pages}
                                className="px-4 py-2 rounded-lg border disabled:opacity-50"
                            >
                                Next
                            </button>
                        </div>
                    )}
                </motion.div>
            ) : (
                <EmptyState />
            )}
        </div>
    )
}

function ScanCard({
    scan,
    index,
    isSelected,
    onSelect,
    onClick,
    onDelete,
    isDeleting,
}: {
    scan: Scan
    index: number
    isSelected: boolean
    onSelect: () => void
    onClick: () => void
    onDelete: (e: React.MouseEvent) => void
    isDeleting: boolean
}) {
    const verdict = scan.overall_verdict || 'unknown'
    const config = verdictConfig[verdict]
    const Icon = config.icon

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className={`glass-card p-4 flex items-center gap-4 cursor-pointer hover:shadow-md transition-all ${isSelected ? 'ring-2 ring-primary' : ''
                }`}
        >
            {/* Checkbox */}
            <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                    e.stopPropagation()
                    onSelect()
                }}
                className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />

            {/* Verdict icon */}
            <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center ${config.color} flex-shrink-0`}>
                <Icon className="w-5 h-5" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0" onClick={onClick}>
                <h3 className="font-medium truncate">
                    {scan.product_name || 'Untitled Scan'}
                </h3>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    {scan.brand && <span>{scan.brand}</span>}
                    <span>{format(new Date(scan.created_at), 'MMM d, yyyy')}</span>
                </div>
            </div>

            {/* Verdict badge */}
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
                {config.label}
            </span>

            {/* Delete button */}
            <button
                onClick={onDelete}
                disabled={isDeleting}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors disabled:opacity-50"
                title="Delete scan"
            >
                {isDeleting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                    <Trash2 className="w-4 h-4" />
                )}
            </button>

            {/* Arrow */}
            <ChevronRight className="w-5 h-5 text-muted-foreground" onClick={onClick} />
        </motion.div>
    )
}

function EmptyState() {
    const navigate = useNavigate()

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20"
        >
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <HistoryIcon className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No scans yet</h3>
            <p className="text-muted-foreground mb-6">
                Start scanning product labels to see them here
            </p>
            <button
                onClick={() => navigate('/app')}
                className="px-6 py-2.5 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all"
            >
                Start Scanning
            </button>
        </motion.div>
    )
}
