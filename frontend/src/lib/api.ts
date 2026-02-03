const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1 = `${API_BASE_URL}/api/v1`

export const api = {
  async get(endpoint: string, raw = false) {
    const response = await fetch(`${API_V1}${endpoint}`)
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }
    return raw ? response.text() : response.json()
  },

  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }
    return response.json()
  },

  async delete(endpoint: string) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'DELETE',
    })
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }
    return response.json()
  },
}
