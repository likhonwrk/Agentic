<template>
  <div class="flex flex-col h-full bg-secondary/20">
    <!-- Header -->
    <div class="p-4 border-b border-border">
      <button 
        @click="$emit('session-create')"
        class="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors flex items-center justify-center space-x-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        <span>New Session</span>
      </button>
    </div>

    <!-- Sessions List -->
    <div class="flex-1 overflow-y-auto">
      <div v-if="sessions.length === 0" class="p-4 text-center text-muted-foreground">
        No sessions yet
      </div>
      <div v-else class="p-2">
        <div 
          v-for="session in sessions" 
          :key="session.session_id"
          @click="$emit('session-select', session.session_id)"
          class="p-3 mb-2 rounded-lg cursor-pointer transition-colors hover:bg-secondary/50"
          :class="{ 'bg-secondary': currentSession?.session_id === session.session_id }"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <h3 class="font-medium truncate">
                {{ session.title || `Session ${session.session_id.slice(0, 8)}` }}
              </h3>
              <p class="text-sm text-muted-foreground truncate mt-1">
                {{ session.latest_message || 'No messages yet' }}
              </p>
              <div class="flex items-center justify-between mt-2">
                <span class="text-xs text-muted-foreground">
                  {{ formatTime(session.latest_message_at) }}
                </span>
                <div class="flex items-center space-x-2">
                  <span 
                    v-if="session.unread_message_count > 0"
                    class="px-2 py-1 text-xs bg-primary text-primary-foreground rounded-full"
                  >
                    {{ session.unread_message_count }}
                  </span>
                  <span 
                    class="px-2 py-1 text-xs rounded-full"
                    :class="getStatusClass(session.status)"
                  >
                    {{ session.status }}
                  </span>
                </div>
              </div>
            </div>
            <button 
              @click.stop="$emit('session-delete', session.session_id)"
              class="ml-2 p-1 text-muted-foreground hover:text-destructive transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Session } from '../types/session'

defineProps<{
  sessions: Session[]
  currentSession: Session | null
}>()

defineEmits<{
  'session-select': [sessionId: string]
  'session-create': []
  'session-delete': [sessionId: string]
}>()

const formatTime = (timestamp?: number) => {
  if (!timestamp) return 'Never'
  return new Date(timestamp * 1000).toLocaleString()
}

const getStatusClass = (status: string) => {
  switch (status) {
    case 'active':
      return 'bg-green-500/20 text-green-400'
    case 'idle':
      return 'bg-yellow-500/20 text-yellow-400'
    case 'error':
      return 'bg-red-500/20 text-red-400'
    default:
      return 'bg-secondary text-muted-foreground'
  }
}
</script>
