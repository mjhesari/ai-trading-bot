const ENGINE_URL =
  process.env.NEXT_PUBLIC_ENGINE_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function readError(res: Response, method: string, path: string): Promise<Error> {
  let detail = "";
  try {
    const body = (await res.json()) as { detail?: unknown };
    if (typeof body.detail === "string") detail = body.detail;
    else if (body.detail != null) detail = JSON.stringify(body.detail);
  } catch {
    // ignore parse errors
  }
  return new Error(
    detail
      ? `${method} ${path} failed (${res.status}): ${detail}`
      : `${method} ${path} failed: ${res.status}`,
  );
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${ENGINE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) throw await readError(res, "GET", path);
  return res.json() as Promise<T>;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${ENGINE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await readError(res, "POST", path);
  return res.json() as Promise<T>;
}

export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${ENGINE_URL}${path}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw await readError(res, "PUT", path);
  return res.json() as Promise<T>;
}

export { ENGINE_URL };
