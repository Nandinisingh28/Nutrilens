import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import About from './pages/About';
import Welcome from './pages/Welcome';
import Dashboard from './pages/Dashboard';
import PrecisionScan from './pages/PrecisionScan';
import QuickScan from './pages/QuickScan';
import Results from './pages/Results';
import History from './pages/History';
import Profile from './pages/Profile';
import EditProfile from './pages/EditProfile';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import DashboardLayout from './components/DashboardLayout';
import ProtectedRoute from './components/ProtectedRoute';

// Public layout: Navbar + Footer wrapping child routes
const PublicLayout = () => (
    <div className="min-h-screen bg-black font-sans text-white">
        <Navbar />
        <main>
            <Outlet />
        </main>
        <Footer />
    </div>
);

function App() {
    return (
        <Router>
            <Routes>
                {/* Welcome — standalone, no chrome */}
                <Route path="/welcome" element={<Welcome />} />

                {/* Protected routes — require auth, wrapped in DashboardLayout */}
                <Route element={<ProtectedRoute />}>
                    <Route element={<DashboardLayout />}>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/scan/precision" element={<PrecisionScan />} />
                        <Route path="/scan/quick" element={<QuickScan />} />
                        <Route path="/results/:id" element={<Results />} />
                        <Route path="/history" element={<History />} />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="/profile/edit" element={<EditProfile />} />
                    </Route>
                </Route>

                {/* Public routes — Navbar + Footer */}
                <Route element={<PublicLayout />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/forgot-password" element={<ForgotPassword />} />
                    <Route path="/reset-password" element={<ResetPassword />} />
                </Route>
            </Routes>
        </Router>
    );
}

export default App;
