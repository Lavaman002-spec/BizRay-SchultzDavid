export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get('q') || '';
  const backendUrl = `http://localhost:8080/companies/search?q=${encodeURIComponent(
    q
  )}`;
  const res = await fetch(backendUrl);
  const data = await res.text();
  return new Response(data, {
    headers: { 'Content-Type': 'application/json' },
  });
}
