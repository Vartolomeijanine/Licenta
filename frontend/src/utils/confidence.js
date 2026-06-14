export function getConfidenceLabel(confidence) {
  const value = Number(confidence)

  if (Number.isNaN(value)) {
    return 'Unknown'
  }

  if (value < 0.35) {
    return 'Low'
  }

  if (value < 0.55) {
    return 'Moderate'
  }

  return 'High'
}
