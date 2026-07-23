interface InstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export default defineNuxtPlugin(() => {
  const installPrompt = useState<InstallPromptEvent | null>('pwa-install-prompt', () => null)

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault()
    installPrompt.value = event as InstallPromptEvent
  })
  window.addEventListener('appinstalled', () => {
    installPrompt.value = null
  })
})
