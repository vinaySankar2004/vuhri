import {access, readFile} from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import {listFiles} from './lib/files.mjs'

const markdownFiles = await listFiles(process.cwd(), (file) => file.endsWith('.md'))
const failures = []
const linkPattern = /\[[^\]]+\]\(([^)]+)\)/g

for (const file of markdownFiles) {
  const content = await readFile(file, 'utf8')
  for (const match of content.matchAll(linkPattern)) {
    const target = match[1].trim().replace(/^<|>$/g, '').split('#')[0]
    if (!target || /^(?:https?:|mailto:|#|\/)/.test(target)) {
      continue
    }

    const resolved = path.resolve(path.dirname(file), target)
    try {
      await access(resolved)
    } catch {
      failures.push(`${path.relative(process.cwd(), file)} -> ${target}`)
    }
  }
}

if (failures.length) {
  console.error('Broken relative Markdown links:')
  for (const failure of failures) {
    console.error(`- ${failure}`)
  }
  process.exit(1)
}

console.log(`Link check passed for ${markdownFiles.length} Markdown file(s).`)

