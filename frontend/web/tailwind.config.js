/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6B2B1F',         // Nâu đỏ trầm — header, nút CTA chính
        accent: '#C9962C',          // Vàng đồng — icon, viền nhấn, badge
        background: '#F5EDE0',      // Kem — nền toàn app
        surface: '#FFFFFF',         // Trắng — nền card
        'surface-border': '#DCC9A8',// Viền card thanh nhã (đậm nhẹ ~8%)
        'text-primary': '#2E1B10',  // Nâu đen mực tàu (đậm nhẹ ~10% cho chữ sắc nét)
        'text-secondary': '#8A6F52',// Nâu nhạt — mô tả, chú thích
        'text-on-primary': '#FBF3E6', // Kem sáng — chữ trên nền primary/accent
      },
      borderRadius: {
        'card': '12px',
        'btn': '10px',
        'input': '10px',
      },
      fontFamily: {
        heading: ['"Cormorant Garamond"', '"Marcellus"', 'serif'],
        body: ['"Be Vietnam Pro"', '"Inter"', 'sans-serif'],
      },
      boxShadow: {
        'subtle': '0 2px 8px rgba(107, 43, 31, 0.04)',
        'elevated': '0 4px 16px rgba(107, 43, 31, 0.08)',
      }
    },
  },
  plugins: [],
}
