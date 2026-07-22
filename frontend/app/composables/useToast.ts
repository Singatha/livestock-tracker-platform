export type ToastVariant = 'success' | 'error' | 'info'

export interface ToastMessage {
  id: number
  title: string
  description?: string
  variant: ToastVariant
}

let nextToastId = 0

export function useToast() {
  const messages = useState<ToastMessage[]>('toast-messages', () => [])

  function dismiss(id: number) {
    messages.value = messages.value.filter(message => message.id !== id)
  }

  function show(title: string, options: { description?: string, variant?: ToastVariant } = {}) {
    const id = ++nextToastId
    messages.value.push({ id, title, description: options.description, variant: options.variant || 'info' })
    if (import.meta.client) window.setTimeout(() => dismiss(id), 4500)
  }

  return {
    messages,
    dismiss,
    success: (title: string, description?: string) => show(title, { description, variant: 'success' }),
    error: (title: string, description?: string) => show(title, { description, variant: 'error' }),
    info: (title: string, description?: string) => show(title, { description, variant: 'info' }),
  }
}
