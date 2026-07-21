export default defineNuxtConfig({
  compatibilityDate: '2026-07-21',
  css: ['~/assets/css/main.css'],
  devtools: { enabled: true },
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
