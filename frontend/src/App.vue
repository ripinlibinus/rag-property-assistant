<template>
  <div class="h-screen flex bg-gray-50">
    <!-- Mobile Backdrop -->
    <div
      v-if="sidebarOpen && isMobile"
      class="fixed inset-0 bg-black/50 z-40 md:hidden"
      @click="sidebarOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'flex flex-col bg-gray-900 text-white transition-all duration-300 ease-in-out',
        sidebarOpen
          ? 'fixed inset-y-0 left-0 z-50 w-full sm:w-72 md:relative md:w-64'
          : 'w-0 overflow-hidden'
      ]"
    >
      <!-- Sidebar Header -->
      <div class="p-4 border-b border-gray-700">
        <button
          @click="startNewChat"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg border border-gray-600 hover:bg-gray-800 transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          <span class="font-medium">New Chat</span>
        </button>
      </div>

      <!-- Chat History - Under Development -->
      <div class="flex-1 overflow-y-auto p-4">
        <div class="text-center py-8">
          <div class="w-12 h-12 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path>
            </svg>
          </div>
          <p class="text-sm text-gray-400 leading-relaxed">
            Chat history feature is under development. All conversations are automatically saved on the server.
          </p>
          <div class="mt-4 px-3 py-2 bg-gray-800 rounded-lg">
            <p class="text-xs text-gray-500">Coming Soon</p>
          </div>
        </div>
      </div>

      <!-- Sidebar Footer -->
      <div class="p-4 border-t border-gray-700 space-y-3">
        <!-- Documentation Button -->
        <button
          @click="goToDocumentation"
          class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition-colors text-left"
          :class="currentPage === 'docs' ? 'bg-gray-800 text-white' : 'text-gray-300'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
          </svg>
          <span class="text-sm font-medium">Documentation</span>
        </button>

        <!-- Method Selector (only show when on chat page) -->
        <div v-if="currentPage === 'chat'" class="space-y-1">
          <label class="text-xs text-gray-400">Search Method</label>
          <select
            v-model="searchMethod"
            class="w-full text-sm bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="hybrid">Hybrid (Best)</option>
            <option value="api_only">API Only</option>
            <option value="vector_only">Vector Only</option>
          </select>
        </div>

        <!-- App Info -->
        <div class="flex items-center gap-2 text-xs text-gray-400">
          <div class="w-6 h-6 bg-gradient-to-br from-blue-500 to-indigo-600 rounded flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
          </div>
          <span>Property Assistant v1.0</span>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top Bar -->
      <header class="h-14 border-b bg-white flex items-center px-4 gap-4">
        <!-- Toggle Sidebar Button -->
        <button
          @click="sidebarOpen = !sidebarOpen"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          :title="sidebarOpen ? 'Close sidebar' : 'Open sidebar'"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>

        <!-- Title -->
        <div class="flex-1 flex items-center gap-2 sm:gap-3 min-w-0">
          <h1 class="text-base sm:text-lg font-semibold text-gray-800 truncate">
            <span class="hidden sm:inline">Property Search Assistant</span>
            <span class="sm:hidden">Property Search</span>
          </h1>
          <span v-if="currentPage === 'chat'" class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full whitespace-nowrap">{{ methodLabel }}</span>
          <span v-else class="text-xs px-2 py-0.5 bg-emerald-100 text-emerald-700 rounded-full whitespace-nowrap">Docs</span>
        </div>

        <!-- New Chat Button (mobile) -->
        <button
          @click="startNewChat"
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="New Chat"
        >
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
        </button>
      </header>

      <!-- Content Area -->
      <main class="flex-1 overflow-hidden">
        <!-- Chat Interface -->
        <ChatInterface
          v-if="currentPage === 'chat'"
          ref="chatRef"
          :method="searchMethod"
          :key="chatKey"
        />
        <!-- Documentation Page -->
        <DocumentationPage
          v-else
          @back-to-chat="goToChat"
        />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import ChatInterface from './components/ChatInterface.vue'
import DocumentationPage from './components/DocumentationPage.vue'

const searchMethod = ref('hybrid')
const sidebarOpen = ref(true)
const chatKey = ref(0)
const chatRef = ref(null)
const currentPage = ref('chat') // 'chat' | 'docs'
const isMobile = ref(false)

const methodLabel = computed(() => {
  const labels = {
    hybrid: 'Hybrid',
    api_only: 'API Only',
    vector_only: 'Vector'
  }
  return labels[searchMethod.value] || 'Hybrid'
})

function checkMobile() {
  isMobile.value = window.innerWidth < 768
  // Auto-close sidebar on mobile
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

function startNewChat() {
  chatKey.value++ // Force re-render ChatInterface
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

function goToDocumentation() {
  currentPage.value = 'docs'
  if (isMobile.value) {
    sidebarOpen.value = false
  }
}

function goToChat() {
  currentPage.value = 'chat'
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style>
/* Hide scrollbar for chat history but allow scrolling */
aside::-webkit-scrollbar {
  width: 6px;
}
aside::-webkit-scrollbar-track {
  background: transparent;
}
aside::-webkit-scrollbar-thumb {
  background: #4b5563;
  border-radius: 3px;
}
aside::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>
