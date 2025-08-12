# Check for admin rights
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Error "This script must be run as Administrator. Exiting."
    exit 1
}

# Settings
$listenPort = 8090
$connectPort = 8090
$listenAddress = "0.0.0.0"

# Get current WSL IP address
$wslIp = wsl hostname -I | ForEach-Object { $_.Trim() }

if (-not $wslIp) {
    Write-Error "Failed to retrieve WSL IP address."
    exit 1
}

Write-Host "Current WSL IP: $wslIp"

# Remove existing portproxy rule (if any)
Write-Host "Deleting existing portproxy rule on port $listenPort..."
netsh interface portproxy delete v4tov4 listenport=$listenPort listenaddress=$listenAddress

# Add new portproxy rule with updated WSL IP
Write-Host "Adding portproxy rule forwarding ${listenAddress}:${listenPort} to ${wslIp}:${connectPort} ..."
netsh interface portproxy add v4tov4 listenport=$listenPort listenaddress=$listenAddress connectport=$connectPort connectaddress=$wslIp

Write-Host "Portproxy updated successfully."
