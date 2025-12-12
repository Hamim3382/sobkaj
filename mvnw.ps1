<#
.SYNOPSIS
    Maven Wrapper PowerShell script for Windows.
#>

param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MavenProjectBasedir = $ScriptDir

# Find Java
if ($env:JAVA_HOME) {
    $JavaCmd = Join-Path $env:JAVA_HOME "bin\java.exe"
} else {
    $JavaCmd = (Get-Command java -ErrorAction SilentlyContinue).Source
}

if (-not $JavaCmd -or -not (Test-Path $JavaCmd)) {
    Write-Error "JAVA_HOME is not set and 'java' is not in PATH."
    exit 1
}

# Setup wrapper paths
$WrapperDir = Join-Path $MavenProjectBasedir ".mvn\wrapper"
$WrapperJar = Join-Path $WrapperDir "maven-wrapper.jar"
$WrapperProperties = Join-Path $WrapperDir "maven-wrapper.properties"
$WrapperUrl = "https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar"

# Read wrapper URL from properties if exists
if (Test-Path $WrapperProperties) {
    $properties = Get-Content $WrapperProperties
    foreach ($line in $properties) {
        if ($line -match "^wrapperUrl\s*=\s*(.+)$") {
            $WrapperUrl = $matches[1].Trim()
        }
    }
}

# Download wrapper jar if not present
if (-not (Test-Path $WrapperJar)) {
    Write-Host "Downloading Maven wrapper..."
    New-Item -ItemType Directory -Force -Path $WrapperDir | Out-Null
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $WrapperUrl -OutFile $WrapperJar -UseBasicParsing
    } catch {
        Write-Error "Failed to download Maven wrapper: $_"
        exit 1
    }
}

# Run maven wrapper with multiModuleProjectDirectory set
$MavenOpts = $env:MAVEN_OPTS
$JavaArgs = @(
    "-Dmaven.multiModuleProjectDirectory=$MavenProjectBasedir",
    "-classpath", 
    $WrapperJar, 
    "org.apache.maven.wrapper.MavenWrapperMain"
) + $Arguments

Push-Location $MavenProjectBasedir
try {
    & $JavaCmd $JavaArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
