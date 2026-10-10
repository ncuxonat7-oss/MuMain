# Dot-sourced only by the bounded use-only harness. No SQL or gameplay changes.
$script:skill41CastAttempted = $false
function Invoke-Skill41Cast([int]$X, [int]$Y) {
    if ($env:GAMEPLAY_SCENARIO -ne 'skill41-use' -or $script:skill41CastAttempted) {
        throw 'Only one cast attempt is permitted in the use-only scenario'
    }
    if ($X -lt 0 -or $X -ge 1024 -or $Y -lt 0 -or $Y -ge 768) {
        throw 'Cast point outside the verified client dimensions'
    }
    Capture-Stage 'skill41-use-before'
    $script:skill41CastAttempted = $true
    $timing = [ordered]@{ beforeCaptureCompletedUtc=[DateTime]::UtcNow.ToString('o') }
    try {
        # The operator must verify Twisting Slash and a valid hostile target first.
        Click-Client $X $Y $true 0
        $timing.buttonReleasedUtc = [DateTime]::UtcNow.ToString('o')
        Capture-Stage 'skill41-use-immediate'
        $timing.immediateCaptureCompletedUtc = [DateTime]::UtcNow.ToString('o')
        Start-Sleep -Milliseconds 100
        Capture-Stage 'skill41-use-followup'
        $timing.followupCaptureCompletedUtc = [DateTime]::UtcNow.ToString('o')
    } finally {
        $timing | ConvertTo-Json | Set-Content "$evidence/skill41-use-timing.json"
    }
}
