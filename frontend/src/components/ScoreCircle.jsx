function ScoreCircle({ score, size = 120, color, label = "Score" }) {
    const radius = (size - 16) / 2;
    const circumference = 2 * Math.PI * radius;
    const progress = ((100 - (score || 0)) / 100) * circumference;

    const getColor = (s) => {
        if (color) return color;
        if (s >= 70) return 'var(--color-true)';
        if (s >= 50) return 'var(--color-partially-true)';
        if (s >= 30) return 'var(--color-misleading)';
        return 'var(--color-false)';
    };

    return (
        <div className="score-circle" style={{ width: size, height: size }}>
            <svg className="score-circle-ring" viewBox={`0 0 ${size} ${size}`}>
                <circle
                    className="score-circle-track"
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                />
                <circle
                    className="score-circle-progress"
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    style={{
                        stroke: getColor(score),
                        strokeDasharray: circumference,
                        strokeDashoffset: progress,
                    }}
                />
            </svg>
            <span className="score-circle-value" style={{ color: getColor(score) }}>
                {Math.round(score || 0)}
            </span>
            <span className="score-circle-label">{label}</span>
        </div>
    );
}

export default ScoreCircle;
