import {readdir, readFile, stat} from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

// Every file an agent loads carries a context cost. The entry files are read at
// the start of every session, so they hold routing and live state only. Detail
// belongs in the method, skill, space, or record it describes, one link away.
const fixed = [
  {file: 'AGENTS.md', budget: 700},
  {file: 'local/NOW.md', budget: 450, private: true},
  {file: 'local/PROFILE.md', budget: 400, private: true},
]
const groups = [
  {dir: 'method', match: (name) => name.endsWith('.md'), budget: 1000},
  {dir: '.agents/skills', match: (name) => name.endsWith('SKILL.md'), budget: 800, depth: 2},
  {dir: '.agents/skills', match: (name) => name.includes('/references/') && name.endsWith('.md'), budget: 1000, depth: 3},
]

const failures = []
let checked = 0

async function exists(file) {
  try {
    await stat(file)
    return true
  } catch {
    return false
  }
}

async function measure(file, budget) {
  const words = (await readFile(file, 'utf8')).split(/\s+/).filter(Boolean).length
  checked += 1
  if (words > budget) failures.push(`${file} is ${words} words, over its ${budget} word budget.`)
}

async function walk(dir, depth) {
  const entries = await readdir(dir, {withFileTypes: true})
  const files = []
  for (const entry of entries) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory() && depth > 1) files.push(...(await walk(full, depth - 1)))
    else if (entry.isFile()) files.push(full)
  }
  return files
}

for (const {file, budget, private: isPrivate} of fixed) {
  if (await exists(file)) await measure(file, budget)
  else if (!isPrivate) failures.push(`${file} is missing.`)
}

for (const {dir, match, budget, depth = 1} of groups) {
  for (const file of await walk(dir, depth)) {
    if (match(file.split(path.sep).join('/'))) await measure(file, budget)
  }
}

if (failures.length) {
  console.error('Context check failed:')
  for (const failure of failures) console.error(`- ${failure}`)
  console.error('Keep entry files to routing and live state. Move detail to the file it belongs to and link to it.')
  process.exit(1)
}

console.log(`Context check passed for ${checked} file(s).`)
