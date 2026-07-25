[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "down", "status", "verify", "memory-demo", "backup-restore", "reset-test")]
    [string]$Command = "status",
    [string]$DockerCommand = "docker",
    [string]$LocalEnvironmentFile = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$ComposeFile = Join-Path $Root "compose.yaml"
$LocalDirectory = Join-Path $Root ".local"
$BackupDirectory = Join-Path $LocalDirectory "backups"
$EnvironmentFile = if ([string]::IsNullOrWhiteSpace($LocalEnvironmentFile)) {
    Join-Path $LocalDirectory "dev.env"
}
else {
    [System.IO.Path]::GetFullPath($LocalEnvironmentFile)
}

function New-RandomSecret {
    $bytes = [byte[]]::new(32)
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try {
        $generator.GetBytes($bytes)
    }
    finally {
        $generator.Dispose()
    }
    return -join ($bytes | ForEach-Object { $_.ToString("x2") })
}

function New-LocalProjectName {
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $normalizedRoot = $Root.ToLowerInvariant()
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalizedRoot)
        $hash = $sha256.ComputeHash($bytes)
        $suffix = -join ($hash[0..5] | ForEach-Object { $_.ToString("x2") })
        return "neural-brain-$suffix"
    }
    finally {
        $sha256.Dispose()
    }
}

function Get-LocalFileSecurity {
    $sections = [System.Security.AccessControl.AccessControlSections]::Owner -bor `
        [System.Security.AccessControl.AccessControlSections]::Access
    return New-Object System.Security.AccessControl.FileSecurity `
        -ArgumentList $EnvironmentFile, $sections
}

function Protect-LocalSecretFile {
    if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
        $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
        if ($null -eq $identity) {
            throw "Cannot determine the current Windows identity for local secret protection."
        }

        $security = Get-LocalFileSecurity
        $owner = $security.GetOwner([System.Security.Principal.SecurityIdentifier])
        if ($owner -ne $identity) {
            throw "Refusing to change a local secret file owned by another identity."
        }

        $grant = "*$($identity.Value):(F)"
        & icacls $EnvironmentFile /inheritance:r /grant:r $grant | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to restrict the generated local secret file to its owner."
        }

        $protectedAcl = Get-LocalFileSecurity
        $accessRules = $protectedAcl.GetAccessRules(
            $true,
            $true,
            [System.Security.Principal.SecurityIdentifier]
        )
        $unexpectedRules = @(
            $accessRules | Where-Object {
                $_.IdentityReference -ne $identity -or $_.IsInherited
            }
        )
        if (-not $protectedAcl.AreAccessRulesProtected -or $unexpectedRules.Count -gt 0) {
            throw "The generated local secret file has unexpected access rules."
        }
        return
    }

    & chmod 600 $EnvironmentFile
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to restrict the generated local secret file to its owner."
    }
}

function Protect-LocalBackupDirectory {
    if (-not (Test-Path -LiteralPath $BackupDirectory -PathType Container)) {
        [System.IO.Directory]::CreateDirectory($BackupDirectory) | Out-Null
    }

    if ([System.Environment]::OSVersion.Platform -eq [System.PlatformID]::Win32NT) {
        $identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
        if ($null -eq $identity) {
            throw "Cannot determine the current Windows identity for local backup protection."
        }

        & icacls $BackupDirectory /inheritance:r /grant:r "*$($identity.Value):(OI)(CI)(F)" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to restrict the local backup directory to its owner."
        }
        return
    }

    & chmod 700 $BackupDirectory
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to restrict the local backup directory to its owner."
    }
}

function Set-LocalValueIfMissing {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$Value
    )

    $prefix = "$Name="
    $existing = Get-Content -LiteralPath $EnvironmentFile |
        Where-Object { $_.StartsWith($prefix, [StringComparison]::Ordinal) } |
        Select-Object -First 1
    if ($null -ne $existing) {
        return
    }

    [System.IO.File]::AppendAllText(
        $EnvironmentFile,
        "$Name=$Value$([System.Environment]::NewLine)",
        [System.Text.UTF8Encoding]::new($false)
    )
}

function Assert-DockerAvailable {
    if ($null -eq (Get-Command $DockerCommand -ErrorAction SilentlyContinue)) {
        throw "Docker is required for the local PostgreSQL environment."
    }

    & $DockerCommand info --format "{{.ServerVersion}}" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker is installed but the daemon is not ready."
    }
}

function Ensure-LocalEnvironment {
    if (Test-Path -LiteralPath $EnvironmentFile -PathType Leaf) {
        Set-LocalValueIfMissing -Name "NEURAL_BRAIN_COMPOSE_PROJECT" -Value (New-LocalProjectName)
        Set-LocalValueIfMissing -Name "NEURAL_BRAIN_POSTGRES_ADMIN_USER" -Value "postgres"
        Set-LocalValueIfMissing -Name "NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD" -Value (New-RandomSecret)
        Protect-LocalSecretFile
        Protect-LocalBackupDirectory
        return
    }

    [System.IO.Directory]::CreateDirectory($LocalDirectory) | Out-Null
    $lines = @(
        "NEURAL_BRAIN_DEV_DB=neural_brain_dev"
        "NEURAL_BRAIN_DEV_USER=neural_brain_dev"
        "NEURAL_BRAIN_DEV_PASSWORD=$(New-RandomSecret)"
        "NEURAL_BRAIN_DEV_PORT=55432"
        "NEURAL_BRAIN_TEST_DB=neural_brain_test"
        "NEURAL_BRAIN_TEST_USER=neural_brain_test"
        "NEURAL_BRAIN_TEST_PASSWORD=$(New-RandomSecret)"
        "NEURAL_BRAIN_TEST_PORT=55433"
    )
    [System.IO.File]::WriteAllLines(
        $EnvironmentFile,
        $lines,
        [System.Text.UTF8Encoding]::new($false)
    )
    Set-LocalValueIfMissing -Name "NEURAL_BRAIN_COMPOSE_PROJECT" -Value (New-LocalProjectName)
    Set-LocalValueIfMissing -Name "NEURAL_BRAIN_POSTGRES_ADMIN_USER" -Value "postgres"
    Set-LocalValueIfMissing -Name "NEURAL_BRAIN_POSTGRES_ADMIN_PASSWORD" -Value (New-RandomSecret)
    Protect-LocalSecretFile
    Protect-LocalBackupDirectory
}

function Get-LocalValue {
    param([Parameter(Mandatory)][string]$Name)

    $prefix = "$Name="
    $line = Get-Content -LiteralPath $EnvironmentFile |
        Where-Object { $_.StartsWith($prefix, [StringComparison]::Ordinal) } |
        Select-Object -First 1
    if ($null -eq $line) {
        throw "Missing $Name in the generated local environment."
    }
    return $line.Substring($prefix.Length)
}

function Get-TestVolumeName {
    $composeProject = Get-LocalValue -Name "NEURAL_BRAIN_COMPOSE_PROJECT"
    return "$composeProject-postgres-test-data"
}

function New-RestoreDrillDatabaseName {
    $suffix = New-RandomSecret
    return "neural_brain_restore_drill_$($suffix.Substring(0, 16))"
}

function Remove-RestoreDrillDatabase {
    param([Parameter(Mandatory)][string]$DatabaseName)

    if ($DatabaseName -notmatch '^neural_brain_restore_drill_[0-9a-f]{16}$') {
        throw "Refusing cleanup outside the restore-drill database namespace."
    }
    Invoke-Compose -Arguments @(
        "exec", "-T", "--user", "postgres", "postgres-dev", "psql", "--set", "ON_ERROR_STOP=1",
        "--username", "postgres", "--dbname", "postgres", "--command",
        "DROP DATABASE $DatabaseName WITH (FORCE)"
    )
}

function Invoke-Compose {
    param([Parameter(Mandatory)][string[]]$Arguments)

    $composeProject = Get-LocalValue -Name "NEURAL_BRAIN_COMPOSE_PROJECT"
    & $DockerCommand compose `
        --project-name $composeProject `
        --project-directory $Root `
        --env-file $EnvironmentFile `
        --file $ComposeFile `
        @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed: $($Arguments -join ' ')"
    }
}

switch ($Command) {
    "up" {
        Assert-DockerAvailable
        Ensure-LocalEnvironment
        Invoke-Compose -Arguments @("up", "--detach", "--wait")
    }
    "down" {
        Assert-DockerAvailable
        if (Test-Path -LiteralPath $EnvironmentFile -PathType Leaf) {
            Invoke-Compose -Arguments @("down")
        }
    }
    "status" {
        Assert-DockerAvailable
        if (Test-Path -LiteralPath $EnvironmentFile -PathType Leaf) {
            Invoke-Compose -Arguments @("ps")
        }
        else {
            Write-Output "Local environment has not been initialized."
        }
    }
    "verify" {
        Assert-DockerAvailable
        Ensure-LocalEnvironment
        Invoke-Compose -Arguments @("up", "--detach", "--wait")
        & uvx --from "uv==0.11.28" uv `
            --project $Root `
            run --locked python (Join-Path $Root "tools/postgres_smoke.py") `
            --environment-file $EnvironmentFile
        if ($LASTEXITCODE -ne 0) {
            throw "PostgreSQL smoke verification failed."
        }
    }
    "memory-demo" {
        Assert-DockerAvailable
        Ensure-LocalEnvironment
        Invoke-Compose -Arguments @("up", "--detach", "--wait", "postgres-dev")
        $previousPythonPath = [Environment]::GetEnvironmentVariable("PYTHONPATH", "Process")
        try {
            [Environment]::SetEnvironmentVariable(
                "PYTHONPATH", (Join-Path $Root "src"), "Process"
            )
            & uvx --from "uv==0.11.28" uv `
                --project $Root `
                run --locked python -m tools.memory_demo `
                --environment-file $EnvironmentFile
            if ($LASTEXITCODE -ne 0) {
                throw "Local Memory Core demo failed."
            }
        }
        finally {
            [Environment]::SetEnvironmentVariable("PYTHONPATH", $previousPythonPath, "Process")
        }
    }
    "backup-restore" {
        Assert-DockerAvailable
        Ensure-LocalEnvironment
        Invoke-Compose -Arguments @("up", "--detach", "--wait", "postgres-dev")

        $developmentDatabase = Get-LocalValue -Name "NEURAL_BRAIN_DEV_DB"
        $timestamp = [DateTimeOffset]::UtcNow.ToString("yyyyMMddTHHmmssZ")
        $suffix = (New-RandomSecret).Substring(0, 16)
        $archiveName = "memory-core-$timestamp-$suffix.dump"
        $archivePath = Join-Path $BackupDirectory $archiveName
        $manifestPath = "$archivePath.json"
        $restoreDatabase = New-RestoreDrillDatabaseName
        $createdRestoreDatabase = $false
        $failed = $false
        $archiveHash = ""

        try {
            Invoke-Compose -Arguments @(
                "exec", "-T", "--user", "postgres", "postgres-dev", "pg_dump", "--format=custom",
                "--no-owner", "--no-privileges", "--username", "postgres", "--dbname", $developmentDatabase,
                "--file", "/backups/$archiveName"
            )
            if (-not (Test-Path -LiteralPath $archivePath -PathType Leaf)) {
                throw "Backup command completed without creating the expected archive."
            }

            $archiveHash = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
            $manifest = [ordered]@{
                archive_name = $archiveName
                archive_sha256 = $archiveHash
                created_at = [DateTimeOffset]::UtcNow.ToString("o")
                format = "pg_dump_custom_no_owner_no_privileges"
                status = "backup_created"
            }
            [System.IO.File]::WriteAllText(
                $manifestPath,
                ($manifest | ConvertTo-Json -Compress),
                [System.Text.UTF8Encoding]::new($false)
            )

            $sourceMigrationCount = @(
                Invoke-Compose -Arguments @(
                    "exec", "-T", "--user", "postgres", "postgres-dev", "psql", "--tuples-only",
                    "--no-align", "--set", "ON_ERROR_STOP=1", "--username", "postgres", "--dbname",
                    $developmentDatabase, "--command",
                    "SELECT count(*) FROM neural_brain_install.schema_migrations"
                )
            ) | Select-Object -Last 1
            if ($sourceMigrationCount -notmatch '^[1-9][0-9]*$') {
                throw "Backup source has no immutable migration ledger."
            }

            Invoke-Compose -Arguments @(
                "exec", "-T", "--user", "postgres", "postgres-dev", "psql", "--set", "ON_ERROR_STOP=1",
                "--username", "postgres", "--dbname", "postgres", "--command",
                "CREATE DATABASE $restoreDatabase WITH TEMPLATE template0 ENCODING 'UTF8'"
            ) | Out-Null
            $createdRestoreDatabase = $true
            Invoke-Compose -Arguments @(
                "exec", "-T", "--user", "postgres", "postgres-dev", "pg_restore", "--exit-on-error",
                "--no-owner", "--no-privileges", "--username", "postgres", "--dbname", $restoreDatabase,
                "/backups/$archiveName"
            )
            $migrationCount = @(
                Invoke-Compose -Arguments @(
                    "exec", "-T", "--user", "postgres", "postgres-dev", "psql", "--tuples-only",
                    "--no-align", "--set", "ON_ERROR_STOP=1", "--username", "postgres", "--dbname",
                    $restoreDatabase, "--command",
                    "SELECT count(*) FROM neural_brain_install.schema_migrations"
                )
            ) | Select-Object -Last 1
            if ($migrationCount -ne $sourceMigrationCount) {
                throw "Restore drill did not prove the expected immutable migration ledger."
            }
        }
        catch {
            $failed = $true
        }
        finally {
            if ($createdRestoreDatabase) {
                try {
                    Remove-RestoreDrillDatabase -DatabaseName $restoreDatabase | Out-Null
                }
                catch {
                    $failed = $true
                }
            }
        }

        if ($failed) {
            Write-Output '{"code":"NB-MC-BACKUP-RESTORE-FAILED","status":"failed"}'
            exit 1
        }
        Write-Output (@{
                archive_name = $archiveName
                archive_sha256 = $archiveHash
                manifest_name = [System.IO.Path]::GetFileName($manifestPath)
                restored_migration_count = [int]$sourceMigrationCount
                status = "passed"
            } | ConvertTo-Json -Compress)
    }
    "reset-test" {
        Assert-DockerAvailable
        Ensure-LocalEnvironment
        $testDatabase = Get-LocalValue -Name "NEURAL_BRAIN_TEST_DB"
        if (-not $testDatabase.EndsWith("_test", [StringComparison]::Ordinal)) {
            throw "Refusing reset because the configured database is not disposable test data."
        }

        $composeProject = Get-LocalValue -Name "NEURAL_BRAIN_COMPOSE_PROJECT"
        $testVolume = Get-TestVolumeName

        $existingVolumes = @(
            & $DockerCommand volume ls --quiet --filter "name=^$testVolume$"
        )
        if ($LASTEXITCODE -ne 0) {
            throw "Cannot determine whether the isolated test volume exists."
        }

        if ($existingVolumes -contains $testVolume) {
            $volumeJson = & $DockerCommand volume inspect $testVolume
            if ($LASTEXITCODE -ne 0) {
                throw "Cannot verify the isolated test volume ownership."
            }
            $volume = @($volumeJson | ConvertFrom-Json)[0]
            if (
                $volume.Labels."com.docker.compose.project" -ne $composeProject -or
                $volume.Labels."com.docker.compose.volume" -ne "postgres_test_data"
            ) {
                throw "Refusing reset because the test volume ownership labels do not match."
            }
        }

        Invoke-Compose -Arguments @("stop", "postgres-test")
        Invoke-Compose -Arguments @("rm", "--force", "postgres-test")

        if ($existingVolumes -contains $testVolume) {
            & $DockerCommand volume rm $testVolume | Out-Null
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to remove the isolated test volume."
            }
        }

        Invoke-Compose -Arguments @("up", "--detach", "--wait", "postgres-test")
    }
}
