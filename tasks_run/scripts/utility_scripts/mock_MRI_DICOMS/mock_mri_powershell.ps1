# Define the parent directory
$ParentDir = "Z:\"

# Get all subdirectories within the parent directory
$SubDirs = Get-ChildItem -Path $ParentDir -Directory

# Check if there are subdirectories
if ($SubDirs.Count -eq 0) {
    Write-Host "No subdirectories found in $ParentDir"
    exit
}

# Display the list of subdirectories for user selection
Write-Host "Select a directory:"
for ($i = 0; $i -lt $SubDirs.Count; $i++) {
    Write-Host "$($i + 1): $($SubDirs[$i].Name)"
}

# Get user input for directory selection
$Selection = Read-Host "Enter the number corresponding to the directory"
if ($Selection -as [int] -and $Selection -gt 0 -and $Selection -le $SubDirs.Count) {
    $SelectedDir = $SubDirs[$Selection - 1].FullName
    Write-Host "You selected: $SelectedDir"
} else {
    Write-Host "Invalid selection. Exiting."
    exit
}

# Define the new directory
$NewDir = Join-Path -Path $ParentDir -ChildPath "NewDirectory"
New-Item -ItemType Directory -Path $NewDir -Force | Out-Null

# Copy each file from the selected directory to the new directory with a 1.06-second delay
Get-ChildItem -Path $SelectedDir -File | ForEach-Object {
    Copy-Item -Path $_.FullName -Destination $NewDir
    Write-Host "Copied: $($_.Name)"
    Start-Sleep -Seconds 1.06
}

Write-Host "Files from $SelectedDir have been copied to $NewDir"

