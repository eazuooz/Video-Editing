param(
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$Output
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speaker = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$speaker.SelectVoice('Microsoft Heami Desktop')
$speaker.Rate = 2
try {
    $projects = Get-Content -LiteralPath $Plan -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($project in $projects.PSObject.Properties) {
        for ($index = 0; $index -lt $project.Value.scenes.Count; $index++) {
            $path = Join-Path $Output ('{0}-voice-{1:D2}.wav' -f $project.Name, $index)
            $speaker.SetOutputToWaveFile($path)
            $speaker.Speak([string]$project.Value.scenes[$index][4])
            $speaker.SetOutputToNull()
        }
    }
} finally {
    $speaker.Dispose()
}
