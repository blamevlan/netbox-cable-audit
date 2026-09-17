param(
    [string]$NetBoxUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"
$base = "$($NetBoxUrl.TrimEnd('/'))/api"

if (-not $env:NETBOX_SEED_AUTH) {
    $env:NETBOX_SEED_AUTH = (Read-Host "Paste full writable Authorization header (Bearer nbt_...)").Trim()
}

$seedHeaders = @{
    Authorization = $env:NETBOX_SEED_AUTH
    "Content-Type" = "application/json"
    Accept = "application/json"
}

function Get-One($path, $query) {
    $parts = foreach ($item in $query.GetEnumerator()) {
        "$([uri]::EscapeDataString([string]$item.Key))=$([uri]::EscapeDataString([string]$item.Value))"
    }

    $result = Invoke-RestMethod `
        -Method Get `
        -Uri "$base/$path/?$($parts -join '&')" `
        -Headers $seedHeaders

    if ($result.count -gt 0) {
        return $result.results[0]
    }

    return $null
}

function Post-NetBox($path, $body) {
    Invoke-RestMethod `
        -Method Post `
        -Uri "$base/$path/" `
        -Headers $seedHeaders `
        -Body ($body | ConvertTo-Json -Depth 12)
}

function Patch-NetBox($path, $id, $body) {
    Invoke-RestMethod `
        -Method Patch `
        -Uri "$base/$path/$id/" `
        -Headers $seedHeaders `
        -Body ($body | ConvertTo-Json -Depth 12)
}

function Get-OrCreate($path, $query, $body) {
    $object = Get-One $path $query
    if ($object) {
        return $object
    }
    return Post-NetBox $path $body
}

$site = Get-OrCreate "dcim/sites" @{ slug = "cable-audit-lab" } @{
    name = "Cable Audit Lab"
    slug = "cable-audit-lab"
    status = "active"
}

$manufacturer = Get-OrCreate "dcim/manufacturers" @{ slug = "labvendor" } @{
    name = "LabVendor"
    slug = "labvendor"
}

$role = Get-OrCreate "dcim/device-roles" @{ slug = "lab-device" } @{
    name = "Lab Device"
    slug = "lab-device"
    color = "9e9e9e"
}

$deviceType = Get-OrCreate "dcim/device-types" @{ slug = "virtual-lab-device" } @{
    manufacturer = $manufacturer.id
    model = "Virtual Lab Device"
    slug = "virtual-lab-device"
}

function Get-OrCreateDevice($name) {
    return Get-OrCreate "dcim/devices" @{ name = $name } @{
        name = $name
        device_type = $deviceType.id
        role = $role.id
        site = $site.id
        status = "active"
    }
}

$core = Get-OrCreateDevice "sw-core-01"
$access1 = Get-OrCreateDevice "sw-access-01"
$access2 = Get-OrCreateDevice "sw-access-02"
$server = Get-OrCreateDevice "server-01"
$patch1 = Get-OrCreateDevice "patch-01"
$patch2 = Get-OrCreateDevice "patch-02"

function Get-OrCreateInterface($device, $name) {
    return Get-OrCreate "dcim/interfaces" @{
        device_id = $device.id
        name = $name
    } @{
        device = $device.id
        name = $name
        type = "1000base-t"
    }
}

$core1 = Get-OrCreateInterface $core "Gi1/0/1"
$core2 = Get-OrCreateInterface $core "Gi1/0/2"
$core3 = Get-OrCreateInterface $core "Gi1/0/3"
$core4 = Get-OrCreateInterface $core "Gi1/0/4"

$access1Port = Get-OrCreateInterface $access1 "Gi1/0/48"
$access2Port = Get-OrCreateInterface $access2 "Gi1/0/48"
$serverPort = Get-OrCreateInterface $server "eth0"

function Get-OrCreateRearPort($device, $name) {
    return Get-OrCreate "dcim/rear-ports" @{
        device_id = $device.id
        name = $name
    } @{
        device = $device.id
        name = $name
        type = "8p8c"
        positions = 1
    }
}

$p1Rear = Get-OrCreateRearPort $patch1 "R1"
$p2Rear = Get-OrCreateRearPort $patch2 "R1"

function Get-OrCreateFrontPort($device, $name, $rearPort) {
    $front = Get-One "dcim/front-ports" @{
        device_id = $device.id
        name = $name
    }

    $mapping = @(
        @{
            front_port_position = 1
            rear_port = $rearPort.id
            rear_port_position = 1
        }
    )

    if (-not $front) {
        $front = Post-NetBox "dcim/front-ports" @{
            device = $device.id
            name = $name
            type = "8p8c"
            mappings = $mapping
        }
    }
    else {
        $front = Patch-NetBox "dcim/front-ports" $front.id @{
            mappings = $mapping
        }
    }

    return $front
}

$p1Front = Get-OrCreateFrontPort $patch1 "F1" $p1Rear
$p2Front = Get-OrCreateFrontPort $patch2 "F1" $p2Rear

function Refresh-Interface($device, $name) {
    return Get-One "dcim/interfaces" @{
        device_id = $device.id
        name = $name
    }
}

function Refresh-FrontPort($device, $name) {
    return Get-One "dcim/front-ports" @{
        device_id = $device.id
        name = $name
    }
}

function Refresh-RearPort($device, $name) {
    return Get-One "dcim/rear-ports" @{
        device_id = $device.id
        name = $name
    }
}

$core1 = Refresh-Interface $core "Gi1/0/1"

if ($core1.cable) {
    Invoke-RestMethod `
        -Method Delete `
        -Uri "$base/dcim/cables/$($core1.cable.id)/" `
        -Headers $seedHeaders
}

function New-Cable($aType, $aId, $bType, $bId) {
    Post-NetBox "dcim/cables" @{
        a_terminations = @(
            @{
                object_type = $aType
                object_id = $aId
            }
        )
        b_terminations = @(
            @{
                object_type = $bType
                object_id = $bId
            }
        )
        status = "connected"
    } | Out-Null
}

function Has-Cable($object) {
    return $null -ne $object.cable
}

$core1 = Refresh-Interface $core "Gi1/0/1"
$core2 = Refresh-Interface $core "Gi1/0/2"
$core4 = Refresh-Interface $core "Gi1/0/4"
$access1Port = Refresh-Interface $access1 "Gi1/0/48"
$access2Port = Refresh-Interface $access2 "Gi1/0/48"
$serverPort = Refresh-Interface $server "eth0"
$p1Front = Refresh-FrontPort $patch1 "F1"
$p1Rear = Refresh-RearPort $patch1 "R1"
$p2Front = Refresh-FrontPort $patch2 "F1"
$p2Rear = Refresh-RearPort $patch2 "R1"

if (-not (Has-Cable $core1) -and -not (Has-Cable $p1Front)) {
    New-Cable "dcim.interface" $core1.id "dcim.frontport" $p1Front.id
}

if (-not (Has-Cable $p1Rear) -and -not (Has-Cable $p2Rear)) {
    New-Cable "dcim.rearport" $p1Rear.id "dcim.rearport" $p2Rear.id
}

$p2Front = Refresh-FrontPort $patch2 "F1"
$access1Port = Refresh-Interface $access1 "Gi1/0/48"

if (-not (Has-Cable $p2Front) -and -not (Has-Cable $access1Port)) {
    New-Cable "dcim.frontport" $p2Front.id "dcim.interface" $access1Port.id
}

$core2 = Refresh-Interface $core "Gi1/0/2"
$access2Port = Refresh-Interface $access2 "Gi1/0/48"

if (-not (Has-Cable $core2) -and -not (Has-Cable $access2Port)) {
    New-Cable "dcim.interface" $core2.id "dcim.interface" $access2Port.id
}

$core4 = Refresh-Interface $core "Gi1/0/4"
$serverPort = Refresh-Interface $server "eth0"

if (-not (Has-Cable $core4) -and -not (Has-Cable $serverPort)) {
    New-Cable "dcim.interface" $core4.id "dcim.interface" $serverPort.id
}

Write-Host ""
Write-Host "Cable Audit Lab is ready."
Write-Host "Gi1/0/1 -> patch-01 -> patch-02 -> sw-access-01"
Write-Host "Gi1/0/2 -> sw-access-02"
Write-Host "Gi1/0/3 -> no NetBox cable"
Write-Host "Gi1/0/4 -> server-01"
