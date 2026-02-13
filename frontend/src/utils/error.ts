export function getErrorMessage(err: unknown): string {
  const e = err as any

  const detail = e?.response?.data?.detail
  if (typeof detail === 'string') return detail

  if (detail && typeof detail === 'object') {
    if (typeof detail.message === 'string') return detail.message
  }

  const msg = e?.response?.data?.message
  if (typeof msg === 'string') return msg

  if (err instanceof Error) return err.message

  return 'Something went wrong'
}
