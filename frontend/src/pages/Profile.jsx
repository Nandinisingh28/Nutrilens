import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Edit, History, Target, LogOut } from 'lucide-react';

function Profile() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const getInitials = (name) => {
        if (!name) return '?';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    };

    return (
        <div className="animate-fadeIn">
            <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
                {/* Profile Header */}
                <div className="profile-header">
                    <div className="profile-avatar">
                        {getInitials(user?.name)}
                    </div>
                    <div className="profile-info">
                        <h2>{user?.name || 'User'}</h2>
                        <p>{user?.email || 'No email'}</p>
                    </div>
                </div>

                {/* Profile Details */}
                <div style={{ marginBottom: 'var(--spacing-8)' }}>
                    <h3 style={{
                        fontSize: 'var(--font-size-lg)',
                        marginBottom: 'var(--spacing-4)',
                        color: 'var(--color-neutral-300)'
                    }}>
                        Account Details
                    </h3>

                    <div style={{
                        display: 'grid',
                        gap: 'var(--spacing-4)'
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: 'var(--spacing-4)',
                            background: 'var(--color-neutral-800)',
                            borderRadius: 'var(--radius-lg)'
                        }}>
                            <span style={{ color: 'var(--color-neutral-400)' }}>Full Name</span>
                            <span style={{ fontWeight: '500' }}>{user?.name}</span>
                        </div>

                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: 'var(--spacing-4)',
                            background: 'var(--color-neutral-800)',
                            borderRadius: 'var(--radius-lg)'
                        }}>
                            <span style={{ color: 'var(--color-neutral-400)' }}>Email</span>
                            <span style={{ fontWeight: '500' }}>{user?.email}</span>
                        </div>

                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: 'var(--spacing-4)',
                            background: 'var(--color-neutral-800)',
                            borderRadius: 'var(--radius-lg)'
                        }}>
                            <span style={{ color: 'var(--color-neutral-400)' }}>Member since</span>
                            <span style={{ fontWeight: '500' }}>{formatDate(user?.created_at)}</span>
                        </div>
                    </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-3)' }}>
                    <button
                        className="btn btn-primary w-full"
                        onClick={() => navigate('/profile/edit')}
                    >
                        <Edit size={18} />
                        Edit Profile
                    </button>

                    <button
                        className="btn btn-secondary w-full"
                        onClick={() => navigate('/history')}
                    >
                        <History size={18} />
                        View Scan History
                    </button>

                    <button
                        className="btn btn-secondary w-full"
                        onClick={() => navigate('/dashboard')}
                    >
                        <Target size={18} />
                        New Scan
                    </button>

                    <button
                        className="btn btn-ghost w-full"
                        onClick={handleLogout}
                        style={{ color: 'var(--color-false)' }}
                    >
                        <LogOut size={18} />
                        Logout
                    </button>
                </div>
            </div>
        </div >
    );
}

export default Profile;
