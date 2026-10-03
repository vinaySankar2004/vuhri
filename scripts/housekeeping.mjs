// Session-start housekeeping: report large items in the vuhri folder and, for a
// user, whether a newer version exists. method/housekeeping.md says how to act
// on the result. Nothing here deletes anything.
import {spawnSync} from 'node:child_process'
import {existsSync, readFileSync} from 'node:fs'
import {lstat, readdir, readFile, writeFile} from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'
import {fileURLToPath, pathToFileURL} from 'node:url'

const MB = 1024 * 1024
export const LIMITS = {rebuildable: 50 * MB, output: 100 * MB, file: 100 * MB}
const REBUILDABLE = new Set([
  '.cache', '.next', '.parcel-cache', '.pytest_cache', '.turbo', '.venv', '.venv-audio', '.vite',
  '__pycache__', 'build', 'coverage', 'dist', 'node_modules', 'venv',
])
const OUTPUT = {out: 'render', renders: 'render', runs: 'evidence'}
const WORKTREES = path.join('.claude', 'worktrees')
const SETTINGS = path.join('local', 'settings', 'housekeeping.json')
const MIGRATIONS = 'MIGRATIONS.md'
const UPDATE_INTERVAL_MS = 24 * 60 * 60 * 1000
const DEEP_CLEAN_DAYS = 30
const DEEP_CLEAN_LESSONS = 5

// A worktree's .git is a file that points into the main checkout's .git folder.
// local/ lives only in the main checkout, so settings and scans start there.
export function mainCheckout(root) {
  try {
    const match = readFileSync(path.join(root, '.git'), 'utf8').match(/^gitdir:\s*(.+)$/m)
    if (match) {
      const gitdir = path.resolve(root, match[1].trim())
      const index = gitdir.lastIndexOf(`${path.sep}.git${path.sep}`)
      if (index !== -1) return gitdir.slice(0, index)
    }
  } catch {
    // .git is a folder, or missing: this is the main checkout.
  }
  return root
}

const diskBytes = (info) => (info.blocks ? info.blocks * 512 : info.size)

async function sizeOf(target) {
  const info = await lstat(target)
  if (!info.isDirectory()) return diskBytes(info)
  let total = diskBytes(info)
  for (const entry of await readdir(target, {withFileTypes: true})) {
    if (!entry.isSymbolicLink()) total += await sizeOf(path.join(target, entry.name))
  }
  return total
}

export async function scan(root, {limits = LIMITS, keep = []} = {}) {
  const findings = []

  async function measure(full, relative, kind, limit) {
    const bytes = await sizeOf(full)
    if (bytes >= limit) findings.push({kind, path: relative, bytes})
    return bytes
  }

  async function visit(dir, rel) {
    let total = 0
    let entries
    try {
      entries = await readdir(dir, {withFileTypes: true})
    } catch {
      return 0
    }
    for (const entry of entries) {
      const full = path.join(dir, entry.name)
      const relative = path.join(rel, entry.name)
      if (entry.isSymbolicLink()) continue
      if (entry.isFile()) {
        const bytes = diskBytes(await lstat(full))
        if (bytes >= limits.file) findings.push({kind: 'file', path: relative, bytes})
        total += bytes
      } else if (!entry.isDirectory()) {
        continue
      } else if (entry.name === '.git') {
        total += await sizeOf(full)
      } else if (rel === WORKTREES) {
        total += await measure(full, relative, 'session copy', 0)
      } else if (REBUILDABLE.has(entry.name)) {
        total += await measure(full, relative, 'rebuildable', limits.rebuildable)
      } else if (OUTPUT[entry.name]) {
        total += await measure(full, relative, OUTPUT[entry.name], limits.output)
      } else {
        total += await visit(full, relative)
      }
    }
    return total
  }

  const total = await visit(root, '')
  const kept = new Map(keep.map((item) => [item.path, item.bytes]))
  const visible = findings.filter((item) => !(kept.has(item.path) && item.bytes <= kept.get(item.path) * 1.5))
  visible.sort((a, b) => b.bytes - a.bytes)
  return {total, findings: visible, hidden: findings.length - visible.length}
}

function git(root, args) {
  return spawnSync('git', ['-C', root, ...args], {encoding: 'utf8'})
}

export function checkUpdate(root) {
  if (git(root, ['fetch', '--quiet']).status !== 0) {
    return {available: null, reason: 'could not reach the update source'}
  }
  const behind = git(root, ['rev-list', '--count', 'HEAD..@{upstream}'])
  if (behind.status !== 0) return {available: null, reason: 'no update source is configured'}
  const changes = Number(behind.stdout.trim())
  return {available: changes > 0, changes}
}

// Entries in MIGRATIONS.md newer than the date this local/ was last aligned to.
export function pendingMigrations(text, alignedThrough = '') {
  return [...text.matchAll(/^## (\d{4}-\d{2}-\d{2}): (.+)$/gm)]
    .map(([, date, title]) => ({date, title}))
    .filter((entry) => entry.date > alignedThrough)
    .sort((a, b) => a.date.localeCompare(b.date))
}

// A deep clean is due when none is recorded, the last is a month old, or
// enough lessons have been accepted since that the rules have likely drifted.
export function deepCleanDue(lastClean, lessonsText, now = new Date()) {
  if (!lastClean) return {due: true, reason: 'no deep clean recorded'}
  const days = (now - new Date(`${lastClean}T00:00:00`)) / 86400000
  if (days > DEEP_CLEAN_DAYS) return {due: true, reason: `last one was ${Math.floor(days)} days ago`}
  const since = [...lessonsText.matchAll(/^## (\d{4}-\d{2}-\d{2}):/gm)].filter(([, date]) => date > lastClean).length
  if (since >= DEEP_CLEAN_LESSONS) return {due: true, reason: `${since} lessons since the last one`}
  return {due: false}
}

function readMigrations(root) {
  try {
    return readFileSync(path.join(root, MIGRATIONS), 'utf8')
  } catch {
    return ''
  }
}

export function applyUpdate(root) {
  const status = git(root, ['status', '--porcelain', '--untracked-files=no'])
  if (status.status !== 0) return {ok: false, reason: 'could not read the folder state'}
  if (status.stdout.trim()) return {ok: false, reason: 'vuhri files were changed locally', files: status.stdout.trim()}
  const before = git(root, ['rev-parse', 'HEAD']).stdout.trim()
  const pull = git(root, ['pull', '--ff-only', '--quiet'])
  if (pull.status !== 0) return {ok: false, reason: 'the update could not be applied', detail: pull.stderr.trim()}
  const changed = git(root, ['diff', '--name-only', before, 'HEAD']).stdout.split('\n').filter(Boolean)
  if (changed.some((file) => file === 'package.json' || file === 'package-lock.json')) {
    if (spawnSync('npm', ['install'], {cwd: root, stdio: 'inherit'}).status !== 0) {
      return {ok: false, reason: 'updated, but reinstalling building blocks failed'}
    }
  }
  // Add any files new templates introduced, without overwriting the person's own.
  spawnSync(process.execPath, [path.join(root, 'scripts', 'setup-local.mjs')], {cwd: root, encoding: 'utf8'})
  const whatsNew = git(root, ['log', '--format=%s', '--max-count=20', `${before}..HEAD`]).stdout.split('\n').filter(Boolean)
  return {ok: true, changedFiles: changed.length, whatsNew}
}

async function readSettings(root) {
  try {
    return JSON.parse(await readFile(path.join(root, SETTINGS), 'utf8'))
  } catch {
    return {}
  }
}

async function writeSettings(root, settings) {
  const file = path.join(root, SETTINGS)
  if (!existsSync(path.dirname(file))) return false
  await writeFile(file, `${JSON.stringify(settings, null, 2)}\n`)
  return true
}

const size = (bytes) => (bytes >= 1024 * MB ? `${(bytes / 1024 / MB).toFixed(1)} GB` : `${Math.round(bytes / MB)} MB`)

async function main() {
  const args = process.argv.slice(2)
  const root = mainCheckout(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..'))
  const settings = await readSettings(root)
  const role = settings.role === 'maintainer' ? 'maintainer' : 'user'

  const keepIndex = args.indexOf('--keep')
  if (keepIndex !== -1) {
    const target = path.resolve(root, args[keepIndex + 1] ?? '')
    const relative = path.relative(root, target)
    if (!args[keepIndex + 1] || relative.startsWith('..') || !existsSync(target)) {
      console.error('Usage: npm run housekeeping -- --keep <path inside the vuhri folder>')
      process.exit(1)
    }
    const bytes = await sizeOf(target)
    settings.keep = [...(settings.keep ?? []).filter((item) => item.path !== relative),
      {path: relative, bytes, date: new Date().toISOString().slice(0, 10)}]
    if (!(await writeSettings(root, settings))) {
      console.error('No local/settings folder to record this in. Run npm run setup first.')
      process.exit(1)
    }
    console.log(`Keeping ${relative} (${size(bytes)}). It is raised again only if it grows by half.`)
    return
  }

  const migrations = pendingMigrations(readMigrations(root), settings.aligned_through ?? '')

  if (args.includes('--aligned')) {
    const latest = pendingMigrations(readMigrations(root)).at(-1)
    if (!latest) return
    settings.aligned_through = latest.date
    if (!(await writeSettings(root, settings))) process.exit(1)
    console.log(`local/ is aligned through ${latest.date}.`)
    return
  }

  if (args.includes('--update')) {
    if (role === 'maintainer') {
      console.log('Maintainers update vuhri through Git directly.')
      return
    }
    const result = applyUpdate(root)
    console.log(result.ok ? `Updated vuhri (${result.changedFiles} files changed).` : `Not updated: ${result.reason}.`)
    if (result.files) console.log(result.files)
    if (result.ok) {
      for (const subject of result.whatsNew) console.log(`- new: ${subject}`)
      const after = pendingMigrations(readMigrations(root), settings.aligned_through ?? '')
      for (const entry of after) console.log(`Align local/: ${entry.date} ${entry.title} (see ${MIGRATIONS})`)
    }
    process.exit(result.ok ? 0 : 1)
  }

  const report = await scan(root, {keep: settings.keep ?? []})
  let update = {available: null, reason: role === 'maintainer' ? 'not checked for a maintainer' : 'already checked today'}
  const lastCheck = Date.parse(settings.last_update_check ?? '') || 0
  if (role === 'user' && (args.includes('--check-update') || Date.now() - lastCheck >= UPDATE_INTERVAL_MS)) {
    update = checkUpdate(root)
    if (update.available !== null) {
      settings.last_update_check = new Date().toISOString()
      await writeSettings(root, settings)
    }
  }

  let lessons = ''
  try {
    lessons = readFileSync(path.join(root, 'lessons', 'log.md'), 'utf8')
  } catch {
    // A clone without lessons still gets the date-based check.
  }
  const deepClean = deepCleanDue(settings.last_consolidation, lessons)

  if (args.includes('--json')) {
    console.log(JSON.stringify({root, role, ...report, update, migrations, deepClean}, null, 2))
    return
  }
  console.log(`Housekeeping for ${root} (role: ${role})`)
  console.log(`Folder total: ${size(report.total)}`)
  console.log(report.findings.length ? 'Large items:' : 'Large items: none')
  for (const item of report.findings) console.log(`- ${item.kind}: ${size(item.bytes)} at ${item.path}`)
  if (report.hidden) console.log(`(${report.hidden} item(s) the person chose to keep are not shown)`)
  if (update.available === true) console.log(`Update: a newer version is ready (${update.changes} change(s)). Ask before updating.`)
  else if (update.available === false) console.log('Update: up to date.')
  else console.log(`Update: ${update.reason}.`)
  for (const entry of migrations) console.log(`Align local/: ${entry.date} ${entry.title} (see ${MIGRATIONS})`)
  if (deepClean.due) console.log(`Deep clean: due (${deepClean.reason}). Offer it once.`)
}

if (import.meta.url === pathToFileURL(process.argv[1] ?? '').href) {
  await main()
}
