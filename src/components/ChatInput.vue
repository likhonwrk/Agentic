<template>
  <div class="space-y-3">
    <!-- File Upload Area -->
    <div 
      v-if="dragOver"
      @drop="handleDrop"
      @dragover.prevent
      @dragleave="dragOver = false"
      class="border-2 border-dashed border-primary rounded-lg p-4 text-center"
    >
      <p class="text-primary">Drop files here to upload</p>
    </div>

    <!-- Input Area -->
    <div class="flex items-end space-x-3">
      <!-- Text Input -->
      <div class="flex-1 relative">
        <textarea
          ref="textareaRef"
          v-model="message"
          @keydown="handleKeydown"
          @input="adjustHeight"
          :disabled="disabled"
          placeholder="Type your message... (Shift+Enter for new line, Enter to send)"
          class="w-full min-h-[44px] max-h-32 px-4 py-3 pr-12 bg-secondary border border-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          rows="1"
        ></textarea>
        
        <!-- File Upload Button -->
        <button
          @click="triggerFileUpload"
          :disabled="disabled"
          class="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button>
      </div>

      <!-- Action Buttons -->
      <div class="flex space-x-2">
        <button
          v-if="sessionActive"
          @click="$emit('session-stop')"
          class="px-4 py-3 bg-destructive text-destructive-foreground rounded-lg hover:bg-destructive/90 transition-colors flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10h6v4H9z" />
          </svg>
          <span>Stop</span>
        </button>
        
        <button
          @click="sendMessage"
          :disabled="disabled || !message.trim()"
          class="px-4 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          <span>Send</span>
        </button>
      </div>
    </div>

    <!-- Uploaded Files -->
    <div v-if="uploadedFiles.length > 0" class="flex flex-wrap gap-2">
      <div 
        v-for="(file, index) in uploadedFiles" 
        :key="index"
        class="flex items-center space-x-2 px-3 py-1 bg-secondary rounded-full text-sm"
      >
        <span>{{ file.name }}</span>
        <button 
          @click="removeFile(index)"
          class="text-muted-foreground hover:text-destructive"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInputRef"
      type="file"
      multiple
      @change="handleFileSelect"
      class="hidden"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

defineProps<{
  disabled?: boolean
  sessionActive?: boolean
}>()

const emit = defineEmits<{
  'message-send': [message: string]
  'session-stop': []
}>()

// State
const message = ref('')
const uploadedFiles = ref<File[]>([])
const dragOver = ref(false)
const textareaRef = ref<HTMLTextAreaElement>()
const fileInputRef = ref<HTMLInputElement>()

// Methods
const sendMessage = () => {
  if (!message.value.trim()) return
  
  emit('message-send', message.value.trim())
  message.value = ''
  uploadedFiles.value = []
  
  nextTick(() => {
    adjustHeight()
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const adjustHeight = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
}

const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    uploadedFiles.value.push(...Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
  
  if (event.dataTransfer?.files) {
    uploadedFiles.value.push(...Array.from(event.dataTransfer.files))
  }
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

// Global drag events
document.addEventListener('dragover', (e) => {
  e.preventDefault()
  dragOver.value = true
})

document.addEventListener('dragleave', (e) => {
  if (!e.relatedTarget) {
    dragOver.value = false
  }
})
</script>
