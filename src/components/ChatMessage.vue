<template>
  <div class="flex" :class="{ 'justify-end': event.sender === 'user' }">
    <div 
      class="max-w-[80%] rounded-lg p-4"
      :class="getMessageClass()"
    >
      <!-- Message Header -->
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center space-x-2">
          <div 
            class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium"
            :class="getAvatarClass()"
          >
            {{ event.sender === 'user' ? 'U' : 'A' }}
          </div>
          <span class="text-sm font-medium">
            {{ event.sender === 'user' ? 'You' : 'Agent' }}
          </span>
          <span v-if="event.type !== 'message'" class="px-2 py-1 text-xs rounded-full bg-secondary">
            {{ event.type }}
          </span>
        </div>
        <span class="text-xs text-muted-foreground">
          {{ formatTime(event.timestamp) }}
        </span>
      </div>

      <!-- Message Content -->
      <div class="prose prose-sm max-w-none" :class="getContentClass()">
        <!-- Regular Message -->
        <div v-if="event.type === 'message'" v-html="formatContent(event.content)"></div>
        
        <!-- Plan -->
        <div v-else-if="event.type === 'plan'" class="bg-blue-500/10 border border-blue-500/20 rounded p-3">
          <h4 class="text-sm font-medium text-blue-400 mb-2">Execution Plan</h4>
          <div v-html="formatContent(event.content)"></div>
        </div>
        
        <!-- Step -->
        <div v-else-if="event.type === 'step'" class="bg-yellow-500/10 border border-yellow-500/20 rounded p-3">
          <div class="flex items-center space-x-2 mb-2">
            <div 
              class="w-3 h-3 rounded-full"
              :class="getStepStatusClass(event.metadata?.status)"
            ></div>
            <h4 class="text-sm font-medium">Step Update</h4>
          </div>
          <div v-html="formatContent(event.content)"></div>
        </div>
        
        <!-- Tool -->
        <div v-else-if="event.type === 'tool'" class="bg-green-500/10 border border-green-500/20 rounded p-3">
          <h4 class="text-sm font-medium text-green-400 mb-2">
            Tool: {{ event.metadata?.tool || 'Unknown' }}
          </h4>
          <div v-html="formatContent(event.content)"></div>
        </div>
        
        <!-- Error -->
        <div v-else-if="event.type === 'error'" class="bg-red-500/10 border border-red-500/20 rounded p-3">
          <h4 class="text-sm font-medium text-red-400 mb-2">Error</h4>
          <div v-html="formatContent(event.content)"></div>
        </div>
        
        <!-- Default -->
        <div v-else v-html="formatContent(event.content)"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import type { ChatEvent } from '../types/session'

defineProps<{
  event: ChatEvent
}>()

const getMessageClass = () => {
  return 'bg-secondary/50 border border-border'
}

const getAvatarClass = () => {
  return 'bg-primary text-primary-foreground'
}

const getContentClass = () => {
  return 'text-foreground prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-code:text-foreground prose-pre:bg-secondary prose-pre:text-foreground'
}

const getStepStatusClass = (status?: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-500'
    case 'running':
      return 'bg-yellow-500 animate-pulse'
    case 'failed':
      return 'bg-red-500'
    default:
      return 'bg-gray-500'
  }
}

const formatContent = (content: string) => {
  if (!content) return ''
  
  // Convert markdown to HTML
  const html = marked(content, {
    breaks: true,
    gfm: true
  })
  
  return html
}

const formatTime = (timestamp: number) => {
  return new Date(timestamp).toLocaleTimeString()
}
</script>
