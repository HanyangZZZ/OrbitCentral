import { readFileSync } from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

const projectRoot = path.resolve(__dirname, '..')

describe('Capacitor config', () => {
  it('has required fields', () => {
    const raw = readFileSync(path.join(projectRoot, 'capacitor.config.json'), 'utf-8')
    const config = JSON.parse(raw)

    expect(config.appId).toBeTruthy()
    expect(config.appName).toBeTruthy()
    expect(config.webDir).toBe('dist')
  })
})
