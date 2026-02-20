import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, Save } from 'lucide-react';
import { usersAPI } from '../api/client';

function EditProfile() {
    const { user, updateUser } = useAuth();
    const navigate = useNavigate();

    const [name, setName] = useState(user?.name || '');
    const [email, setEmail] = useState(user?.email || '');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Validate
        if (!name.trim()) {
            setError('Name is required');
            return;
        }
        if (!email.trim()) {
            setError('Email is required');
            return;
        }

        // Check if anything changed
        if (name === user?.name && email === user?.email) {
            setError('No changes to save');
            return;
        }

        setLoading(true);

        try {
            const updateData = {};
            if (name !== user?.name) updateData.name = name;
            if (email !== user?.email) updateData.email = email;

            const response = await usersAPI.updateProfile(updateData);

            // Update local user data
            updateUser(response.data);

            setSuccess('Profile updated successfully!');

            // Navigate back after short delay
            setTimeout(() => {
                navigate('/profile');
            }, 1500);
        } catch (err) {
            const message = err.response?.data?.detail || 'Failed to update profile';
            setError(message);
        }

        setLoading(false);
    };

    return (
        <div className="animate-fadeIn">
            <button
                className="btn btn-ghost"
                onClick={() => navigate('/profile')}
                style={{ marginBottom: 'var(--spacing-6)' }}
            >
                <ArrowLeft size={18} />
                Back to Profile
            </button>

            <div className="card" style={{ maxWidth: '500px', margin: '0 auto' }}>
                <h1 style={{
                    fontSize: 'var(--font-size-2xl)',
                    marginBottom: 'var(--spacing-6)',
                    textAlign: 'center'
                }}>
                    Edit Profile
                </h1>

                {error && (
                    <div className="alert alert-error" style={{ marginBottom: 'var(--spacing-6)' }}>
                        {error}
                    </div>
                )}

                {success && (
                    <div className="alert alert-success" style={{ marginBottom: 'var(--spacing-6)' }}>
                        {success}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="name">Full Name</label>
                        <input
                            id="name"
                            type="text"
                            className="form-input"
                            placeholder="Your name"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            className="form-input"
                            placeholder="you@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                        <p style={{
                            fontSize: 'var(--font-size-xs)',
                            color: 'var(--color-neutral-500)',
                            marginTop: 'var(--spacing-2)'
                        }}>
                            Changing your email will update your login credentials
                        </p>
                    </div>

                    <div style={{ display: 'flex', gap: 'var(--spacing-4)', marginTop: 'var(--spacing-8)' }}>
                        <button
                            type="button"
                            className="btn btn-secondary"
                            onClick={() => navigate('/profile')}
                            style={{ flex: 1 }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={loading}
                            style={{ flex: 1 }}
                        >
                            {loading ? (
                                <>
                                    <div className="spinner"></div>
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save size={18} />
                                    Save Changes
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default EditProfile;
