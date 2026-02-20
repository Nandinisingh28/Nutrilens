function NutritionCard({ label, value, unit }) {
    if (value === null || value === undefined) {
        return null;
    }

    return (
        <div className="nutrition-card">
            <div className="nutrition-card-value">
                {typeof value === 'number' ? value.toFixed(1) : value}
                <span className="nutrition-card-unit">{unit}</span>
            </div>
            <div className="nutrition-card-label">{label}</div>
        </div>
    );
}

export default NutritionCard;
