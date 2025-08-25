<template>
  <div id="app" class="min-h-screen bg-background text-foreground">
    <div class="flex h-screen">
      <!-- Sidebar -->
      <Sidebar 
        :sessions="sessions"
        :current-session="currentSession"
        @session-select="selectSession"
        @session-create="createSession"
        @session-delete="deleteSession"
        class="w-80 border-r border-border"
      />
      
      <!-- Main Content -->
      <div class="flex-1 flex flex-col">
        <!-- Header -->
        <header class="h-16 border-b border-border flex items-center justify-between px-6">
          <div class="flex items-center space-x-4">
            <h1 class="text-xl font-semibold">Agentic AI</h1>
            <div v-if="currentSession" class="text-sm text-muted-foreground">
              Session: {{ currentSession.session_id.slice(0, 8) }}...
            </div>
          </div>
          <div class="flex items-center space-x-2">
            <button 
              @click="toggleVNC"
              class="px-3 py-1 text-sm bg-secondary hover:bg-secondary/80 rounded-md transition-colors"
            >
              {{ showVNC ? 'Hide VNC' : 'Show VNC' }}
            </button>
            <button 
              @click="toggleTools"
              class="px-3 py-1 text-sm bg-secondary hover:bg-secondary/80 rounded-md transition-colors"
            >
              {{ showTools ? 'Hide Tools' : 'Show Tools' }}
            </button>
          </div>
        </header>

        <!-- Content Area -->
        <div class="flex-1 flex">
          <!-- Chat Area -->
          <div class="flex-1 flex flex-col">
            <ChatPage 
              v-if="currentSession"
              :session="currentSession"
              @message-send="sendMessage"
              @session-stop="stopSession"
              class="flex-1"
            />
            <div v-else class="flex-1 flex items-center justify-center">
              <div class="text-center">
                <h2 class="text-2xl font-semibold mb-4">Welcome to Agentic AI</h2>
                <p class="text-muted-foreground mb-6">Create a new session to start chatting with your AI agent</p>
                <button 
                  @click="createSession"
                  class="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                  Start New Session
                </button>
              </div>
            </div>
          </div>

          <!-- Tool Panel -->
          <ToolPanel 
            v-if="showTools && currentSession"
            :session-id="currentSession.session_id"
            @tool-action="handleToolAction"
            class="w-96 border-l border-border"
          />
        </div>

        <!-- VNC Viewer -->
        <div v-if="showVNC && currentSession" class="h-96 border-t border-border">
          <VNCViewer 
            :session-id="currentSession.session_id"
            class="w-full h-full"
          />
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-background p-6 rounded-lg shadow-lg">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
          <span>{{ loadingMessage }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatPage from './components/ChatPage.vue'
import ToolPanel from './components/ToolPanel.vue'
import VNCViewer from './components/VNCViewer.vue'
import { sessionService } from './services/sessionService'
import type { Session } from './types/session'

// State
const sessions = ref<Session[]>([])
const currentSession = ref<Session | null>(null)
const showVNC = ref(false)
const showTools = ref(true)
const loading = ref(false)
const loadingMessage = ref('')

// Methods
const loadSessions = async () => {
  try {
    const response = await sessionService.listSessions()
    sessions.value = response.data.sessions
  } catch (error) {
    console.error('Failed to load sessions:', error)
  }
}

const createSession = async () => {
  loading.value = true
  loadingMessage.value = 'Creating new session...'
  
  try {
    const response = await sessionService.createSession()
    const newSession = await sessionService.getSession(response.data.session_id)
    sessions.value.unshift(newSession.data)
    currentSession.value = newSession.data
  } catch (error) {
    console.error('Failed to create session:', error)
  } finally {
    loading.value = false
  }
}

const selectSession = async (sessionId: string) => {
  loading.value = true
  loadingMessage.value = 'Loading session...'
  
  try {
    const response = await sessionService.getSession(sessionId)
    currentSession.value = response.data
  } catch (error) {
    console.error('Failed to load session:', error)
  } finally {
    loading.value = false
  }
}

const deleteSession = async (sessionId: string) => {
  try {
    await sessionService.deleteSession(sessionId)
    sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
    if (currentSession.value?.session_id === sessionId) {
      currentSession.value = null
    }
  } catch (error) {
    console.error('Failed to delete session:', error)
  }
}

const sendMessage = async (message: string) => {
  if (!currentSession.value) return
  
  try {
    // Message sending is handled by ChatPage component via SSE
    await sessionService.sendMessage(currentSession.value.session_id, message)
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const stopSession = async () => {
  if (!currentSession.value) return
  
  try {
    await sessionService.stopSession(currentSession.value.session_id)
  } catch (error) {
    console.error('Failed to stop session:', error)
  }
}

const toggleVNC = () => {
  showVNC.value = !showVNC.value
}

const toggleTools = () => {
  showTools.value = !showTools.value
}

const handleToolAction = (action: any) => {
  console.log('Tool action:', action)
  // Handle tool actions like shell commands, file operations, etc.
}

// Lifecycle
onMounted(() => {
  loadSessions()
})
</script>
