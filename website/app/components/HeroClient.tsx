'use client'

import { useState, useEffect } from 'react'
import { Copy, Check } from 'lucide-react'

type Platform = 'macos' | 'linux' | 'windows'

// Logo component with fixed dimensions to prevent layout shift
function Logo() {
  return (
    <img 
      src="/logo.png" 
      alt="Tempo logo" 
      width={160}
      height={160}
      className="w-32 h-32 md:w-40 md:h-40 object-contain"
      loading="eager"
    />
  )
}

interface HeroClientProps {
  initialDownloadCount: number
}

export function HeroClient({ initialDownloadCount }: HeroClientProps) {
  const [copied, setCopied] = useState(false)
  const [platform, setPlatform] = useState<Platform>('macos')

  // Auto-detect platform on mount
  useEffect(() => {
    const userAgent = navigator.userAgent.toLowerCase()
    if (userAgent.includes('win')) setPlatform('windows')
    else if (userAgent.includes('linux')) setPlatform('linux')
    else setPlatform('macos')
  }, [])

  const commands = {
    macos: 'curl -fsSL https://raw.githubusercontent.com/tomalmog/tempo/main/install.sh | bash',
    linux: 'curl -fsSL https://raw.githubusercontent.com/tomalmog/tempo/main/install.sh | bash',
    windows: 'irm https://raw.githubusercontent.com/tomalmog/tempo/main/install.ps1 | iex',
  }

  const altCommands = {
    macos: null,
    linux: null,
    windows: 'curl -fsSL https://raw.githubusercontent.com/tomalmog/tempo/main/install.cmd -o install.cmd && install.cmd',
  }

  // Raw GitHub URLs
  const rawDownloadUrls = {
    macos: {
      arm64: 'https://github.com/tomalmog/tempo/releases/latest/download/tempo-macos-arm64',
      x64: 'https://github.com/tomalmog/tempo/releases/latest/download/tempo-macos-x64',
    },
    linux: {
      x64: 'https://github.com/tomalmog/tempo/releases/latest/download/tempo-linux-x64',
      arm64: 'https://github.com/tomalmog/tempo/releases/latest/download/tempo-linux-arm64',
    },
    windows: {
      x64: 'https://github.com/tomalmog/tempo/releases/latest/download/tempo-windows-x64.exe',
    },
  }

  // Tracked download URLs (go through our API to increment counter)
  const trackUrl = (url: string) => `/api/downloads/track?url=${encodeURIComponent(url)}`
  
  const downloadUrls = {
    macos: {
      arm64: trackUrl(rawDownloadUrls.macos.arm64),
      x64: trackUrl(rawDownloadUrls.macos.x64),
    },
    linux: {
      x64: trackUrl(rawDownloadUrls.linux.x64),
      arm64: trackUrl(rawDownloadUrls.linux.arm64),
    },
    windows: {
      x64: trackUrl(rawDownloadUrls.windows.x64),
    },
  }

  const platformLabels = {
    macos: 'macOS',
    linux: 'Linux',
    windows: 'Windows',
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="relative flex flex-col items-center justify-center px-6 pt-24 pb-20 md:pt-32 md:pb-24 overflow-hidden">
      {/* Subtle background pattern */}
      <div 
        className="absolute inset-0 opacity-[0.03]" 
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, #2563EB 1px, transparent 0)`,
          backgroundSize: '40px 40px'
        }}
      />
      
      <div className="max-w-[700px] w-full text-center relative z-10">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Logo />
        </div>

        {/* App Name */}
        <h1 className="text-5xl md:text-6xl font-semibold mb-6 tracking-tight text-[#1A1A1A]">
          Tempo
        </h1>

        {/* Tagline */}
        <p className="text-xl md:text-2xl text-[#6B7280] mb-6 leading-relaxed">
          Run Claude Code overnight, automatically
        </p>

        {/* Description */}
        <p className="text-base md:text-lg text-[#6B7280] mb-12 max-w-[550px] mx-auto leading-relaxed">
          Tempo handles rate limits and waits for credit resets, so your tasks continue running while you sleep—no intervention needed.
        </p>

        {/* Platform Selector */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex bg-[#F3F4F6] rounded-lg p-1">
            {(Object.keys(platformLabels) as Platform[]).map((key) => (
              <button
                key={key}
                onClick={() => setPlatform(key)}
                className={`px-6 py-2 rounded-md text-sm font-medium transition-all ${
                  platform === key
                    ? 'bg-white text-[#1A1A1A] shadow-sm'
                    : 'text-[#6B7280] hover:text-[#1A1A1A]'
                }`}
              >
                {platformLabels[key]}
              </button>
            ))}
          </div>
        </div>

        {/* Command */}
        <div className="max-w-[600px] mx-auto mb-8">
          <div className="relative group">
            <div className="bg-[#F9FAFB] border border-[#E5E7EB] rounded-lg p-4 pr-14 overflow-x-auto">
              <code className="font-mono text-sm text-[#1A1A1A]">
                {commands[platform]}
              </code>
            </div>
            <button
              onClick={() => copyToClipboard(commands[platform])}
              className="absolute top-3 right-3 p-2 rounded-md hover:bg-[#E5E7EB] transition-colors"
              aria-label="Copy to clipboard"
            >
              {copied ? (
                <Check className="w-4 h-4 text-[#2563EB]" />
              ) : (
                <Copy className="w-4 h-4 text-[#6B7280]" />
              )}
            </button>
          </div>
        </div>

        {/* Alternative install methods */}
        <div className="max-w-[600px] mx-auto mb-6">
          <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-2 text-sm text-[#6B7280]">
            {/* Download binary links */}
            {platform === 'macos' && (
              <>
                <a href={downloadUrls.macos.arm64} className="hover:text-[#1A1A1A] transition-colors">
                  Download (Apple Silicon)
                </a>
                <span className="text-[#E5E7EB]">·</span>
                <a href={downloadUrls.macos.x64} className="hover:text-[#1A1A1A] transition-colors">
                  Download (Intel)
                </a>
              </>
            )}
            {platform === 'linux' && (
              <>
                <a href={downloadUrls.linux.x64} className="hover:text-[#1A1A1A] transition-colors">
                  Download (x64)
                </a>
                <span className="text-[#E5E7EB]">·</span>
                <a href={downloadUrls.linux.arm64} className="hover:text-[#1A1A1A] transition-colors">
                  Download (ARM64)
                </a>
              </>
            )}
            {platform === 'windows' && (
              <a href={downloadUrls.windows.x64} className="hover:text-[#1A1A1A] transition-colors">
                Download binary
              </a>
            )}
            {platform === 'windows' && (
              <>
                <span className="text-[#E5E7EB]">·</span>
                <span className="text-[#9CA3AF] text-xs" title={altCommands.windows || ''}>
                  or use CMD
                </span>
              </>
            )}
          </div>
        </div>

        {/* Links */}
        <div className="flex items-center justify-center gap-6 text-sm">
          <a 
            href="https://github.com/tomalmog/tempo" 
            className="text-[#2563EB] hover:text-[#1d4ed8] transition-colors font-medium"
          >
            View on GitHub →
          </a>
        </div>

        {/* Download counter - passed from server, no flash! */}
        <p className="text-sm text-[#9CA3AF] mt-8">
          {initialDownloadCount.toLocaleString()} downloads
        </p>
      </div>
    </section>
  )
}

