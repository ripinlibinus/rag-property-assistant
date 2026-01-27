<template>
  <div class="h-full flex flex-col bg-white">
    <!-- Messages Area -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto">
      <!-- Content Container (centered, max-width like ChatGPT) -->
      <div class="max-w-3xl mx-auto px-4 py-6 space-y-6">
        <!-- Welcome message -->
        <div v-if="messages.length === 0" class="text-center py-20">
          <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-3">Property Search Assistant</h2>
          <p class="text-gray-500 max-w-lg mx-auto mb-8">
            Find your dream property with AI-powered search. Ask me anything about houses, apartments, or land in Indonesia.
          </p>
          <div class="flex flex-wrap justify-center gap-3">
            <button
              v-for="suggestion in suggestions"
              :key="suggestion"
              @click="sendMessage(suggestion)"
              class="px-5 py-2.5 bg-white border border-gray-200 hover:border-blue-300 hover:bg-blue-50 rounded-xl text-sm text-gray-700 transition-all shadow-sm"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>

        <!-- Chat messages -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          :class="['py-4', msg.role === 'user' ? 'bg-transparent' : 'bg-gray-50 -mx-4 px-4 rounded-xl']"
        >
          <div class="flex gap-4">
            <!-- Avatar -->
            <div class="flex-shrink-0">
              <div v-if="msg.role === 'user'" class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                </svg>
              </div>
              <div v-else class="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
              </div>
            </div>
            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium text-gray-500 mb-1">{{ msg.role === 'user' ? 'You' : 'Assistant' }}</div>
              <div v-if="msg.role === 'assistant'" class="chat-message prose prose-sm max-w-none text-gray-800" v-html="formatMessage(msg.displayText)"></div>
              <div v-else class="text-gray-800">{{ msg.content }}</div>
              <div class="text-xs text-gray-400 mt-2">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>
        </div>

        <!-- Agent Reasoning Panel (shows during streaming) -->
        <div v-if="isLoading" class="py-4 bg-gray-50 -mx-4 px-4 rounded-xl">
          <div class="flex gap-4">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <!-- Agent Status -->
              <div class="flex items-center gap-2 mb-3">
                <div class="text-sm font-semibold text-gray-800">Assistant</div>
                <div class="text-xs text-emerald-600">{{ agentStatusText }}</div>
              </div>

              <!-- Reasoning Steps -->
              <div class="space-y-2 max-h-[300px] overflow-y-auto overflow-x-hidden pb-2" id="reasoning-scroll">
                <div
                  v-for="(step, idx) in reasoningSteps"
                  :key="idx"
                  class="flex items-start gap-2 text-sm"
                >
                  <!-- Step Icon -->
                  <div :class="[getStepIconClass(step.type)]">
                    <svg v-if="step.type === 'thinking'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                    </svg>
                    <svg v-else-if="step.type === 'tool_call'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <svg v-else-if="step.type === 'tool_result'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <svg v-else-if="step.type === 'geocoding'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    </svg>
                    <svg v-else-if="step.type === 'api_call'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                    </svg>
                    <svg v-else-if="step.type === 'reranking'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"></path>
                    </svg>
                    <svg v-else-if="step.type === 'writing'" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>

                  <!-- Step Content -->
                  <div class="flex-1 min-w-0">
                    <div :class="[getStepTextClass(step.type)]">{{ step.title }}</div>
                    <div v-if="step.detail && step.type !== 'thinking'" class="text-xs text-gray-500 mt-0.5 break-words">{{ step.detail }}</div>
                    <!-- JSON Preview for tool calls -->
                    <div v-if="step.json" class="mt-1 p-2 bg-gray-800 rounded text-xs font-mono text-green-400 overflow-hidden">
                      <pre class="whitespace-pre-wrap break-all">{{ step.json }}</pre>
                    </div>
                  </div>

                  <!-- Loading indicator -->
                  <div v-if="step.loading" class="flex-shrink-0">
                    <svg class="w-4 h-4 text-emerald-500 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                    </svg>
                  </div>
                  <div v-else-if="step.done" class="flex-shrink-0">
                    <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                </div>
              </div>

              <!-- Status Bar -->
              <div class="mt-3 pt-2 border-t border-gray-200 text-xs text-gray-400 text-right">
                <span v-if="reasoningSteps.length > 0">{{ reasoningSteps.length }} steps completed</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t bg-white p-4">
      <div class="max-w-3xl mx-auto">
        <form @submit.prevent="handleSubmit" class="flex gap-3 items-end">
          <textarea
            ref="inputRef"
            v-model="inputMessage"
            placeholder="Ask about properties..."
            rows="1"
            class="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-gray-50 resize-none overflow-hidden"
            :disabled="isLoading"
            @keydown="handleKeyDown"
            @input="autoResizeTextarea"
          />
          <button
            type="submit"
            :disabled="isButtonDisabled"
            class="px-6 py-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            <svg v-if="!isLoading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
            </svg>
            <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  method: {
    type: String,
    default: 'hybrid'
  }
})


// Session Management
const STORAGE_KEY = 'rag-chat-session-id'

function getOrCreateSessionId() {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) {
    return stored
  }
  const newId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
  localStorage.setItem(STORAGE_KEY, newId)
  return newId
}

function startNewSession() {
  const newId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9)
  localStorage.setItem(STORAGE_KEY, newId)
  sessionId.value = newId
  messages.value = []
  reasoningSteps.value = []
}

// State
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
const sessionId = ref(getOrCreateSessionId())

// Reasoning steps for detailed agent display
const reasoningSteps = ref([])
const agentStatusText = ref('Initializing...')

// Fun rotating messages for writing phase
const writingMessages = [
  'Crafting response...',
  'Analyzing data...',
  'Processing results...',
  'Preparing recommendations...',
  'Matching properties...',
  'Almost there...',
  'Finishing touches...',
  'Polishing answer...',
  'Just a moment...',
  'Wrapping up...',
]
let writingMsgIndex = 0
let writingMsgTimer = null

function startWritingMessages() {
  writingMsgIndex = 0
  updateWritingMessage()
  writingMsgTimer = setInterval(() => {
    writingMsgIndex = (writingMsgIndex + 1) % writingMessages.length
    updateWritingMessage()
  }, 2000)
}

function updateWritingMessage() {
  const writingStep = reasoningSteps.value.find(s => s.type === 'writing' && s.loading)
  if (writingStep) {
    writingStep.title = writingMessages[writingMsgIndex]
  }
  agentStatusText.value = writingMessages[writingMsgIndex]
  scrollReasoningToBottom()
}

function stopWritingMessages() {
  if (writingMsgTimer) {
    clearInterval(writingMsgTimer)
    writingMsgTimer = null
  }
}

const suggestions = [
  'Cari rumah di cemara asri medan',
  'Rumah 3 kamar harga di bawah 2M di medan',
  'Rumah dekat mall di batam'
]

// Mobile detection
const isMobile = ref(false)

function checkMobile() {
  isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    || window.innerWidth < 768
}

// Keyboard handler for textarea
function handleKeyDown(event) {
  if (event.key === 'Enter') {
    if (isMobile.value) {
      // Mobile: Enter = new line, only button sends
      return // Allow default behavior (new line)
    } else {
      // Desktop: Enter = send, Shift+Enter = new line
      if (!event.shiftKey) {
        event.preventDefault()
        handleSubmit()
      }
      // Shift+Enter: allow default behavior (new line)
    }
  }
}

// Auto-resize textarea
function autoResizeTextarea(event) {
  const textarea = event.target
  textarea.style.height = 'auto'
  textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
}

// Reset textarea height
function resetTextareaHeight() {
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
  }
}

// Focus input
function focusInput() {
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus()
    }
  })
}

// Computed
const isButtonDisabled = computed(() => {
  return !inputMessage.value.trim() || isLoading.value
})

// Methods
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

function formatMessage(content) {
  if (!content) return ''
  let formatted = content
  // Markdown links [text](url)
  formatted = formatted.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" class="text-blue-600 hover:text-blue-800 underline">$1</a>')
  // Standalone URLs
  formatted = formatted.replace(/(^|[^"'])(https?:\/\/[^\s<]+)/g,
    '$1<a href="$2" target="_blank" class="text-blue-600 hover:text-blue-800 underline break-all">$2</a>')
  // Bold
  formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  // Newlines to br
  formatted = formatted.replace(/\n/g, '<br>')
  return formatted
}

function getStepIconClass(type) {
  const baseClass = 'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center'
  switch (type) {
    case 'thinking':
      return `${baseClass} bg-amber-100 text-amber-600`
    case 'tool_call':
      return `${baseClass} bg-blue-100 text-blue-600`
    case 'tool_result':
      return `${baseClass} bg-green-100 text-green-600`
    case 'geocoding':
      return `${baseClass} bg-blue-100 text-blue-600`
    case 'api_call':
      return `${baseClass} bg-purple-100 text-purple-600`
    case 'reranking':
      return `${baseClass} bg-pink-100 text-pink-600`
    case 'writing':
      return `${baseClass} bg-emerald-100 text-emerald-600`
    default:
      return `${baseClass} bg-gray-100 text-gray-600`
  }
}

function getStepTextClass(type) {
  switch (type) {
    case 'thinking':
      return 'text-amber-700 font-medium'
    case 'tool_result':
      return 'text-green-700 font-medium'
    case 'geocoding':
      return 'text-blue-700 font-medium'
    case 'api_call':
      return 'text-purple-700 font-medium'
    case 'reranking':
      return 'text-pink-700 font-medium'
    case 'writing':
      return 'text-emerald-700 font-medium'
    default:
      return 'text-gray-700'
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function scrollReasoningToBottom() {
  nextTick(() => {
    const el = document.getElementById('reasoning-scroll')
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

function addReasoningStep(step) {
  if (reasoningSteps.value.length > 0) {
    const lastStep = reasoningSteps.value[reasoningSteps.value.length - 1]
    if (lastStep.loading) {
      lastStep.loading = false
      lastStep.done = true
    }
  }
  reasoningSteps.value.push(step)
  scrollToBottom()
  scrollReasoningToBottom()
}

function updateLastStep(updates) {
  if (reasoningSteps.value.length > 0) {
    Object.assign(reasoningSteps.value[reasoningSteps.value.length - 1], updates)
  }
}

function parseToolName(name) {
  const toolNames = {
    'search_properties': 'Property Search',
    'geocode_location': 'Geocoding',
    'get_knowledge': 'Knowledge Base',
    'search_properties_api': 'API Search',
    'search_properties_semantic': 'Semantic Search',
    'search_properties_hybrid': 'Hybrid Search'
  }
  return toolNames[name] || name
}

function formatToolArgs(args) {
  if (!args) return null
  try {
    const parsed = typeof args === 'string' ? JSON.parse(args) : args
    return JSON.stringify(parsed, null, 2)
  } catch {
    return null
  }
}

function getToolCallDescription(name, args) {
  try {
    const parsed = typeof args === 'string' ? JSON.parse(args) : args
    if (name === 'geocode_location') {
      return `Finding coordinates for "${parsed.address || parsed.location}"`
    }
    if (name.includes('search')) {
      const parts = []
      if (parsed.location) parts.push(`Location: ${parsed.location}`)
      if (parsed.property_type) parts.push(`Type: ${parsed.property_type}`)
      if (parsed.min_price || parsed.max_price) {
        parts.push(`Price: ${parsed.min_price || 0} - ${parsed.max_price || 'unlimited'}`)
      }
      return parts.join(' | ') || 'Searching properties...'
    }
    return null
  } catch {
    return null
  }
}

function parseToolResult(content) {
  if (!content) return { type: 'text', content: 'No result' }

  const contentStr = String(content)

  if (contentStr.includes('Found') && contentStr.includes('properties')) {
    const match = contentStr.match(/Found (\d+) properties/)
    return {
      type: 'properties',
      count: match ? parseInt(match[1]) : 0,
      content: contentStr
    }
  }

  if (contentStr.includes('coordinates')) {
    return { type: 'geocoding', content: contentStr }
  }

  if (contentStr.includes('reranked') || contentStr.includes('Semantic')) {
    return { type: 'reranking', content: contentStr }
  }

  return { type: 'text', content: contentStr.length > 50 ? contentStr.substring(0, 50) + '...' : contentStr }
}

function truncateContent(content) {
  if (!content) return ''
  return content.length > 50 ? content.substring(0, 50) + '...' : content
}

async function typeText(msgIndex, fullText) {
  const msg = messages.value[msgIndex]
  if (!msg) return

  const length = fullText.length
  const chunkSize = Math.max(3, Math.min(8, Math.floor(length / 80)))
  let pos = 0

  return new Promise(resolve => {
    const interval = setInterval(() => {
      pos = Math.min(pos + chunkSize, length)
      msg.displayText = fullText.substring(0, pos)
      scrollToBottom()

      if (pos >= length) {
        clearInterval(interval)
        msg.displayText = fullText
        resolve()
      }
    }, 12)
  })
}

async function sendMessage(text) {
  inputMessage.value = text
  await handleSubmit()
}

async function handleSubmit() {
  const text = inputMessage.value.trim()
  if (!text || isLoading.value) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: text,
    displayText: text,
    timestamp: new Date()
  })

  inputMessage.value = ''
  resetTextareaHeight()
  isLoading.value = true
  reasoningSteps.value = []
  agentStatusText.value = 'Starting...'

  scrollToBottom()
  focusInput()

  // Use streaming
  await handleStreamingChat(text)
}

async function handleStreamingChat(text) {
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: text,
      session_id: sessionId.value,
      method: props.method
    })
  })

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let finalResponse = ''
  let currentToolName = ''

  // Add initial thinking step
  addReasoningStep({
    type: 'thinking',
    title: 'Analyzing your request...',
    detail: '',
    loading: true
  })

  let buffer = ''  // Buffer for incomplete lines

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      buffer += chunk
      const lines = buffer.split('\n')

      // Keep the last incomplete line in buffer
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue

        try {
          const data = JSON.parse(line.slice(6))

          switch (data.type) {
            case 'user_input':
              agentStatusText.value = 'Processing...'
              break

            case 'reasoning_token':
              if (reasoningSteps.value.length > 0) {
                const lastStep = reasoningSteps.value[reasoningSteps.value.length - 1]
                if (lastStep.loading && (lastStep.type === 'thinking' || lastStep.type === 'writing')) {
                  if (lastStep.type === 'thinking') {
                    lastStep.detail = (lastStep.detail || '') + data.content
                  }
                } else if (!lastStep.loading && lastStep.type !== 'writing') {
                  addReasoningStep({
                    type: 'writing',
                    title: writingMessages[0],
                    detail: '',
                    loading: true
                  })
                  startWritingMessages()
                }
              }
              break

            case 'reasoning_done':
              updateLastStep({ loading: false, done: true })
              agentStatusText.value = 'Deciding next action...'
              break

            case 'tool_call':
              currentToolName = data.name
              agentStatusText.value = `Calling ${parseToolName(data.name)}...`

              const toolTitle = parseToolName(data.name)
              const jsonArgs = formatToolArgs(data.args)

              let stepType = 'tool_call'
              if (data.name === 'geocode_location') {
                stepType = 'geocoding'
              } else if (data.name.includes('search')) {
                stepType = 'api_call'
              }

              addReasoningStep({
                type: stepType,
                title: `Calling: ${toolTitle}`,
                detail: getToolCallDescription(data.name, data.args),
                json: jsonArgs,
                loading: true
              })
              break

            case 'tool_result':
              const result = parseToolResult(data.content)
              updateLastStep({ loading: false, done: true })

              if (result.type === 'properties') {
                addReasoningStep({
                  type: 'tool_result',
                  title: `Found ${result.count} properties`,
                  detail: '',
                  loading: false,
                  done: true
                })
              } else if (result.type === 'reranking') {
                addReasoningStep({
                  type: 'reranking',
                  title: 'Semantic reranking applied',
                  detail: 'Results sorted by relevance to your query',
                  loading: false,
                  done: true
                })
              } else {
                addReasoningStep({
                  type: 'tool_result',
                  title: truncateContent(result.content),
                  detail: '',
                  loading: false,
                  done: true
                })
              }

              agentStatusText.value = 'Processing results...'
              break

            case 'response_token':
              finalResponse += data.content
              agentStatusText.value = 'Writing response...'
              break

            case 'response_done':
              finalResponse = data.content
              stopWritingMessages()
              agentStatusText.value = 'Complete!'
              updateLastStep({ loading: false, done: true })
              break

            case 'done':
              break

            case 'error':
              console.error('Stream error:', data.content)
              break
          }
        } catch (e) {
          // Ignore JSON parse errors
        }
      }
    }
  } finally {
    stopWritingMessages()
    isLoading.value = false

    // Add assistant message with typing effect
    if (finalResponse) {
      const msgIndex = messages.value.length
      messages.value.push({
        role: 'assistant',
        content: finalResponse,
        displayText: '',
        timestamp: new Date()
      })

      await typeText(msgIndex, finalResponse)
    }

    scrollToBottom()
    focusInput()
  }
}

// Lifecycle
onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  inputRef.value?.focus()
})

onUnmounted(() => {
  stopWritingMessages()
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.chat-message a {
  word-break: break-all;
}

@keyframes pulse-text {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.animate-pulse-text {
  animation: pulse-text 1.2s ease-in-out infinite;
}

/* Custom scrollbar */
#reasoning-scroll::-webkit-scrollbar {
  width: 4px;
}

#reasoning-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

#reasoning-scroll::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

#reasoning-scroll::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
