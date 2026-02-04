// Theme configuration and utilities

export const theme = {
    colors: {
        primary: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e',
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
        },
        healthy: '#22c55e',
        moderate: '#eab308',
        unhealthy: '#ef4444',
    },

    // Verdict colors
    verdictColors: {
        healthy: {
            bg: 'bg-green-100',
            text: 'text-green-700',
            border: 'border-green-200',
        },
        moderate: {
            bg: 'bg-yellow-100',
            text: 'text-yellow-700',
            border: 'border-yellow-200',
        },
        unhealthy: {
            bg: 'bg-red-100',
            text: 'text-red-700',
            border: 'border-red-200',
        },
        unknown: {
            bg: 'bg-gray-100',
            text: 'text-gray-700',
            border: 'border-gray-200',
        },
    },
} as const

export type Verdict = keyof typeof theme.verdictColors

export function getVerdictStyles(verdict: string) {
    return theme.verdictColors[verdict as Verdict] || theme.verdictColors.unknown
}

export function getHealthScore(score: number | null): {
    label: string
    color: string
} {
    if (score === null) {
        return { label: 'Unknown', color: 'gray' }
    }
    if (score >= 70) {
        return { label: 'Good', color: 'green' }
    }
    if (score >= 40) {
        return { label: 'Moderate', color: 'yellow' }
    }
    return { label: 'Poor', color: 'red' }
}
