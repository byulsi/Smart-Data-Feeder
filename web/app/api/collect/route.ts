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

    return new Promise((resolve) => {
      exec(command, { cwd: projectRoot }, (error, stdout, stderr) => {
        if (error) {
          console.error(`exec error: ${error}`)
          console.error(`stderr: ${stderr}`)
          resolve(NextResponse.json({ error: 'Collection failed', details: stderr }, { status: 500 }))
          return
        }
        
        console.log(`stdout: ${stdout}`)
        
        // After collection, we also need to run the markdown generator to ensure artifacts are ready
        // Although the collector might be enough if the web app reads from DB directly.
        // But for "Download .md", we need the generator.
        
        const generatorPath = path.join(projectRoot, 'processors', 'markdown_generator.py')
        const genCommand = `python3 "${generatorPath}"`
        
        exec(genCommand, { cwd: projectRoot }, (genError, genStdout, genStderr) => {
             if (genError) {
                 console.error(`Generator error: ${genError}`)
                 // We don't fail the whole request if generator fails, but it's good to know
             }
             resolve(NextResponse.json({ success: true, message: 'Collection completed' }))
        })
      })
    })

  } catch (error: any) {
    console.error('API error:', error)
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 })
  }
}
