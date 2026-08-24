import {readFile} from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import {listFiles} from './lib/files.mjs'

const extensions = new Set(['.css', '.html', '.md', '.ts', '.tsx'])
const excluded = new Set([
  'method/writing.md',
  'scripts/check-writing.mjs',
])
const checks = [
  {label: 'em dash', pattern: /—/g},
  {label: 'en dash', pattern: /–/g},
  {label: 'canned contrast', pattern: /\b(?:is|are|was|were|it(?:'s| is)) not just\b/gi},
  {label: 'empty opening', pattern: /\b(?:great question|let(?:'s| us) dive in)\b/gi},
]
const failures = []

const files = await listFiles(process.cwd(), (file) => extensions.has(path.extname(file)))
for (const file of files) {
  const relative = path.relative(process.cwd(), file)
  if (excluded.has(relative)) {
    continue
  }

  const lines = (await readFile(file, 'utf8')).split(/\r?\n/)
  lines.forEach((line, index) => {
    for (const check of checks) {
      check.pattern.lastIndex = 0
      if (check.pattern.test(line)) {
        failures.push(`${relative}:${index + 1}: ${check.label}`)
      }
    }
  })
}

if (failures.length) {
  console.error('Writing check failed:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log(`Writing check passed for ${files.length} file(s).`)

