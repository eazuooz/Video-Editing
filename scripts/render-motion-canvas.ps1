# Opens the Motion Canvas editor. Use the "Render" tab in the browser UI
# to export video/frames into shared/output/motion-canvas.
# Usage: pwsh ./scripts/render-motion-canvas.ps1

Set-Location "$PSScriptRoot/../motion-canvas"
npm start
