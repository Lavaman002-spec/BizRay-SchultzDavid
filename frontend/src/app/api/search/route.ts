import { NextRequest, NextResponse } from 'next/server';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const q = url.searchParams.get('q') ?? '';

  // Call your proxy (which returns { results: [{ fnr, name }] })
  const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`, { cache: 'no-store' });

  if (!res.ok) {
    // Bubble up error but keep CompanyList 
    return NextResponse.json({ items: [], total: 0 }, { status: res.status });
  }

  const data = await res.json(); // { results: [...] }
  const items = (data?.results ?? []).map((r: any) => ({
    id: r.fnr,      // normalize to what CompanyList typically expects
    name: r.name ?? '',
  }));

  return NextResponse.json({ items, total: items.length });
}
