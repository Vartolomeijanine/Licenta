const API_BASE = import.meta.env.VITE_API_BASE || ""

export function resolveMediaUrl(url) {
  if (!url) {
    return ""
  }

  // Fix for backend returning http://localhost/media/... without port
  if (url.startsWith("http://localhost/media/")) {
    return url.replace("http://localhost", "")
  }

  if (url.startsWith("http://127.0.0.1/media/")) {
    return url.replace("http://127.0.0.1", "")
  }

  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url
  }

  if (url.startsWith("/")) {
    return `${API_BASE}${url}`
  }

  return `${API_BASE}/${url}`
}