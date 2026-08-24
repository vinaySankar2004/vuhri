import {describe, expect, test} from 'vitest'
import {clampStep} from './steps'

describe('clampStep', () => {
  test('keeps a valid step', () => {
    expect(clampStep(2, 5)).toBe(2)
  })

  test('clamps both boundaries', () => {
    expect(clampStep(-1, 5)).toBe(0)
    expect(clampStep(9, 5)).toBe(4)
  })

  test('handles invalid totals and fractional steps', () => {
    expect(clampStep(1, 0)).toBe(0)
    expect(clampStep(1.5, 5)).toBe(0)
  })
})

