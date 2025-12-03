import Database from 'better-sqlite3'
import path from 'path'

// Assuming the web app is running from the 'web' directory
// and data.db is in the parent directory.
const dbPath = path.join(process.cwd(), '..', 'data.db')

let db: any

try {
  db = new Database(dbPath, { verbose: console.log })
  db.pragma('journal_mode = WAL')
} catch (error) {
  console.error('Failed to open database:', error)
  // Fallback or re-throw depending on how you want to handle it
  throw error
}

export default db
