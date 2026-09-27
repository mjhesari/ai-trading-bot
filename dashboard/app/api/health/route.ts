import { NextResponse } from "next/server";
import { ENGINE_URL } from "@/lib/api";

export async function GET() {
  try {
    const res = await fetch(`${ENGINE_URL}/api/health`, { cache: "no-store" });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch {
    return NextResponse.json({ status: "unreachable", engine: ENGINE_URL }, { status: 502 });
  }
}
