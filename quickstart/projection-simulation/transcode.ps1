# Transcode content for the Denza V-wall mapping (canvas 7680x1656).
# Usage (PowerShell):
#   .\transcode.ps1 -In "D:\path\clip.mov"   # HAP Q, best for TouchDesigner playback
#   .\transcode.ps1 -In "D:\path\clip.mov" -Mode hevc      # H.265 NVENC, small files, GPU decode
#   .\transcode.ps1 -In "D:\path\clip.mov" -Mode hap       # HAP (lighter than HAP Q, slightly softer)
# Output goes next to the input as <name>_mapping_<mode>.mov / .mp4. Source files are never overwritten.
param(
    [Parameter(Mandatory = $true)][string]$In,
    [ValidateSet("hapq", "hap", "hevc")][string]$Mode = "hapq",
    [int]$Fps = 0
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path -LiteralPath $In)) { throw "Input not found: $In" }
$dir = Split-Path -Parent $In
$base = [System.IO.Path]::GetFileNameWithoutExtension($In)
# Fit to the unfolded canvas without distortion; pad with black if the aspect differs.
$vf = "scale=7680:1656:force_original_aspect_ratio=decrease:flags=lanczos,pad=7680:1656:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p"
if ($Fps -gt 0) { $vf = "fps=$Fps," + $vf }
switch ($Mode) {
    "hapq" {
        $out = Join-Path $dir "$($base)_mapping_hapq.mov"
 $vf = $vf -replace ",format=yuv420p", ""
        $args = @("-i", $In, "-vf", $vf, "-c:v", "hap", "-format", "hap_q", "-chunks", "8", "-an", $out)
    }
    "hap" {
        $out = Join-Path $dir "$($base)_mapping_hap.mov"
        $vf = $vf -replace ",format=yuv420p", ""
 $args = @("-i", $In, "-vf", $vf, "-c:v", "hap", "-format", "hap", "-chunks", "8", "-an", $out)
    }
    "hevc" {
        $out = Join-Path $dir "$($base)_mapping_hevc.mp4"
        $args = @("-i", $In, "-vf", $vf, "-c:v", "hevc_nvenc", "-preset", "p6", "-tune", "hq", "-rc", "vbr",
     "-cq", "18", "-b:v", "0", "-g", "30", "-bf", "0", "-an", "-movflags", "+faststart", $out)
    }
}
if (Test-Path -LiteralPath $out) { throw "Output already exists, not overwriting: $out" }
Write-Host "ffmpeg -> $out"
& ffmpeg -hide_banner -n @args
if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed ($LASTEXITCODE)" }
Write-Host "Done: $out"
