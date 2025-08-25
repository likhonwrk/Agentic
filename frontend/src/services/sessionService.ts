import type { Session } from "../types/session"

const API_BASE = "/api/v1"

interface ApiResponse<T> {
  code: number
  msg: string
  data: T
}

export const sessionService = {
  async createSession(): Promise<ApiResponse<{ session_id: string }>> {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async getSession(sessionId: string): Promise<ApiResponse<Session>> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async listSessions(): Promise<ApiResponse<{ sessions: Session[] }>> {
    const response = await fetch(`${API_BASE}/sessions`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async deleteSession(sessionId: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: "DELETE",
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async stopSession(sessionId: string): Promise<ApiResponse<null>> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/stop`, {
      method: "POST",
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async sendMessage(sessionId: string, message: string): Promise<Response> {
    return fetch(`${API_BASE}/sessions/${sessionId}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        timestamp: Date.now(),
      }),
    })
  },

  async viewShell(sessionId: string, shellSessionId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/shell`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: shellSessionId,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async viewFile(sessionId: string, filePath: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/file`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file: filePath,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },
}
