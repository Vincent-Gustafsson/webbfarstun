export function getErrorMessage(err: unknown): string {
  if (err instanceof Error) {
    return err.message
  }
  // Fallback if the error is a string or something else
  return String(err)
}
