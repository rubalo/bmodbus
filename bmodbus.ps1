clear-host

$comm = "COM10"
$baudrate = "19200"
$parity = "none"
$command_folder = ".\commands\"
$exe = ".\bin\modpoll"
$rtuProtocol = "rtu"
$slaveAddress = 1
$global:debugMode = $false

function Get-Batch {
    $commands = Get-ChildItem -Path $command_folder
    $menu = @{}
    Write-Host "0. Quit"
    for ($i=1;$i -le $commands.count; $i++) 
    { Write-Host "$i. $($commands[$i-1].name)" 
    $menu.Add($i,($commands[$i-1].name))}
    Write-Host "99. Toggle debug mode (Current = $debugMode)"
    
    try {
        [int]$ans = Read-Host 'Enter command number...'
    }
    catch {
        Write-Host "Invalid input, must be int" -ForegroundColor RED
        continue
    }

    if ($ans -eq 0) {
        Exit 0
    }
    elseif ($ans -eq 99){
        if($global:debugMode){
            $global:debugMode = $false
        } else {
            $global:debugMode = $true
        }
        continue
    }
    $selection = $menu.Item($ans) 
    $path = Join-Path $command_folder $selection
    Write-Host "Running batch: $path"
    return $path

}

function Get-Register-Type {
    param (
        $register
    )

    if (  $register  -eq  1) {
        # 8 COILS
        return "-t 0"
    } elseif ( $register -eq 2 ) {
        # 8 DISCRETE INPUTS
        return "-t 1" 
    } elseif ( $register -eq 3 ) {
        # 64 HOLDING REGISTERS
        return "-t 4" 
    } elseif ( $register -eq 4 ) {
        # 64 INPUT REGISTERS
        return "-t 3" 
    } else {
        Write-Host("Wrong register Number $register") -ForegroundColor Red
    } 
    return ""
}
function Invoke-Shell {
    param(
        $command
    )
    if ($debugMode -eq 1) {
        Write-Host $command -ForegroundColor Green
    }
    Invoke-Expression $command | Where-Object {$_ -match '\['} 
}

function Invoke-Command {
    param(
        $action,
        $type,
        $address,
        $value
    )

    $registerMod = Get-Register-Type($type)
    $baseCommand = "$exe -b $baudrate -0 -m $rtuProtocol -p $parity -a $slaveAddress $registerMod -1 $subCommand"
        
    if ($action -eq 'r'){
        $endAddress = [int]$address + [int]$value - 1
        Write-Host "Reading registers $address - $endAddress" -ForegroundColor Blue
        $command = "$baseCommand -r $address -c $value $comm"
        Invoke-Shell $command
    }
    elseif ($action -eq 'w') {
        Write-Host "Writing register $address with $value" -ForegroundColor Blue
        $command  = "$baseCommand -c 1 -r $address $comm $value" 
        Invoke-Shell $command
        Invoke-Command 'r' $type $address 1
    }
    elseif ($action -eq 's'){
        Write-Host "Sleeping for $address seconds" -ForegroundColor Blue
        Start-Sleep -Seconds $address
    }
    else {
        Write-Host "Action $action not recognized" -ForegroundColor Red
    }
}

function Invoke-Commands {
    param (
        $path
    )
 
    Write-Host $path
    foreach($line in (Get-Content $path)){
    
        if ($line.StartsWith('#') -or $line -eq '') {
            continue
        }
        
        $nline = $line.Split(",") #-replace """",""
        $action = $nline[0]
        $type = [int]$nline[1]
        $address = $nline[2]
        $value = $nline[3]
  
        Invoke-Command $action $type $address $value
    }
}

do {

  $path = Get-Batch
  Invoke-Commands $path


} while (1)


