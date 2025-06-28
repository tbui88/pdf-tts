export const API_BASE = import.meta.env.VITE_API_BASE_URL;

export interface UploadResponse {
  audio_url: string;          // adjust to your backend’s JSON keys
  estimated_duration?: number;
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new Error(`Upload failed (${res.status}): ${res.statusText}`);
  }
  return res.json();
}
