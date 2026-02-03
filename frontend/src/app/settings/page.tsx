'use client'

export default function Settings() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Configure honeypot system settings
        </p>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-border">
        <h2 className="text-2xl font-bold mb-4">Detection Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Detection Sensitivity
            </label>
            <input
              type="range"
              min="0"
              max="100"
              defaultValue="60"
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground mt-1">
              <span>Low</span>
              <span>Medium</span>
              <span>High</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-border">
        <h2 className="text-2xl font-bold mb-4">Persona Configuration</h2>
        <p className="text-muted-foreground">
          Manage honeypot personas used for engaging scammers
        </p>
        <div className="mt-4">
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90">
            View Personas
          </button>
        </div>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-border">
        <h2 className="text-2xl font-bold mb-4">Safety Guardrails</h2>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-green-500">✓</span>
            <span>Never send real money</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-500">✓</span>
            <span>Never provide real personal information</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-500">✓</span>
            <span>Never click external links</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-green-500">✓</span>
            <span>Operate only in authorized environments</span>
          </div>
        </div>
      </div>
    </div>
  )
}
