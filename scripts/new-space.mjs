import {cp, mkdir, readFile, writeFile} from 'node:fs/promises'
import path from 'node:path'
import process from 'node:process'

const [slug, ...titleParts] = process.argv.slice(2)
const title = titleParts.join(' ').trim()

if (!slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || !title) {
  console.error('Usage: node scripts/new-space.mjs <kebab-case-slug> <title>')
  process.exit(1)
}

const root = process.cwd()
const destination = path.join(root, 'local', 'spaces', slug)
const template = path.join(root, 'templates', 'space')

try {
  await mkdir(destination, {recursive: false})
} catch (error) {
  if (error.code === 'ENOENT') {
    console.error('Run npm run setup before creating a space.')
  } else if (error.code === 'EEXIST') {
    console.error(`Space already exists: ${destination}`)
  } else {
    console.error(error.message)
  }
  process.exit(1)
}

await cp(template, destination, {recursive: true, errorOnExist: true})
const contextPath = path.join(destination, 'CONTEXT.md')
const context = await readFile(contextPath, 'utf8')
await writeFile(
  contextPath,
  context
    .replace('title: Replace with a clear title', `title: ${title}`)
    .replace('description: Replace with a one-sentence purpose.', `description: Learning space for ${title}.`),
)

console.log(`Created private learning space: local/spaces/${slug}`)

