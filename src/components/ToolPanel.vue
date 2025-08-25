<template>
  <div class="flex flex-col h-full bg-secondary/10">
    <!-- Header -->
    <div class="p-4 border-b border-border">
      <h3 class="font-semibold mb-3">Tools & Monitoring</h3>
      <div class="flex space-x-1">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-3 py-1 text-sm rounded-md transition-colors"
          :class="activeTab === tab.id ? 'bg-primary text-primary-foreground' : 'hover:bg-secondary'"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-hidden">
      <!-- Shell Tab -->
      <div v-if="activeTab === 'shell'" class="h-full flex flex-col">
        <div class="p-3 border-b border-border">
          <div class="flex space-x-2">
            <input
              v-model="shellCommand"
              @keydown.enter="executeShellCommand"
              placeholder="Enter shell command..."
              class="flex-1 px-3 py-1 text-sm bg-background border border-border rounded"
            />
            <button
              @click="executeShellCommand"
              class="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Run
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto p-3">
          <div class="font-mono text-sm space-y-2">
            <div v-for="(entry, index) in shellHistory" :key="index" class="space-y-1">
              <div class="text-green-400">{{ entry.ps1 }}</div>
              <div class="text-blue-400">{{ entry.command }}</div>
              <pre class="text-foreground whitespace-pre-wrap">{{ entry.output }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Files Tab -->
      <div v-else-if="activeTab === 'files'" class="h-full flex flex-col">
        <div class="p-3 border-b border-border">
          <div class="flex space-x-2">
            <input
              v-model="filePath"
              placeholder="Enter file path..."
              class="flex-1 px-3 py-1 text-sm bg-background border border-border rounded"
            />
            <button
              @click="readFile"
              class="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Read
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto p-3">
          <div v-if="fileContent" class="space-y-3">
            <div class="text-sm text-muted-foreground">{{ currentFile }}</div>
            <pre class="font-mono text-sm bg-background border border-border rounded p-3 overflow-x-auto">{{ fileContent }}</pre>
          </div>
          <div v-else class="text-center text-muted-foreground py-8">
            Enter a file path to read its contents
          </div>
        </div>
      </div>

      <!-- Browser Tab -->
      <div v-else-if="activeTab === 'browser'" class="h-full flex flex-col">
        <div class="p-3 border-b border-border">
          <div class="flex space-x-2">
            <input
              v-model="browserUrl"
              placeholder="Enter URL..."
              class="flex-1 px-3 py-1 text-sm bg-background border border-border rounded"
            />
            <button
              @click="navigateBrowser"
              class="px-3 py-1 text-sm bg-primary text-primary-foreground rounded hover:bg-primary/90"
            >
              Go
            </button>
          </div>
        </div>
        <div class="flex-1 p-3">
          <div class="text-center text-muted-foreground py-8">
            Browser automation controls
            <br />
            <small>Use VNC viewer to see browser output</small>
          </div>
        </div>
      </div>

      <!-- System Tab -->
      <div v-else-if="activeTab === 'system'" class="h-full flex flex-col">
        <div class="flex-1 overflow-y-auto p-3 space-y-4">
          <div>
            <h4 class="font-medium mb-2">System Status</h4>
            <div class="space-y-2">
              <div v-for="service in systemStatus" :key="service.name" class="flex justify-between items-center p-2 bg-background rounded">
                <span class="text-sm">{{ service.name }}</span>
                <span 
                  class="px-2 py-1 text-xs rounded-full"
                  :class="service.status === 'RUNNING' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'"
                >
                  {{ service.status }}
                </span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 class="font-medium mb-2">Actions</h4>
            <div class="space-y-2">
              <button
                @click="restartServices"
                class="w-full px-3 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded transition-colors"
              >
                Restart Services
              </button>
              <button
                @click="extendTimeout"
                class="w-full px-3 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded transition-colors"
              >
                Extend Timeout
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { sandboxService } from '../services/sandboxService'

defineProps<{
  sessionId: string
}>()

const emit = defineEmits<{
  'tool-action': [action: any]
}>()

// State
const activeTab = ref('shell')
const shellCommand = ref('')
const shellHistory = ref<any[]>([])
const filePath = ref('')
const fileContent = ref('')
const currentFile = ref('')
const browserUrl = ref('')
const systemStatus = ref<any[]>([])

const tabs = [
  { id: 'shell', label: 'Shell' },
  { id: 'files', label: 'Files' },
  { id: 'browser', label: 'Browser' },
  { id: 'system', label: 'System' }
]

// Methods
const executeShellCommand = async () => {
  if (!shellCommand.value.trim()) return
  
  try {
    const response = await sandboxService.executeShell({
      command: shellCommand.value
    })
    
    // Add to history
    shellHistory.value.push({
      ps1: 'user@sandbox:~$',
      command: shellCommand.value,
      output: response.data.output || 'Command executed'
    })
    
    shellCommand.value = ''
    emit('tool-action', { type: 'shell', command: shellCommand.value })
  } catch (error) {
    console.error('Shell command failed:', error)
  }
}

const readFile = async () => {
  if (!filePath.value.trim()) return
  
  try {
    const response = await sandboxService.readFile({
      file: filePath.value
    })
    
    fileContent.value = response.data.content
    currentFile.value = filePath.value
    emit('tool-action', { type: 'file', action: 'read', file: filePath.value })
  } catch (error) {
    console.error('File read failed:', error)
  }
}

const navigateBrowser = async () => {
  if (!browserUrl.value.trim()) return
  
  try {
    // Browser navigation would be handled by the browser automation service
    emit('tool-action', { type: 'browser', action: 'navigate', url: browserUrl.value })
  } catch (error) {
    console.error('Browser navigation failed:', error)
  }
}

const loadSystemStatus = async () => {
  try {
    const response = await sandboxService.getSystemStatus()
    systemStatus.value = response.data || []
  } catch (error) {
    console.error('Failed to load system status:', error)
  }
}

const restartServices = async () => {
  try {
    await sandboxService.restartServices()
    await loadSystemStatus()
    emit('tool-action', { type: 'system', action: 'restart' })
  } catch (error) {
    console.error('Failed to restart services:', error)
  }
}

const extendTimeout = async () => {
  try {
    await sandboxService.extendTimeout({ minutes: 30 })
    emit('tool-action', { type: 'system', action: 'extend_timeout' })
  } catch (error) {
    console.error('Failed to extend timeout:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadSystemStatus()
})
</script>
