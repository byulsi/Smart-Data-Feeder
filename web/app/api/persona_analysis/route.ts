import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import path from 'path'
import util from 'util'

const execPromise = util.promisify(exec)

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { ticker, persona } = body

    if (!ticker) {
      return NextResponse.json({ error: 'Ticker is required' }, { status: 400 })
    }

    // Resolve path to the python script
    // Assuming the web app is in /web and processors is in /processors
    // We need to go up two levels from the current file location? 
    // Actually, process.cwd() in Next.js usually points to the project root (where package.json is).
    // If package.json is in /web, then we need to go up one level to find processors.
    
    // Let's try to find the script relative to the project root
    // In this environment, the root is /Users/admin/.gemini/antigravity/playground/vector-schrodinger
    // The web app is in /web.
    // So if we run `npm run dev` in /web, process.cwd() is likely /web.
    
    const scriptPath = path.resolve(process.cwd(), '../processors/analyst_engine.py')
    
    // Command to run python script
    // We assume python3 is available in the environment
    const command = `python3 "${scriptPath}" --ticker "${ticker}" --persona "${persona || 'value_hunter'}"`
    
    console.log('Executing command:', command)
    
    const { stdout, stderr } = await execPromise(command)
    
    if (stderr) {
      console.error('Python script error:', stderr)
      // Note: Python might print warnings to stderr, so we don't necessarily fail here unless stdout is empty
    }

    return NextResponse.json({ result: stdout })
    
  } catch (error: any) {
    console.error('Analysis generation error:', error)
    return NextResponse.json({ error: 'Failed to generate analysis', details: error.message }, { status: 500 })
  }
}
