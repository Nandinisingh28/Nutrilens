import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Scan, History, User, LogOut, Leaf, Sun, Moon } from 'lucide-react';

function Layout() {
    const { user, logout } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const location = useLocation();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const isActive = (path) => {
        return location.pathname === path ? 'active' : '';
    };

    return (
        <>
            {/* Navigation Bar */}
            <nav className="navbar">
                <div className="container navbar-content">
                    <Link to="/" className="navbar-logo">
                        <div className="navbar-logo-icon">
                            <Leaf size={20} />
                        </div>
                        NutriLens
                    </Link>

                    <div className="navbar-nav">
                        <Link to="/dashboard" className={`navbar-link ${isActive('/dashboard')}`}>
                            <Scan size={18} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                            Scan
                        </Link>
                        <Link to="/history" className={`navbar-link ${isActive('/history')}`}>
                            <History size={18} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                            History
                        </Link>
                        <Link to="/profile" className={`navbar-link ${isActive('/profile')}`}>
                            <User size={18} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                            Profile
                        </Link>

                        {/* Theme Toggle */}
                        <button
                            onClick={toggleTheme}
                            className="btn btn-ghost theme-toggle"
                            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                            style={{ padding: 'var(--spacing-2)' }}
                        >
                            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        </button>

                        <button onClick={handleLogout} className="btn btn-ghost">
                            <LogOut size={18} />
                            Logout
                        </button>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className="page">
                <div className="container">
                    <Outlet />
                </div>
            </main>

            {/* Footer */}
            <footer style={{
                textAlign: 'center',
                padding: 'var(--spacing-6)',
                borderTop: '1px solid var(--color-neutral-800)',
                color: 'var(--color-neutral-500)',
                fontSize: 'var(--font-size-sm)'
            }}>
                <p>NutriLens © 2024 - Verify food claims with confidence</p>
                <p style={{ marginTop: '4px', fontSize: 'var(--font-size-xs)' }}>
                    Based on FSSAI Guidelines for Indian Food Products
                </p>
            </footer>
        </>
    );
}

export default Layout;
