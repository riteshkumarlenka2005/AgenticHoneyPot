'use client'

const steps = [
  {
    number: '01',
    title: 'Scammer Reaches Out',
    description: 'A scammer sends a message through SMS, email, or messaging platform trying to initiate a scam.',
  },
  {
    number: '02',
    title: 'AI Detection',
    description: 'Our AI instantly analyzes the message content, patterns, and context to detect scam indicators.',
  },
  {
    number: '03',
    title: 'Persona Generation',
    description: 'The system generates a believable persona tailored to the scam type to keep the scammer engaged.',
  },
  {
    number: '04',
    title: 'Intelligence Extraction',
    description: 'As the conversation progresses, we extract and catalog valuable intelligence about the scammer.',
  },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 sm:py-32 bg-muted/20">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Our automated system handles everything from detection to intelligence gathering
          </p>
        </div>

        {/* Steps */}
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            {/* Connecting line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-border hidden md:block"></div>

            <div className="space-y-12">
              {steps.map((step, index) => (
                <div key={index} className="relative flex gap-8 items-start">
                  {/* Step number */}
                  <div className="flex-shrink-0 w-16 h-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold z-10">
                    {step.number}
                  </div>

                  {/* Step content */}
                  <div className="flex-1 pb-8">
                    <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                    <p className="text-muted-foreground">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
