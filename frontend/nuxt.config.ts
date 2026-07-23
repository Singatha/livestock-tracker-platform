import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2026-07-21',
  css: ['~/assets/css/main.css'],
  devtools: { enabled: false },
  modules: ['shadcn-nuxt', '@vite-pwa/nuxt'],
  app: {
    head: {
      title: 'Flockwise',
      meta: [
        { name: 'description', content: 'Livestock health, breeding, medicine, and farm task management.' },
        { name: 'theme-color', content: '#075f38' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'default' },
      ],
      link: [
        { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' },
        { rel: 'apple-touch-icon', href: '/icons/apple-touch-icon.png' },
      ],
    },
  },
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Flockwise Livestock Tracker',
      short_name: 'Flockwise',
      description: 'Livestock health, breeding, medicine, and farm task management.',
      theme_color: '#075f38',
      background_color: '#f7f6f0',
      display: 'standalone',
      start_url: '/',
      scope: '/',
      icons: [
        { src: '/icons/pwa-192x192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icons/pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        { src: '/icons/pwa-maskable-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
    },
    workbox: {
      navigateFallback: '/offline',
      globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
      navigateFallbackDenylist: [/^\/api\//, /^\/media\//],
      cleanupOutdatedCaches: true,
    },
    devOptions: {
      enabled: false,
    },
  },
  shadcn: {
    prefix: '',
    componentDir: '@/components/ui',
  },
  vite: {
    plugins: [tailwindcss()],
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
    },
  },
  typescript: {
    strict: true,
    // Run `npm run typecheck` explicitly; the Vite checker overlay is not needed in dev.
    typeCheck: false,
  },
})
