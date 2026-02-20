import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    // Initialize auth state from localStorage
    useEffect(() => {
        const storedToken = localStorage.getItem('nutrilens_token');
        const storedUser = localStorage.getItem('nutrilens_user');

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    // Signup function
    const signup = async (email, password, name) => {
        try {
            const response = await authAPI.signup({ email, password, name });
            const { access_token, user: userData } = response.data;

            // Store in localStorage
            localStorage.setItem('nutrilens_token', access_token);
            localStorage.setItem('nutrilens_user', JSON.stringify(userData));

            // Update state
            setToken(access_token);
            setUser(userData);

            return { success: true };
        } catch (error) {
            const message = error.response?.data?.detail || 'Signup failed';
            return { success: false, error: message };
        }
    };

    // Login function
    const login = async (email, password) => {
        try {
            const response = await authAPI.login({ email, password });
            const { access_token, user: userData } = response.data;

            // Store in localStorage
            localStorage.setItem('nutrilens_token', access_token);
            localStorage.setItem('nutrilens_user', JSON.stringify(userData));

            // Update state
            setToken(access_token);
            setUser(userData);

            return { success: true };
        } catch (error) {
            const message = error.response?.data?.detail || 'Login failed';
            return { success: false, error: message };
        }
    };

    // Logout function
    const logout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            // Ignore logout errors
        }

        // Clear storage
        localStorage.removeItem('nutrilens_token');
        localStorage.removeItem('nutrilens_user');

        // Update state
        setToken(null);
        setUser(null);
    };

    // Update user data
    const updateUser = (userData) => {
        setUser(userData);
        localStorage.setItem('nutrilens_user', JSON.stringify(userData));
    };

    // Refresh user data from server
    const refreshUser = async () => {
        try {
            const response = await authAPI.me();
            updateUser(response.data);
            return response.data;
        } catch (error) {
            // If refresh fails, logout
            await logout();
            throw error;
        }
    };

    const value = {
        user,
        token,
        loading,
        isAuthenticated: !!token,
        signup,
        login,
        logout,
        updateUser,
        refreshUser,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;
