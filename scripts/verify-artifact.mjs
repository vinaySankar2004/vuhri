import {spawnSync} from 'node:child_process'
import process from 'node:process'

const artifact = process.argv[2]
if (!artifact) {
  console.error('Usage: npm run verify:artifact -- <artifact-slug>')
  process.exit(1)
}

const steps = [
  ['npm', ['run', 'test']],
  ['npm', ['run', 'build']],
]

for (const [command, args] of steps) {
  const result = spawnSync(command, args, {stdio: 'inherit'})
  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }
}

console.log(`Mechanical checks passed for ${artifact}.`)
console.log('A real browser walkthrough and instructional review are still required.')

