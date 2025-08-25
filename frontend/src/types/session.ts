export interface Session {
  session_id: string
  title?: string
  latest_message?: string
  latest_message_at?: number
  status: string
  unread_message_count: number
  events: ChatEvent[]
}

export interface ChatEvent {
  id?: string
  type: "message" | "title" | "plan" | "step" | "tool" | "error" | "done"
  content: string
  timestamp: number
  sender: "user" | "assistant"
  metadata?: {
    status?: string
    tool?: string
    action?: string
    [key: string]: any
  }
}

export interface ShellSession {
  session_id: string
  output: string
  console: Array<{
    ps1: string
    command: string
    output: string
  }>
}

export interface FileContent {
  content: string
  line_count: number
  file: string
}

export interface SystemService {
  name: string
  status: string
  description: string
}
