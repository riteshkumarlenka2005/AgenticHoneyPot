"use client";

import { useEffect, useState } from "react";

interface Persona {
  id: string;
  name: string;
  age: number;
  occupation: string;
  location: string;
  communication_style: string;
  traits: Record<string, unknown>;
  backstory: Record<string, unknown>;
  is_active: boolean;
}

export default function PersonasPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingPersona, setEditingPersona] = useState<Persona | null>(null);

  useEffect(() => {
    fetchPersonas();
  }, []);

  const fetchPersonas = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/personas`);
      
      if (response.ok) {
        const data = await response.json();
        setPersonas(data);
      }
    } catch (err) {
      console.error("Failed to fetch personas:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (persona: Persona) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/personas/${persona.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !persona.is_active })
      });
      
      if (response.ok) {
        fetchPersonas();
      }
    } catch (err) {
      console.error("Failed to toggle persona:", err);
    }
  };

  const handleDelete = async (personaId: string) => {
    if (!confirm("Are you sure you want to delete this persona?")) {
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/v1/personas/${personaId}`, {
        method: "DELETE"
      });
      
      if (response.ok) {
        fetchPersonas();
      }
    } catch (err) {
      console.error("Failed to delete persona:", err);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-gray-200 rounded mb-4"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Persona Management</h1>
          <p className="text-gray-600">Manage AI personas for honeypot interactions</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium"
        >
          + Create Persona
        </button>
      </div>

      {/* Personas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {personas.map((persona) => (
          <div
            key={persona.id}
            className={`bg-white rounded-lg shadow-md p-6 border-2 ${
              persona.is_active ? "border-green-500" : "border-gray-200"
            }`}
          >
            {/* Status Badge */}
            <div className="flex justify-between items-start mb-4">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                persona.is_active
                  ? "bg-green-100 text-green-800"
                  : "bg-gray-100 text-gray-800"
              }`}>
                {persona.is_active ? "Active" : "Inactive"}
              </span>
            </div>

            {/* Persona Info */}
            <h3 className="text-xl font-bold mb-2">{persona.name}</h3>
            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Age:</span> {persona.age}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Occupation:</span> {persona.occupation}
              </p>
              <p className="text-sm text-gray-600">
                <span className="font-medium">Location:</span> {persona.location}
              </p>
            </div>

            {/* Communication Style */}
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-1">Communication Style:</p>
              <p className="text-sm text-gray-700 line-clamp-2">
                {persona.communication_style}
              </p>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <button
                onClick={() => handleToggleActive(persona)}
                className={`flex-1 px-4 py-2 rounded font-medium ${
                  persona.is_active
                    ? "bg-gray-200 hover:bg-gray-300 text-gray-800"
                    : "bg-green-600 hover:bg-green-700 text-white"
                }`}
              >
                {persona.is_active ? "Deactivate" : "Activate"}
              </button>
              <button
                onClick={() => setEditingPersona(persona)}
                className="px-4 py-2 bg-blue-100 hover:bg-blue-200 text-blue-800 rounded font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(persona.id)}
                className="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {personas.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">No personas created yet</p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium"
          >
            Create Your First Persona
          </button>
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreateForm || editingPersona) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
            <h2 className="text-2xl font-bold mb-6">
              {editingPersona ? "Edit Persona" : "Create New Persona"}
            </h2>
            
            <form onSubmit={(e) => {
              e.preventDefault();
              // Form submission logic would go here
              setShowCreateForm(false);
              setEditingPersona(null);
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border rounded-lg"
                    defaultValue={editingPersona?.name}
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Age</label>
                    <input
                      type="number"
                      className="w-full px-4 py-2 border rounded-lg"
                      defaultValue={editingPersona?.age}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Occupation</label>
                    <input
                      type="text"
                      className="w-full px-4 py-2 border rounded-lg"
                      defaultValue={editingPersona?.occupation}
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Location</label>
                  <input
                    type="text"
                    className="w-full px-4 py-2 border rounded-lg"
                    defaultValue={editingPersona?.location}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Communication Style</label>
                  <textarea
                    className="w-full px-4 py-2 border rounded-lg"
                    rows={3}
                    defaultValue={editingPersona?.communication_style}
                    required
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    className="mr-2"
                    defaultChecked={editingPersona?.is_active ?? true}
                  />
                  <label htmlFor="is_active" className="text-sm font-medium">
                    Active
                  </label>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium"
                >
                  {editingPersona ? "Update Persona" : "Create Persona"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setEditingPersona(null);
                  }}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
