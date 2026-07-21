<script setup lang="ts">
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const submitting = ref(false)
const { request } = useApi()

async function submit() {
  submitting.value = true
  errorMessage.value = ''
  try {
    await request('/auth/login/', {
      method: 'POST',
      body: { username: username.value, password: password.value },
    })
    await navigateTo('/')
  } catch {
    errorMessage.value = 'Unable to sign in. Check your username and password.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="auth-card">
    <p class="eyebrow">Livestock management</p>
    <h1>Welcome back</h1>
    <p>Sign in to manage your farm, animals, and upcoming work.</p>
    <form class="stack" @submit.prevent="submit">
      <label>Username <input v-model="username" autocomplete="username" required></label>
      <label>Password <input v-model="password" type="password" autocomplete="current-password" required></label>
      <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>
      <button type="submit" :disabled="submitting">
        {{ submitting ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>
  </section>
</template>
