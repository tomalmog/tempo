import { setRealDownloadCount } from '../../../../lib/redis'
import { NextRequest, NextResponse } from 'next/server'

const ADMIN_SECRET = process.env.ADMIN_SECRET || 'tempo-admin-secret'

export async function POST(request: NextRequest) {
  try {
    const { count, secret } = await request.json()
    
    if (secret !== ADMIN_SECRET) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    if (typeof count !== 'number' || count < 0) {
      return NextResponse.json({ error: 'Invalid count' }, { status: 400 })
    }
    
    const success = await setRealDownloadCount(count)
    
    if (!success) {
      return NextResponse.json({ error: 'Redis not configured' }, { status: 500 })
    }
    
    return NextResponse.json({ success: true, count })
  } catch (error) {
    console.error('Error:', error)
    return NextResponse.json({ error: 'Failed to set count' }, { status: 500 })
  }
}
