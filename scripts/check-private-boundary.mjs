import {readFile} from 'node:fs/promises'
import {spawnSync} from 'node:child_process'
import process from 'node:process'

const gitignore = await readFile('.gitignore', 'utf8')
if (!gitignore.split(/\r?\n/).includes('/local/')) {
  console.error('Privacy check failed: .gitignore must contain /local/.')
  process.exit(1)
}

const result = spawnSync('git', ['ls-files', '--', 'local'], {encoding: 'utf8'})
if (result.status !== 0) {
  console.error('Privacy check failed: this folder is not a readable Git repository.')
  process.exit(1)
}

const tracked = result.stdout.trim()
if (tracked) {
  console.error('Privacy check failed: Git is tracking files under local/:')
  console.error(tracked)
  process.exit(1)
}

console.log('Privacy boundary check passed.')

