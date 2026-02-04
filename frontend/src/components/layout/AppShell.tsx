import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Navbar } from './Navbar'
import { Footer } from './Footer'

export function AppShell() {
    return (
        <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 to-gray-100">
            <Navbar />
            <motion.main
                className="flex-1 container py-8"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
            >
                <Outlet />
            </motion.main>
            <Footer />
        </div>
    )
}
