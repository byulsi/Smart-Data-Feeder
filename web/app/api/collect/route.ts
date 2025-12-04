import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import path from 'path'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { ticker } = body

    if (!ticker) {
      return NextResponse.json({ error: 'Invalid ticker or name' }, { status: 400 })
    }

    // Path to the collector script
    // Assuming the web app is in /web and collector is in root
    const projectRoot = path.resolve(process.cwd(), '..')
    const scriptPath = path.join(projectRoot, 'collector.py')
    
    // Command to run python script
    // Using python3, assuming it's in the path. 
    // In a real env, might need absolute path to python executable.
    const command = `python3 "${scriptPath}" ${ticker}`
    
    console.log(`Executing command: ${command}`)

    const util = require('util');
    const execPromise = util.promisify(exec);

    try {
        const { stdout, stderr } = await execPromise(command, { cwd: projectRoot });
        console.log(`stdout: ${stdout}`);
        if (stderr) console.error(`stderr: ${stderr}`);

        // Run generator
        const generatorPath = path.join(projectRoot, 'processors', 'markdown_generator.py')
        const genCommand = `python3 "${generatorPath}"`
        
        try {
             await execPromise(genCommand, { cwd: projectRoot });
        } catch (genError) {
             console.error(`Generator error: ${genError}`)
        }

        return NextResponse.json({ success: true, message: 'Collection completed' })

    } catch (error: any) {
        console.error(`exec error: ${error}`)
        return NextResponse.json({ error: 'Collection failed', details: error.stderr || error.message }, { status: 500 })
    }

  } catch (error: any) {
    console.error('API error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
