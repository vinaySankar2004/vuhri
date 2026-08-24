import {execFileSync} from 'node:child_process'
import {readFileSync} from 'node:fs'

const tracked = execFileSync('git', ['ls-files', '-z'], {encoding: 'utf8'})
  .split('\0')
  .filter(Boolean)

const retiredTitle = ['Hub', 'To', 'Learn'].join('')
const retiredSlug = ['hub', 'to', 'learn'].join('-')
const retiredScope = `@${['hub', 'to', 'learn'].join('')}`
const retiredIntermediateName = ['va', 'hri'].join('')
const uppercaseName = ['V', 'uhri'].join('')

const forbidden = [
  {
    label: 'retired project name',
    pattern: new RegExp(
      `${retiredTitle}|${retiredSlug}|${retiredScope}|${retiredIntermediateName}`,
      'gi',
    ),
  },
  {label: 'uppercase project name', pattern: new RegExp(`\\b${uppercaseName}\\b`, 'g')},
]

const failures = []

for (const file of tracked) {
  const content = readFileSync(file)
  if (content.includes(0)) continue
  const text = content.toString('utf8')
  for (const rule of forbidden) {
    for (const match of text.matchAll(rule.pattern)) {
      const line = text.slice(0, match.index).split('\n').length
      failures.push(`${file}:${line}: ${rule.label}: ${match[0]}`)
    }
  }
}

if (failures.length) {
  console.error(failures.join('\n'))
  process.exit(1)
}

console.log(`Identity check passed for ${tracked.length} tracked file(s).`)
