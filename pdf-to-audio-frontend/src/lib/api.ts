export const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function uploadPdf(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Upload failed: ${res.statusText}`);
  }

  // adjust to whatever your backend returns
  const { audio_url } = await res.json();
  return audio_url;            // e.g. "https://.../output.mp3"
}
