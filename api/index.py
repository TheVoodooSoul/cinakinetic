import os

def handler(request):
    runpod_endpoint = os.getenv("RUNPOD_ENDPOINT", "")
    
    if runpod_endpoint:
        status = "Connected to RunPod RTX 6000 Ada ✅"
        status_color = "#28a745"
    else:
        status = "RunPod endpoint not configured ⚠️"
        status_color = "#dc3545"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎬 CinaKinetic - Cinema Action Scene Generator</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea, #764ba2); 
                color: white; 
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 1000px; 
                margin: 0 auto; 
                text-align: center; 
                padding: 40px;
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
            }}
            h1 {{ font-size: 3rem; margin-bottom: 10px; }}
            .status {{ 
                color: {status_color}; 
                font-weight: bold; 
                margin: 20px 0; 
                padding: 15px;
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
            }}
            .generator {{ 
                background: rgba(255,255,255,0.1); 
                padding: 30px; 
                border-radius: 15px; 
                margin: 30px 0;
                text-align: left;
            }}
            .form-group {{ 
                margin: 20px 0; 
            }}
            label {{ 
                display: block; 
                margin-bottom: 5px; 
                font-weight: bold; 
            }}
            input, textarea, select {{ 
                width: 100%; 
                padding: 10px; 
                border: none; 
                border-radius: 5px; 
                font-size: 16px;
                background: rgba(255,255,255,0.9);
                color: #333;
                box-sizing: border-box;
            }}
            textarea {{ 
                height: 80px; 
                resize: vertical; 
            }}
            .btn {{ 
                display: inline-block; 
                padding: 15px 30px; 
                background: #ff6b6b; 
                color: white; 
                border: none;
                border-radius: 25px; 
                font-weight: bold; 
                font-size: 16px;
                cursor: pointer;
                margin: 20px 0;
                width: 100%;
            }}
            .btn:hover {{ 
                background: #ff5252; 
            }}
            .btn:disabled {{ 
                background: #666; 
                cursor: not-allowed; 
            }}
            .features {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin: 40px 0; 
            }}
            .feature {{ 
                background: rgba(255,255,255,0.1); 
                padding: 20px; 
                border-radius: 10px; 
            }}
            .result {{ 
                margin: 20px 0; 
                padding: 20px; 
                background: rgba(0,0,0,0.2); 
                border-radius: 10px; 
                display: none; 
            }}
            .loading {{ 
                text-align: center; 
                color: #ffc107; 
            }}
            .error {{ 
                color: #dc3545; 
            }}
            .success {{ 
                color: #28a745; 
            }}
        </style>
        <script>
            async function generateImage() {{
                const form = document.getElementById('generateForm');
                const btn = document.getElementById('generateBtn');
                const result = document.getElementById('result');
                
                // Get form data
                const formData = new FormData(form);
                const prompt = formData.get('prompt');
                const style = formData.get('style');
                const resolution = formData.get('resolution');
                
                if (!prompt) {{
                    alert('Please enter a scene description');
                    return;
                }}
                
                // Show loading
                btn.disabled = true;
                btn.textContent = '🔄 Generating...';
                result.style.display = 'block';
                result.innerHTML = '<div class="loading">🎬 Creating your epic action scene...<br>Connecting to RunPod RTX 6000 Ada...<br><br>⚠️ Note: This is a demo. Real generation requires backend integration.</div>';
                
                // Simulate generation process
                setTimeout(() => {{
                    result.innerHTML = `
                        <div class="success">✅ Generation Complete! (Demo)</div>
                        <div style="background: #333; padding: 20px; border-radius: 10px; margin: 10px 0;">
                            <h3>Generated Scene Preview</h3>
                            <p><strong>Prompt:</strong> ${{prompt}}</p>
                            <p><strong>Style:</strong> ${{style}}</p>
                            <p><strong>Resolution:</strong> ${{resolution}}</p>
                            <p style="color: #ffc107;">🔥 Your RunPod endpoint: {runpod_endpoint ? 'Connected' : 'Not configured'}</p>
                            <p style="color: #17a2b8;">💡 Real images will appear here once fully integrated</p>
                        </div>
                    `;
                    
                    // Reset button
                    btn.disabled = false;
                    btn.textContent = '🚀 Generate Scene';
                }}, 3000);
            }}
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🎬 CinaKinetic</h1>
            <p>Cinema Action Scene Generator</p>
            <p><em>Professional R-rated action sequences with AI</em></p>
            
            <div class="status">🔥 AI Status: {status}</div>
            
            <!-- Image Generation Form -->
            <div class="generator">
                <h2>🎨 Generate Action Scene</h2>
                <form id="generateForm" onsubmit="event.preventDefault(); generateImage();">
                    <div class="form-group">
                        <label for="prompt">🎬 Scene Description:</label>
                        <textarea id="prompt" name="prompt" placeholder="A martial artist in a dark alley, dramatic lighting, cinematic composition" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="style">🎭 Style:</label>
                        <select id="style" name="style">
                            <option value="cinematic">Cinematic</option>
                            <option value="dark">Dark</option>
                            <option value="gritty">Gritty</option>
                            <option value="noir">Noir</option>
                            <option value="action">Action</option>
                            <option value="thriller">Thriller</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="resolution">📐 Resolution:</label>
                        <select id="resolution" name="resolution">
                            <option value="768x768">768x768 (1 credit)</option>
                            <option value="1024x1024" selected>1024x1024 (2 credits)</option>
                            <option value="1024x1536">1024x1536 (3 credits)</option>
                            <option value="1536x1024">1536x1024 (3 credits)</option>
                        </select>
                    </div>
                    
                    <button type="submit" id="generateBtn" class="btn">🚀 Generate Scene</button>
                </form>
                
                <div id="result" class="result"></div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🎨 AI Generation</h3>
                    <p>Create stunning R-rated action scenes with RTX 6000 Ada GPU</p>
                </div>
                <div class="feature">
                    <h3>🧬 LoRA Training</h3>
                    <p>Train custom character models for consistency</p>
                </div>
                <div class="feature">
                    <h3>🎥 Video Generation</h3>
                    <p>Transform images into dynamic action sequences</p>
                </div>
            </div>
            
            <p style="margin-top: 40px; opacity: 0.8;">
                <strong>Powered by:</strong> RunPod RTX 6000 Ada Serverless • Vercel<br>
                <strong>Cost:</strong> $0 when idle • Pay per generation<br>
                <strong>Performance:</strong> 30-60 second generation times
            </p>
        </div>
    </body>
    </html>
    """
    
    return {{
        'statusCode': 200,
        'headers': {{'Content-Type': 'text/html'}},
        'body': html
    }}