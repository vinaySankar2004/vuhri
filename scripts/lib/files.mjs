import {readdir, stat} from 'node:fs/promises'
import path from 'node:path'

const ignoredDirectories = new Set([
  '.git',
  'coverage',
  'dist',
  'local',
  'node_modules',
  'output',
])

export async function listFiles(root, predicate = () => true) {
  const files = []

  async function visit(current) {
    const entries = await readdir(current, {withFileTypes: true})
    for (const entry of entries) {
      const fullPath = path.join(current, entry.name)
      if (entry.isDirectory()) {
        if (!ignoredDirectories.has(entry.name)) {
          await visit(fullPath)
        }
      } else if (entry.isFile() && predicate(fullPath)) {
        files.push(fullPath)
      }
    }
  }

  if ((await stat(root)).isDirectory()) {
    await visit(root)
  }

  return files.sort()
}

