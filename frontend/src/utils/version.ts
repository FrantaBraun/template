/**
 * Part of the With FBraun project template.
 * Author: František Braun <frantisek.braun95@gmail.com>
 * Freely available as a template for building custom applications.
 */

/** Parses a "major.minor[.patch]" string into numeric parts, defaulting missing/invalid segments to 0. */
export function parseMajorMinor(version: string | undefined) {
  const parts = String(version ?? '').split('.')
  return { major: parseInt(parts[0], 10) || 0, minor: parseInt(parts[1], 10) || 0 }
}

/**
 * Numerically compares two "major.minor.patch"-style version strings,
 * segment by segment (not lexicographic, so "10.0" > "9.0"). Returns a
 * positive number if `a` > `b`, negative if `a` < `b`, 0 if equal.
 */
export function compareVersions(a: string, b: string): number {
  const partsA = a.split('.').map((n) => parseInt(n, 10) || 0)
  const partsB = b.split('.').map((n) => parseInt(n, 10) || 0)
  const length = Math.max(partsA.length, partsB.length)
  for (let i = 0; i < length; i++) {
    const diff = (partsA[i] ?? 0) - (partsB[i] ?? 0)
    if (diff !== 0) return diff
  }
  return 0
}
