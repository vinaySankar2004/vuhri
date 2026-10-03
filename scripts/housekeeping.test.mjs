import assert from 'node:assert/strict'
import {mkdir, mkdtemp, rm, writeFile} from 'node:fs/promises'
import {tmpdir} from 'node:os'
import path from 'node:path'
import test from 'node:test'
import {deepCleanDue, mainCheckout, pendingMigrations, scan} from './housekeeping.mjs'

const MB = 1024 * 1024

async function file(root, relative, megabytes) {
  const target = path.join(root, relative)
  await mkdir(path.dirname(target), {recursive: true})
  await writeFile(target, Buffer.alloc(megabytes * MB, 1))
}

test('reports rebuildable folders, renders, large files, and session copies', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'housekeeping-'))
  try {
    await file(root, 'node_modules/pkg/index.js', 2)
    await file(root, 'local/artifacts/clip/06_production/out/final.mp4', 3)
    await file(root, 'local/inbox/recording.mov', 2)
    await file(root, '.claude/worktrees/session-a/notes.md', 1)
    await file(root, 'method/small.md', 0)

    const limits = {rebuildable: MB, output: MB, file: MB}
    const report = await scan(root, {limits})
    const kinds = Object.fromEntries(report.findings.map((item) => [item.path, item.kind]))
    assert.equal(kinds['node_modules'], 'rebuildable')
    assert.equal(kinds[path.join('local/artifacts/clip/06_production/out')], 'render')
    assert.equal(kinds[path.join('local/inbox/recording.mov')], 'file')
    assert.equal(kinds[path.join('.claude/worktrees/session-a')], 'session copy')
    assert.ok(report.total >= 8 * MB)

    const kept = await scan(root, {limits, keep: [{path: 'node_modules', bytes: 2 * MB}]})
    assert.equal(kept.hidden, 1)
    assert.ok(!kept.findings.some((item) => item.path === 'node_modules'))
  } finally {
    await rm(root, {recursive: true, force: true})
  }
})

test('finds the main checkout from a worktree', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'housekeeping-'))
  try {
    const worktree = path.join(root, 'main', '.claude', 'worktrees', 'w')
    await mkdir(worktree, {recursive: true})
    await writeFile(path.join(worktree, '.git'), `gitdir: ${path.join(root, 'main', '.git', 'worktrees', 'w')}\n`)
    assert.equal(mainCheckout(worktree), path.join(root, 'main'))
    assert.equal(mainCheckout(path.join(root, 'main')), path.join(root, 'main'))
  } finally {
    await rm(root, {recursive: true, force: true})
  }
})

test('lists migrations newer than the aligned date, oldest first', () => {
  const text = '# Migrations\n\n## 2026-11-02: Later\n\n- step\n\n## 2026-10-03: First\n\n- step\n'
  assert.deepEqual(pendingMigrations(text, '').map((entry) => entry.date), ['2026-10-03', '2026-11-02'])
  assert.deepEqual(pendingMigrations(text, '2026-10-03').map((entry) => entry.title), ['Later'])
  assert.deepEqual(pendingMigrations(text, '2026-11-02'), [])
})

test('reports a deep clean as due by age or by accepted lessons', () => {
  const now = new Date('2026-11-20T12:00:00')
  assert.equal(deepCleanDue(undefined, '', now).due, true)
  assert.equal(deepCleanDue('2026-10-03', '', now).due, true)
  assert.equal(deepCleanDue('2026-11-10', '', now).due, false)
  const lessons = ['11-11', '11-12', '11-13', '11-14', '11-15'].map((day) => `## 2026-${day}: lesson`).join('\n')
  assert.equal(deepCleanDue('2026-11-10', lessons, now).due, true)
})
