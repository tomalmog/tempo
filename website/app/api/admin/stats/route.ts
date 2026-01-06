import { getRealDownloadCount, getDisplayDownloadCount } from '../../../../lib/redis'
import { NextRequest, NextResponse } from 'next/server'

const ADMIN_SECRET = process.env.ADMIN_SECRET || 'tempo-admin-secret'

export async function GET(request: NextRequest) {
  const secret = request.nextUrl.searchParams.get('secret')
  
  if (secret !== ADMIN_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  const realCount = await getRealDownloadCount()
  const displayCount = await getDisplayDownloadCount()
  const fakeCount = displayCount - realCount
  
  return NextResponse.json({
    real: realCount,           // Actual downloads
    fake: fakeCount,           // Inflated fake downloads
    display: displayCount,     // What visitors see (real + fake)
    timestamp: new Date().toISOString(),
  })
}
