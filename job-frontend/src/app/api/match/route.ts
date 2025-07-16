import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const token = request.headers.get('authorization');
    
    // Build the backend URL with query parameters
    const backendUrl = new URL('http://localhost:8000/api/match');
    searchParams.forEach((value, key) => {
      backendUrl.searchParams.append(key, value);
    });

    // Make request to backend with longer timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes

    const response = await fetch(backendUrl.toString(), {
      headers: {
        'Authorization': token || '',
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Backend error' }));
      return NextResponse.json(errorData, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error: any) {
    console.error('Match API error:', error);
    
    if (error.name === 'AbortError') {
      return NextResponse.json(
        { detail: 'Request timeout - job search is taking longer than expected' },
        { status: 408 }
      );
    }

    return NextResponse.json(
      { detail: 'Internal server error' },
      { status: 500 }
    );
  }
} 