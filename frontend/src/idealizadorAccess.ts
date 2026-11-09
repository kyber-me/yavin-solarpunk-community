const ACCESS_MARKER = 'yavin.idealizador.access.v1';
const API_URL = import.meta.env?.VITE_API_URL ?? 'http://127.0.0.1:8000';

export class IdealizadorAccessError extends Error {
  status: number;
  code?: string;
  constructor(message: string, status: number, code?: string) {
    super(message); this.status = status; this.code = code;
  }
}

function requestBody(value: unknown): Record<string, unknown> | undefined {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown> : undefined;
}

export function hasIdealizadorAccess(): boolean {
  return sessionStorage.getItem(ACCESS_MARKER) === 'authorized';
}

export function clearIdealizadorAccess(): void {
  sessionStorage.removeItem(ACCESS_MARKER);
}

export async function authorizeIdealizador(key: string): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/access/idealizador`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key }),
      signal: AbortSignal.timeout(30000),
    });
  } catch {
    throw new Error('Não foi possível acessar a API. Verifique a conexão e tente novamente.');
  }
  const payload = requestBody(await response.json().catch(() => null));
  const error = requestBody(payload?.error);
  if (!response.ok || error) {
    throw new IdealizadorAccessError(
      typeof error?.message === 'string' ? error.message : 'Não foi possível validar a palavra-chave.',
      response.status,
      typeof error?.code === 'string' ? error.code : undefined,
    );
  }
  if (requestBody(payload?.data)?.authorized !== true) {
    throw new Error('A API não confirmou o acesso ao Idealizador.');
  }
  sessionStorage.setItem(ACCESS_MARKER, 'authorized');
}
