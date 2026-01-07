import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Tempo - Run Claude Code Overnight',
  description: 'Automated Claude Code runner with rate limit handling. Start a task, go to sleep, wake up to results.',
  keywords: ['claude', 'claude code', 'automation', 'ai', 'coding', 'developer tools'],
  authors: [{ name: 'Tempo' }],
  icons: {
    icon: '/iconlogo.png',
    apple: '/iconlogo.png',
  },
  openGraph: {
    title: 'Tempo - Run Claude Code Overnight',
    description: 'Automated Claude Code runner with rate limit handling.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}

