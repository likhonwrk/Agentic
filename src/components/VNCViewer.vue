<template>
  <div class="relative w-full h-full bg-black">
    <!-- VNC Canvas Container -->
    <div ref="vncContainer" class="w-full h-full">
      <canvas
        ref="vncCanvas"
        class="w-full h-full cursor-crosshair"
        @mousedown="handleMouseDown"
        @mouseup="handleMouseUp"
        @mousemove="handleMouseMove"
        @wheel="handleWheel"
        @contextmenu.prevent
      ></canvas>
    </div>

    <!-- Connection Status -->
    <div 
      v-if="connectionStatus !== 'connected'"
      class="absolute inset-0 flex items-center justify-center bg-black/80"
    >
      <div class="text-center text-white">
        <div v-if="connectionStatus === 'connecting'" class="space-y-3">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto"></div>
          <p>Connecting to VNC...</p>
        </div>
        <div v-else-if="connectionStatus === 'disconnected'" class="space-y-3">
          <svg class="w-8 h-8 mx-auto text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p>VNC Connection Failed</p>
          <button 
            @click="connect"
            class="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
          >
            Retry Connection
          </button>
        </div>
        <div v-else-if="connectionStatus === 'error'" class="space-y-3">
          <svg class="w-8 h-8 mx-auto text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>{{ errorMessage }}</p>
          <button 
            @click="connect"
            class="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="absolute top-2 right-2 flex space-x-2">
      <button
        @click="toggleFullscreen"
        class="p-2 bg-black/50 text-white rounded hover:bg-black/70 transition-colors"
        title="Toggle Fullscreen"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
      </button>
      <button
        @click="disconnect"
        class="p-2 bg-black/50 text-white rounded hover:bg-black/70 transition-colors"
        title="Disconnect"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  sessionId: string
}>()

// State
const vncContainer = ref<HTMLElement>()
const vncCanvas = ref<HTMLCanvasElement>()
const connectionStatus = ref<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
const errorMessage = ref('')
const websocket = ref<WebSocket | null>(null)
const canvasContext = ref<CanvasRenderingContext2D | null>(null)

// Methods
const connect = async () => {
  if (connectionStatus.value === 'connecting' || connectionStatus.value === 'connected') {
    return
  }

  connectionStatus.value = 'connecting'
  errorMessage.value = ''

  try {
    // Establish WebSocket connection to VNC
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/sessions/${props.sessionId}/vnc`
    
    websocket.value = new WebSocket(wsUrl, ['binary'])
    websocket.value.binaryType = 'arraybuffer'

    websocket.value.onopen = () => {
      connectionStatus.value = 'connected'
      console.log('[v0] VNC WebSocket connected')
    }

    websocket.value.onmessage = (event) => {
      handleVNCMessage(event.data)
    }

    websocket.value.onclose = () => {
      connectionStatus.value = 'disconnected'
      console.log('[v0] VNC WebSocket disconnected')
    }

    websocket.value.onerror = (error) => {
      connectionStatus.value = 'error'
      errorMessage.value = 'WebSocket connection failed'
      console.error('[v0] VNC WebSocket error:', error)
    }

  } catch (error) {
    connectionStatus.value = 'error'
    errorMessage.value = 'Failed to establish VNC connection'
    console.error('[v0] VNC connection error:', error)
  }
}

const disconnect = () => {
  if (websocket.value) {
    websocket.value.close()
    websocket.value = null
  }
  connectionStatus.value = 'disconnected'
}

const handleVNCMessage = (data: ArrayBuffer) => {
  if (!canvasContext.value) return

  try {
    // This is a simplified VNC message handler
    // In a real implementation, you would need to parse VNC protocol messages
    // and render the framebuffer updates to the canvas
    
    // For now, we'll just log that we received data
    console.log('[v0] Received VNC data:', data.byteLength, 'bytes')
    
    // You would implement VNC protocol parsing here:
    // - Handle server initialization
    // - Process framebuffer updates
    // - Handle color map updates
    // - etc.
    
  } catch (error) {
    console.error('[v0] Error handling VNC message:', error)
  }
}

const sendVNCMessage = (data: ArrayBuffer) => {
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    websocket.value.send(data)
  }
}

const handleMouseDown = (event: MouseEvent) => {
  if (connectionStatus.value !== 'connected') return
  
  const rect = vncCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = Math.floor((event.clientX - rect.left) * (vncCanvas.value?.width || 0) / rect.width)
  const y = Math.floor((event.clientY - rect.top) * (vncCanvas.value?.height || 0) / rect.height)
  
  // Send mouse down event to VNC server
  // This would need to be formatted according to VNC protocol
  console.log('[v0] Mouse down at:', x, y, 'button:', event.button)
}

const handleMouseUp = (event: MouseEvent) => {
  if (connectionStatus.value !== 'connected') return
  
  const rect = vncCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = Math.floor((event.clientX - rect.left) * (vncCanvas.value?.width || 0) / rect.width)
  const y = Math.floor((event.clientY - rect.top) * (vncCanvas.value?.height || 0) / rect.height)
  
  // Send mouse up event to VNC server
  console.log('[v0] Mouse up at:', x, y, 'button:', event.button)
}

const handleMouseMove = (event: MouseEvent) => {
  if (connectionStatus.value !== 'connected') return
  
  const rect = vncCanvas.value?.getBoundingClientRect()
  if (!rect) return

  const x = Math.floor((event.clientX - rect.left) * (vncCanvas.value?.width || 0) / rect.width)
  const y = Math.floor((event.clientY - rect.top) * (vncCanvas.value?.height || 0) / rect.height)
  
  // Send mouse move event to VNC server (throttled)
  // console.log('[v0] Mouse move to:', x, y)
}

const handleWheel = (event: WheelEvent) => {
  if (connectionStatus.value !== 'connected') return
  
  event.preventDefault()
  
  // Send wheel event to VNC server
  console.log('[v0] Wheel event:', event.deltaY)
}

const toggleFullscreen = () => {
  if (!vncContainer.value) return
  
  if (document.fullscreenElement) {
    document.exitFullscreen()
  } else {
    vncContainer.value.requestFullscreen()
  }
}

// Lifecycle
onMounted(() => {
  if (vncCanvas.value) {
    canvasContext.value = vncCanvas.value.getContext('2d')
    // Set default canvas size
    vncCanvas.value.width = 1024
    vncCanvas.value.height = 768
  }
  
  // Auto-connect when component mounts
  connect()
})

onUnmounted(() => {
  disconnect()
})
</script>
