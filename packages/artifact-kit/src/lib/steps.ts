export function clampStep(step: number, total: number) {
  if (!Number.isFinite(step) || !Number.isInteger(step)) {
    return 0
  }
  if (!Number.isFinite(total) || total <= 0) {
    return 0
  }
  return Math.min(Math.max(step, 0), total - 1)
}

