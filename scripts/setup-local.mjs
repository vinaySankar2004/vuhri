import {constants} from 'node:fs'
import {copyFile, mkdir, readdir} from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

const root = process.cwd()
const templateRoot = path.join(root, 'templates', 'local')
const localRoot = path.join(root, 'local')
let created = 0
let preserved = 0

async function copyMissing(source, destination) {
  await mkdir(destination, {recursive: true})
  const entries = await readdir(source, {withFileTypes: true})

  for (const entry of entries) {
    const from = path.join(source, entry.name)
    const to = path.join(destination, entry.name)

    if (entry.isDirectory()) {
      await copyMissing(from, to)
      continue
    }

    try {
      await copyFile(from, to, constants.COPYFILE_EXCL)
      created += 1
    } catch (error) {
      if (error.code !== 'EEXIST') {
        throw error
      }
      preserved += 1
    }
  }
}

await copyMissing(templateRoot, localRoot)

console.log(`Private learner area ready at ${localRoot}`)
console.log(`Created ${created} file(s); preserved ${preserved} existing file(s).`)

