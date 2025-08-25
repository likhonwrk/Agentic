<template>
  <div class="flex flex-col h-full">
    <!-- Messages Area -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div v-if="session.events.length === 0" class="text-center text-muted-foreground py-8">
        Start a conversation with your AI agent
      </div>
      
      <ChatMessage 
        v-for="event in session.events" 
        :key="event.id || event.timestamp"
        :event="event"
        class="max-w-4xl"
      />
      
      <!-- Typing Indicator -->
      <div v-if="isTyping" class="flex items-center space-x-2 text-muted-foreground">
        <div class="flex space-x-1">
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
          <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        </div>
        <span>Agent is thinking...</span>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-border p-4">
      <ChatInput 
        @message-send="handleMessageSend"
        @session-stop="$emit('session-stop')"
        :disabled="isProcessing"
        :session-active="session.status === 'active'"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import ChatMessage from './ChatMessage.vue'
import ChatInput from './ChatInput.vue'
import { sessionService } from '../services/sessionService'
import type { Session, ChatEvent } from '../types/session'

const props = defineProps<{
  session: Session
}>()

const emit = defineEmits<{
  'message-send': [message: string]
  'session-stop': []
}>()

// State
const messagesContainer = ref<HTMLElement>()
const isTyping = ref(false)
const isProcessing = ref(false)

// Methods
const handleMessageSend = async (message: string) => {
  if (isProcessing.value) return
  
  isProcessing.value = true
  isTyping.value = true
  
  try {
    // Add user message to events
    const userEvent: ChatEvent = {
      id: Date.now().toString(),
      type: 'message',
      content: message,
      timestamp: Date.now(),
      sender: 'user'
    }
    props.session.events.push(userEvent)
    
    await nextTick()
    scrollToBottom()
    
    // Start SSE connection for streaming response
    await startSSEConnection(message)
    
  } catch (error) {
    console.error('Failed to send message:', error)
    isTyping.value = false
    isProcessing.value = false
  }
}

const startSSEConnection = async (message: string) => {
  try {
    const response = await fetch(`/api/v1/sessions/${props.session.session_id}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        timestamp: Date.now()
      })
    })

    if (!response.ok) throw new Error('Failed to start chat')

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    let currentEvent: ChatEvent | null = null

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = new TextDecoder().decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            switch (data.type) {
              case 'message':
                if (!currentEvent) {
                  currentEvent = {
                    id: Date.now().toString(),
                    type: 'message',
                    content: '',
                    timestamp: Date.now(),
                    sender: 'assistant'
                  }
                  props.session.events.push(currentEvent)
                }
                currentEvent.content += data.content
                break
                
              case 'title':
                props.session.title = data.content
                break
                
              case 'plan':
                props.session.events.push({
                  id: Date.now().toString(),
                  type: 'plan',
                  content: data.content,
                  timestamp: Date.now(),
                  sender: 'assistant'
                })
                break
                
              case 'step':
                props.session.events.push({
                  id: Date.now().toString(),
                  type: 'step',
                  content: data.content,
                  timestamp: Date.now(),
                  sender: 'assistant',
                  metadata: { status: data.status }
                })
                break
                
              case 'tool':
                props.session.events.push({
                  id: Date.now().toString(),
                  type: 'tool',
                  content: data.content,
                  timestamp: Date.now(),
                  sender: 'assistant',
                  metadata: { tool: data.tool, action: data.action }
                })
                break
                
              case 'error':
                props.session.events.push({
                  id: Date.now().toString(),
                  type: 'error',
                  content: data.content,
                  timestamp: Date.now(),
                  sender: 'assistant'
                })
                break
                
              case 'done':
                isTyping.value = false
                isProcessing.value = false
                break
            }
            
            await nextTick()
            scrollToBottom()
            
          } catch (e) {
            console.error('Failed to parse SSE data:', e)
          }
        }
      }
    }
    
  } catch (error) {
    console.error('SSE connection failed:', error)
    isTyping.value = false
    isProcessing.value = false
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Watchers
watch(() => props.session.events.length, () => {
  nextTick(() => scrollToBottom())
})

// Lifecycle
onMounted(() => {
  scrollToBottom()
})

onUnmounted(() => {
  // Clean up any active connections
})
</script>
