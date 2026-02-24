/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                nutri: {
                    mint: {
                        light: '#CFF5D2', // Very light mint
                        DEFAULT: '#A7EFC1', // Primary mint
                    },
                    red: '#EF4444', // Accent red
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'], // Assuming Inter or similar desirable
            }
        },
    },
    plugins: [],
}
