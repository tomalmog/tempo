import { incrementDownloadCount } from '../../../../lib/redis'
import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const url = request.nextUrl.searchParams.get('url')
  
  if (!url) {
    return NextResponse.json({ error: 'Missing URL' }, { status: 400 })
  }
  
  // Increment download count
  try {
    await incrementDownloadCount()
  } catch (e) {
    console.error('Failed to increment:', e)
  }
  
  // For CLI installs, just return OK (no redirect needed)
  if (url === 'cli-install') {
    return NextResponse.json({ tracked: true })
  }
  
  // Redirect to actual download URL (307 = temporary redirect, preserves method)
  return NextResponse.redirect(url, { status: 307 })
}
