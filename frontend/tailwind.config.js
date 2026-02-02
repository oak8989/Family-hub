/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: ["class"],
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
        "./public/index.html"
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['DM Sans', 'sans-serif'],
                heading: ['Nunito', 'sans-serif'],
                handwritten: ['Caveat', 'cursive'],
            },
            colors: {
                terracotta: {
                    DEFAULT: '#E07A5F',
                    hover: '#D0694E',
                    light: '#E89B85',
                },
                sage: {
                    DEFAULT: '#81B29A',
                    hover: '#6FA388',
                    light: '#A8D0BC',
                },
                cream: '#F4F1DE',
                'warm-white': '#FEFAE0',
                navy: {
                    DEFAULT: '#3D405B',
                    light: '#6D6875',
                },
                sunny: {
                    DEFAULT: '#F2CC8F',
                    hover: '#E5BE7E',
                },
                background: 'hsl(var(--background))',
                foreground: 'hsl(var(--foreground))',
                card: {
                    DEFAULT: 'hsl(var(--card))',
                    foreground: 'hsl(var(--card-foreground))'
                },
                popover: {
                    DEFAULT: 'hsl(var(--popover))',
                    foreground: 'hsl(var(--popover-foreground))'
                },
                primary: {
                    DEFAULT: 'hsl(var(--primary))',
                    foreground: 'hsl(var(--primary-foreground))'
                },
                secondary: {
                    DEFAULT: 'hsl(var(--secondary))',
                    foreground: 'hsl(var(--secondary-foreground))'
                },
                muted: {
                    DEFAULT: 'hsl(var(--muted))',
                    foreground: 'hsl(var(--muted-foreground))'
                },
                accent: {
                    DEFAULT: 'hsl(var(--accent))',
                    foreground: 'hsl(var(--accent-foreground))'
                },
                destructive: {
                    DEFAULT: 'hsl(var(--destructive))',
                    foreground: 'hsl(var(--destructive-foreground))'
                },
                border: 'hsl(var(--border))',
                input: 'hsl(var(--input))',
                ring: 'hsl(var(--ring))',
            },
            borderRadius: {
                lg: 'var(--radius)',
                md: 'calc(var(--radius) - 2px)',
                sm: 'calc(var(--radius) - 4px)',
                '2xl': '1rem',
                '3xl': '1.5rem',
            },
            boxShadow: {
                'warm': '0 10px 40px -10px rgba(224, 122, 95, 0.3)',
                'card': '0 4px 20px -5px rgba(61, 64, 91, 0.08)',
                'card-hover': '0 12px 40px -10px rgba(224, 122, 95, 0.25)',
            },
            keyframes: {
                'accordion-down': {
                    from: { height: '0' },
                    to: { height: 'var(--radix-accordion-content-height)' }
                },
                'accordion-up': {
                    from: { height: 'var(--radix-accordion-content-height)' },
                    to: { height: '0' }
                },
                'fade-in-up': {
                    '0%': { opacity: '0', transform: 'translateY(20px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' }
                },
                'bounce-soft': {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-5px)' }
                }
            },
            animation: {
                'accordion-down': 'accordion-down 0.2s ease-out',
                'accordion-up': 'accordion-up 0.2s ease-out',
                'fade-in-up': 'fade-in-up 0.5s ease-out forwards',
                'bounce-soft': 'bounce-soft 2s ease-in-out infinite'
            }
        }
    },
    plugins: [require("tailwindcss-animate")],
};
