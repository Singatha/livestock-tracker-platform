interface InstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function usePwaInstall() {
  const installPrompt = useState<InstallPromptEvent | null>('pwa-install-prompt', () => null)
  const canInstall = computed(() => installPrompt.value !== null)

  async function install() {
    if (!installPrompt.value) return
    const prompt = installPrompt.value
    await prompt.prompt()
    await prompt.userChoice
    installPrompt.value = null
  }

  return { canInstall, install }
}
