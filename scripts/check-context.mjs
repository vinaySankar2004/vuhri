import {readFile, stat} from 'node:fs/promises'
import process from 'node:process'

// NOW.md is read at the start of every session, so its length is a standing
// context cost. Keep it to what is live. Detail belongs in the space, the
// session record, or the knowledge note it describes.
const budget = 450
const path = 'local/NOW.md'

try {
  await stat(path)
} catch {
  console.log('Context check skipped: no private workspace in this clone.')
  process.exit(0)
}

const text = await readFile(path, 'utf8')
const words = text.split(/\s+/).filter(Boolean).length

if (words > budget) {
  console.error(`Context check failed: ${path} is ${words} words, over the ${budget} word budget.`)
  console.error('Trim resolved items, fold duplicated facts, and move detail to the space it belongs to.')
  process.exit(1)
}

console.log(`Context check passed: ${path} is ${words} of ${budget} words.`)
