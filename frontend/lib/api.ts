export async function parseJsonResponse(response: Response): Promise<unknown | null> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

export function formatApiError(data: unknown, fallback = 'Something went wrong'): string {
  if (!data || typeof data !== 'object') return fallback;
  const record = data as Record<string, unknown>;

  if (typeof record.detail === 'string') return record.detail;
  if (Array.isArray(record.detail)) return record.detail.map(String).join(', ');

  for (const key of ['email', 'password', 'password_confirm', 'role', 'name', 'non_field_errors']) {
    const value = record[key];
    if (typeof value === 'string') return value;
    if (Array.isArray(value) && value.length > 0) return value.map(String).join(', ');
  }

  return fallback;
}

export function displayNameFromEmail(email: string): string {
  const local = email.split('@')[0]?.trim() || 'User';
  const words = local.replace(/[._-]+/g, ' ').split(' ').filter(Boolean);
  if (words.length === 0) return 'User';
  return words.map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');
}
