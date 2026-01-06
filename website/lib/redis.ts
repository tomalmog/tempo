import { Redis } from '@upstash/redis'

export const REAL_DOWNLOAD_KEY = 'tempo_downloads_real'

// Launch date for fake downloads
const LAUNCH_DATE = new Date('2026-01-07T08:00:00Z') // Jan 7, 2026 morning
const FAKE_PER_HOUR = 5 // Average fake downloads per hour

// Create Redis client
function createRedisClient() {
  const url = process.env.KV_REST_API_URL
  const token = process.env.KV_REST_API_TOKEN
  
  if (!url || !token) {
    console.warn('Redis env vars not configured')
    return null
  }
  
  return new Redis({ url, token })
}

export const redis = createRedisClient()

// Pseudo-random number generator with seed (deterministic)
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 9999) * 10000
  return x - Math.floor(x)
}

// Calculate fake downloads up to current time
// This creates random-looking increments that are consistent
function calculateFakeDownloads(): number {
  const now = new Date()
  const msSinceLaunch = now.getTime() - LAUNCH_DATE.getTime()
  
  if (msSinceLaunch <= 0) return 0
  
  const hoursSinceLaunch = Math.floor(msSinceLaunch / (1000 * 60 * 60))
  let fakeTotal = 0
  
  // For each completed hour, add a pseudo-random number of downloads (3-7, avg 5)
  for (let hour = 0; hour < hoursSinceLaunch; hour++) {
    const rand = seededRandom(hour + 12345) // Seed with hour number
    const downloadsThisHour = Math.floor(rand * 5) + 3 // 3-7 downloads
    fakeTotal += downloadsThisHour
  }
  
  // For the current partial hour, add downloads proportionally with randomness
  const currentHourProgress = (msSinceLaunch % (1000 * 60 * 60)) / (1000 * 60 * 60)
  const currentHourSeed = hoursSinceLaunch + 12345
  const currentHourTotal = Math.floor(seededRandom(currentHourSeed) * 5) + 3
  
  // Spread downloads throughout the hour using deterministic "times"
  for (let i = 0; i < currentHourTotal; i++) {
    const downloadTime = seededRandom(currentHourSeed * 100 + i) // 0-1 within the hour
    if (downloadTime < currentHourProgress) {
      fakeTotal++
    }
  }
  
  return fakeTotal
}

// Get REAL download count (private - for admin only)
export async function getRealDownloadCount(): Promise<number> {
  if (!redis) return 0
  
  try {
    const count = await redis.get<number>(REAL_DOWNLOAD_KEY)
    return count ?? 0
  } catch (error) {
    console.error('Redis error:', error)
    return 0
  }
}

// Get DISPLAY download count (public - real + fake)
export async function getDisplayDownloadCount(): Promise<number> {
  const realCount = await getRealDownloadCount()
  const fakeCount = calculateFakeDownloads()
  return realCount + fakeCount
}

// Increment REAL download count (also increases display count since display = real + fake)
export async function incrementDownloadCount(): Promise<void> {
  if (!redis) return
  
  try {
    await redis.incr(REAL_DOWNLOAD_KEY)
  } catch (error) {
    console.error('Redis error:', error)
  }
}

// Set real download count (admin)
export async function setRealDownloadCount(count: number): Promise<boolean> {
  if (!redis) return false
  
  try {
    await redis.set(REAL_DOWNLOAD_KEY, count)
    return true
  } catch (error) {
    console.error('Redis error:', error)
    return false
  }
}
