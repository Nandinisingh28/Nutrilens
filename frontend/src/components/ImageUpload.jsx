import { useState, useRef } from 'react';
import { Upload, Image, X } from 'lucide-react';

function ImageUpload({ label, hint, onFileSelect, accept = "image/*" }) {
    const [preview, setPreview] = useState(null);
    const [fileName, setFileName] = useState('');
    const [dragOver, setDragOver] = useState(false);
    const inputRef = useRef(null);

    const handleFileChange = (file) => {
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }

            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreview(reader.result);
            };
            reader.readAsDataURL(file);

            setFileName(file.name);
            onFileSelect(file);
        }
    };

    const handleInputChange = (e) => {
        const file = e.target.files?.[0];
        handleFileChange(file);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files?.[0];
        handleFileChange(file);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragOver(true);
    };

    const handleDragLeave = () => {
        setDragOver(false);
    };

    const clearFile = () => {
        setPreview(null);
        setFileName('');
        onFileSelect(null);
        if (inputRef.current) {
            inputRef.current.value = '';
        }
    };

    if (preview) {
        return (
            <div className="file-upload" style={{ padding: 'var(--spacing-4)' }}>
                <div style={{ position: 'relative' }}>
                    <img
                        src={preview}
                        alt="Preview"
                        style={{
                            width: '100%',
                            maxHeight: '200px',
                            objectFit: 'contain',
                            borderRadius: 'var(--radius-lg)'
                        }}
                    />
                    <button
                        type="button"
                        onClick={clearFile}
                        style={{
                            position: 'absolute',
                            top: '-8px',
                            right: '-8px',
                            background: 'var(--color-false)',
                            border: 'none',
                            borderRadius: '50%',
                            width: '28px',
                            height: '28px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            cursor: 'pointer',
                            color: 'white'
                        }}
                    >
                        <X size={16} />
                    </button>
                </div>
                <p className="file-upload-text" style={{ marginTop: 'var(--spacing-2)' }}>
                    {fileName}
                </p>
            </div>
        );
    }

    return (
        <div
            className={`file-upload ${dragOver ? 'dragover' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
        >
            <input
                ref={inputRef}
                type="file"
                accept={accept}
                onChange={handleInputChange}
            />
            <div className="file-upload-icon">
                <Upload size={48} />
            </div>
            <p className="file-upload-text">{label}</p>
            <p className="file-upload-hint">{hint}</p>
        </div>
    );
}

export default ImageUpload;
