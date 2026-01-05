export function Features() {
  const features = [
    {
      title: 'Automatic Rate Limit Handling',
      description: 'Detects when Claude hits rate limits and intelligently waits for credit resets.',
    },
    {
      title: 'Unattended Operation',
      description: 'Start a task before bed and wake up to completed work. No need to babysit the process.',
    },
    {
      title: 'Simple & Lightweight',
      description: 'Just a small utility that does one thing well. No bloat, no complexity.',
    },
  ]

  return (
    <section className="py-16 md:py-20 px-6 bg-[#F9FAFB]">
      <div className="max-w-[900px] mx-auto">
        <div className="grid md:grid-cols-3 gap-10 md:gap-12">
          {features.map((feature, index) => (
            <div key={index} className="text-center md:text-left">
              <h3 className="text-lg font-semibold mb-3 text-[#1A1A1A]">
                {feature.title}
              </h3>
              <p className="text-[#6B7280] leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

