import { getDisplayDownloadCount } from '../lib/redis'
import { HeroClient } from './components/HeroClient'
import { Features } from './components/Features'
import { Footer } from './components/Footer'

// Force dynamic rendering
export const dynamic = 'force-dynamic'

export default async function Home() {
  // Get display count (real downloads + fake inflated)
  const downloadCount = await getDisplayDownloadCount()
  
  return (
    <div className="min-h-screen bg-[#FAFBFC] text-[#1A1A1A]">
      <HeroClient initialDownloadCount={downloadCount} />
      <Features />
      <Footer />
    </div>
  )
}
