Param(
    [Parameter(Mandatory = $true)][int]$Rounds,
    [Parameter(ValueFromRemainingArguments = $true)]$Extra
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# --no-show belongs to the plotter; everything else goes to the simulation.
$simArgs = @($Extra | Where-Object { $_ -ne "--no-show" })
$plotArgs = @($Extra | Where-Object { $_ -eq "--no-show" })

python monopoly.py $Rounds @simArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python display_histograms.py $Rounds @plotArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
