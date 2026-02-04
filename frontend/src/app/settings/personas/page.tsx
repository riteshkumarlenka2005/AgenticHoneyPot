'use client'

import { useEffect, useState } from 'react'
import { Sidebar } from '@/components/ui/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Plus, Edit, Trash2, CheckCircle, XCircle } from 'lucide-react'

interface Persona {
  id: string
  name: string
  age: number
  occupation: string
  location: string
  is_active: boolean
  communication_style: string
}

export default function PersonasPage() {
  const [personas, setPersonas] = useState<Persona[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadPersonas()
  }, [])

  const loadPersonas = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/personas')
      const data = await res.json()
      setPersonas(data || [])
      setLoading(false)
    } catch (error) {
      console.error('Error loading personas:', error)
      setLoading(false)
    }
  }

  const toggleActive = async (id: string, isActive: boolean) => {
    try {
      await fetch(`http://localhost:8000/api/v1/personas/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !isActive })
      })
      loadPersonas()
    } catch (error) {
      console.error('Error updating persona:', error)
    }
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Persona Management</h1>
              <p className="text-muted-foreground">
                Manage honeypot personas for scammer engagement
              </p>
            </div>
            
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Persona
            </Button>
          </div>

          {loading ? (
            <div className="text-center py-12">Loading personas...</div>
          ) : personas.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <p className="text-muted-foreground">
                  No personas found. Create your first persona to start engaging scammers.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {personas.map((persona) => (
                <Card key={persona.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div>
                        <CardTitle>{persona.name}</CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                          {persona.age} years • {persona.occupation}
                        </p>
                      </div>
                      <Badge variant={persona.is_active ? 'default' : 'secondary'}>
                        {persona.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-muted-foreground">Location</div>
                        <div className="text-sm font-medium">{persona.location}</div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-muted-foreground">Communication Style</div>
                        <div className="text-sm">{persona.communication_style.slice(0, 100)}...</div>
                      </div>

                      <div className="flex gap-2 pt-4">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleActive(persona.id, persona.is_active)}
                        >
                          {persona.is_active ? (
                            <>
                              <XCircle className="h-4 w-4 mr-1" />
                              Deactivate
                            </>
                          ) : (
                            <>
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Activate
                            </>
                          )}
                        </Button>
                        <Button size="sm" variant="outline">
                          <Edit className="h-4 w-4 mr-1" />
                          Edit
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="h-4 w-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
