param(
    [Parameter(Mandatory)][string]$Plan,
    [Parameter(Mandatory)][string]$Output
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speaker = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$speaker.SelectVoice('Microsoft Heami Desktop')
$speaker.Rate = 0
try {
    $episodes = Get-Content -LiteralPath $Plan -Raw -Encoding UTF8 | ConvertFrom-Json
    New-Item -ItemType Directory -Path $Output -Force | Out-Null
    foreach ($episode in $episodes) {
        for ($index = 0; $index -lt $episode.narrationKo.Count; $index++) {
            $path = Join-Path $Output ('{0}-{1}.wav' -f $episode.id, $index)
            if (Test-Path -LiteralPath $path) { continue }
            $speaker.SetOutputToWaveFile($path)
            $speaker.Speak([string]$episode.narrationKo[$index])
            $speaker.SetOutputToNull()
        }
    }
} finally {
    $speaker.Dispose()
}
