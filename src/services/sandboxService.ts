const SANDBOX_API_BASE = "/api/v1"

interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

export const sandboxService = {
  // Shell operations
  async executeShell(params: {
    id?: string
    exec_dir?: string
    command: string
  }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/shell/exec`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async viewShell(sessionId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/shell/view`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id: sessionId }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async waitForProcess(sessionId: string, seconds?: number): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/shell/wait`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id: sessionId, seconds }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async writeInput(sessionId: string, input: string, pressEnter = true): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/shell/write`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id: sessionId,
        input,
        press_enter: pressEnter,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async killProcess(sessionId: string): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/shell/kill`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id: sessionId }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  // File operations
  async readFile(params: {
    file: string
    start_line?: number
    end_line?: number
    sudo?: boolean
  }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/file/read`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async writeFile(params: {
    file: string
    content: string
    append?: boolean
    leading_newline?: boolean
    trailing_newline?: boolean
    sudo?: boolean
  }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/file/write`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async replaceInFile(params: {
    file: string
    old_str: string
    new_str: string
    sudo?: boolean
  }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/file/replace`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async searchFile(params: {
    file: string
    regex: string
    sudo?: boolean
  }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/file/search`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async findFiles(params: {
    path: string
    glob: string
  }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/file/find`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  // System operations
  async getSystemStatus(): Promise<ApiResponse<any[]>> {
    const response = await fetch(`${SANDBOX_API_BASE}/supervisor/status`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async stopServices(): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/supervisor/stop`, {
      method: "POST",
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async restartServices(): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/supervisor/restart`, {
      method: "POST",
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },

  async extendTimeout(params: { minutes?: number }): Promise<ApiResponse<any>> {
    const response = await fetch(`${SANDBOX_API_BASE}/supervisor/timeout/extend`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.json()
  },
}
