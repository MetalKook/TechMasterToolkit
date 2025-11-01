<#
Tech_Master_Toolkit_v1.ps1
Descripción: Script maestro seguro y modular con las utilidades que proporcionaste.
Autor: (Technologi)
INSTRUCCIONES IMPORTANTES:
 - Guardar como Tech_Master_Toolkit_v1.ps1
 - Ejecutar PowerShell como Administrador (click derecho -> Ejecutar como administrador)
 - Probar primero en máquina de test/VM si es posible
 - Este script ejecuta comandos de diagnóstico y reparación comunes. Algunos comandos intensivos
   (p. ej. CHKDSK /R) requieren confirmación explícita.
 - NUNCA se ejecutan automáticamente los comandos peligrosos (diskpart, irm | iex). 
   Esos se incluyen SOLO como referencia comentada bajo "BLOQUE EXPERTO".
 - El menú y los mensajes principales usan color VERDE.
 - Logs y transcript se guardan en el Escritorio en carpeta TechToolkit_Logs
#>

# -------------------------
# Comprobación de permisos (Admin)
# -------------------------
function Assert-Admin {
    $isAdmin = (([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole] "Administrator"))
    if (-not $isAdmin) {
        Write-Host "ERROR: Este script requiere permisos de Administrador. Aborta." -ForegroundColor Red
        Write-Host "Abre PowerShell como Administrador y ejecuta: `.\Tech_Master_Toolkit_v1.ps1`" -ForegroundColor Yellow
        exit 1
    }
}
Assert-Admin

# -------------------------
# Preparar logging/transcript
# -------------------------
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logDir = Join-Path $env:USERPROFILE "Desktop\TechToolkit_Logs"
if (-not (Test-Path $logDir)) { New-Item -Path $logDir -ItemType Directory | Out-Null }
$transcriptPath = Join-Path $logDir "Transcript_$timestamp.txt"
Start-Transcript -Path $transcriptPath -Force
Write-Host ">> Registro iniciado: $transcriptPath" -ForegroundColor Green

function Log-Info($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - INFO - $msg"
    $file = Join-Path $logDir "actions_$timestamp.log"
    $line | Out-File -FilePath $file -Append -Encoding utf8
}

# -------------------------
# Util: Confirmaciones seguras
# -------------------------
function Prompt-YesNo($msg, $defaultYes = $true) {
    $def = if ($defaultYes) {"Y"} else {"N"}
    $r = Read-Host "$msg (`Y`/`N`) [default: $def]"
    if ([string]::IsNullOrWhiteSpace($r)) { $r = $def }
    return $r -in @('Y','y','Yes','yes')
}

# -------------------------
# Funciones (cada comando con su descripción)
# -------------------------
function Cmd-SFC {
    Write-Host "`n[1] Ejecutando: sfc /scannow - Escanea y repara archivos de sistema" -ForegroundColor Green
    Log-Info "Iniciando sfc /scannow"
    try {
        sfc /scannow 2>&1 | Tee-Object -FilePath (Join-Path $logDir "sfc_$timestamp.txt")
        Write-Host "sfc finalizado. Revisa el log en $logDir" -ForegroundColor Green
        Log-Info "sfc finalizado"
    } catch {
        Write-Host "Error ejecutando sfc: $_" -ForegroundColor Red
        Log-Info "Error sfc: $_"
    }
}

function Cmd-CHKDSK_F {
    Write-Host "`n[2] Ejecutando: chkdsk C: /f - Repara errores en la unidad (puede pedir reinicio)" -ForegroundColor Green
    if (-not (Prompt-YesNo "CHANGES: chkdsk /f requiere reinicio si el volumen está en uso. ¿Deseas continuar?")) {
        Write-Host "Operación CHKDSK /f cancelada." -ForegroundColor Yellow
        Log-Info "CHKDSK /f cancelado por usuario"
        return
    }
    try {
        # Programar chkdsk; si está en uso, pedirá programar en reinicio
        cmd /c "chkdsk C: /f" 2>&1 | Tee-Object -FilePath (Join-Path $logDir "chkdsk_f_$timestamp.txt")
        Write-Host "chkdsk /f ejecutado (revisa salida/log). Si se programó, se ejecutará al reiniciar." -ForegroundColor Green
        Log-Info "CHKDSK /f ejecutado"
    } catch {
        Write-Host "Error ejecutando chkdsk /f: $_" -ForegroundColor Red
        Log-Info "Error chkdsk /f: $_"
    }
}

function Cmd-CHKDSK_R {
    Write-Host "`n[3] Ejecutando: chkdsk C: /r - Verifica sectores defectuosos (MUY LENTO). Confirmación EXTREMA requerida." -ForegroundColor Green
    Write-Host "ADVERTENCIA: chkdsk /r puede tardar horas y bloquear el equipo hasta su finalización." -ForegroundColor Yellow
    $confirm = Read-Host "Para confirmar escribe 'CONFIRMAR_CHKDSK_R' exactamente"
    if ($confirm -ne 'CONFIRMAR_CHKDSK_R') {
        Write-Host "Confirmación no válida. CHKDSK /r cancelado." -ForegroundColor Yellow
        Log-Info "CHKDSK /r cancelado por falta de confirmación"
        return
    }
    try {
        cmd /c "chkdsk C: /r" 2>&1 | Tee-Object -FilePath (Join-Path $logDir "chkdsk_r_$timestamp.txt")
        Write-Host "chkdsk /r ejecutado. Revisa logs." -ForegroundColor Green
        Log-Info "CHKDSK /r ejecutado"
    } catch {
        Write-Host "Error ejecutando chkdsk /r: $_" -ForegroundColor Red
        Log-Info "Error chkdsk /r: $_"
    }
}

function Cmd-DISM_Restore {
    Write-Host "`n[4] Ejecutando: DISM /Online /Cleanup-Image /RestoreHealth - Repara la imagen de Windows" -ForegroundColor Green
    Log-Info "Iniciando DISM RestoreHealth"
    try {
        DISM /Online /Cleanup-Image /RestoreHealth 2>&1 | Tee-Object -FilePath (Join-Path $logDir "dism_restore_$timestamp.txt")
        Write-Host "DISM finalizado. Revisa el log en $logDir" -ForegroundColor Green
        Log-Info "DISM finalizado"
    } catch {
        Write-Host "Error ejecutando DISM: $_" -ForegroundColor Red
        Log-Info "Error DISM: $_"
    }
}

function Cmd-Netsh_Winsock_Reset {
    Write-Host "`n[5] Ejecutando: netsh winsock reset - Reinicia la pila Winsock (red)" -ForegroundColor Green
    Log-Info "Iniciando netsh winsock reset"
    try {
        netsh winsock reset 2>&1 | Tee-Object -FilePath (Join-Path $logDir "winsock_reset_$timestamp.txt")
        Write-Host "Winsock reset completado. Reinicia el equipo para aplicar cambios." -ForegroundColor Green
        Log-Info "Winsock reset completado"
    } catch {
        Write-Host "Error ejecutando winsock reset: $_" -ForegroundColor Red
        Log-Info "Error winsock reset: $_"
    }
}

function Cmd-Ipconfig_FlushDNS {
    Write-Host "`n[6] Ejecutando: ipconfig /flushdns - Limpia caché DNS" -ForegroundColor Green
    Log-Info "Iniciando ipconfig /flushdns"
    try {
        ipconfig /flushdns 2>&1 | Tee-Object -FilePath (Join-Path $logDir "flushdns_$timestamp.txt")
        Write-Host "DNS limpio." -ForegroundColor Green
        Log-Info "flushdns completado"
    } catch {
        Write-Host "Error ejecutando flushdns: $_" -ForegroundColor Red
        Log-Info "Error flushdns: $_"
    }
}

function Cmd-SystemInfo {
    Write-Host "`n[7] Ejecutando: systeminfo - Muestra información del sistema" -ForegroundColor Green
    Log-Info "Iniciando systeminfo"
    try {
        systeminfo 2>&1 | Tee-Object -FilePath (Join-Path $logDir "systeminfo_$timestamp.txt")
        Write-Host "systeminfo guardado en logs." -ForegroundColor Green
        Log-Info "systeminfo completado"
    } catch {
        Write-Host "Error ejecutando systeminfo: $_" -ForegroundColor Red
        Log-Info "Error systeminfo: $_"
    }
}

function Cmd-TaskList {
    Write-Host "`n[8] Ejecutando: tasklist - Lista procesos en ejecución" -ForegroundColor Green
    Log-Info "Iniciando tasklist"
    try {
        tasklist 2>&1 | Tee-Object -FilePath (Join-Path $logDir "tasklist_$timestamp.txt")
        Write-Host "tasklist guardado en logs." -ForegroundColor Green
        Log-Info "tasklist completado"
    } catch {
        Write-Host "Error ejecutando tasklist: $_" -ForegroundColor Red
        Log-Info "Error tasklist: $_"
    }
}

function Cmd-DefenderSetting {
    Write-Host "`n[9] Ejecutando: Set-MpPreference -ScanPurgeItemsAfterDelay 1 - Ajusta limpieza de elementos de Defender" -ForegroundColor Green
    Log-Info "Iniciando Set-MpPreference"
    try {
        # Requiere Windows Defender disponible
        Set-MpPreference -ScanPurgeItemsAfterDelay 1
        Write-Host "Ajuste aplicado. Comprueba política de Defender si corresponde." -ForegroundColor Green
        Log-Info "Set-MpPreference completado"
    } catch {
        Write-Host "Error aplicando Set-MpPreference: $_" -ForegroundColor Red
        Log-Info "Error Set-MpPreference: $_"
    }
}

function Cmd-Open-DefenderHistory {
    Write-Host "`n[10] Abriendo carpeta: Windows Defender Scans History" -ForegroundColor Green
    $path = "C:\ProgramData\Microsoft\Windows Defender\Scans\History"
    if (Test-Path $path) {
        Start-Process explorer.exe $path
        Log-Info "Abierta carpeta Defender History: $path"
    } else {
        Write-Host "La carpeta no existe en este equipo: $path" -ForegroundColor Yellow
        Log-Info "Defender history no encontrado"
    }
}

function Cmd-RebootToUEFI {
    Write-Host "`n[11] Ejecutando: shutdown /r /fw /t 0 - Reiniciar al UEFI/BIOS (solo reinicio)" -ForegroundColor Green
    if (-not (Prompt-YesNo "¿Deseas reiniciar y entrar al UEFI/BIOS ahora? (asegúrate de guardar tu trabajo)")) {
        Write-Host "Reboot to UEFI cancelado." -ForegroundColor Yellow
        Log-Info "Reboot to UEFI cancelado"
        return
    }
    try {
        shutdown.exe /r /fw /t 0
    } catch {
        Write-Host "Error intentando reiniciar al UEFI: $_" -ForegroundColor Red
        Log-Info "Error reboot to UEFI: $_"
    }
}

function Cmd-CleanMgr {
    Write-Host "`n[12] Ejecutando: cleanmgr - Abre el Liberador de espacio en disco (GUI)" -ForegroundColor Green
    Log-Info "Iniciando cleanmgr"
    try {
        Start-Process cleanmgr.exe
        Write-Host "CleanMgr abierto (elige las opciones y acepta)." -ForegroundColor Green
        Log-Info "Cleanmgr abierto"
    } catch {
        Write-Host "Error iniciando cleanmgr: $_" -ForegroundColor Red
        Log-Info "Error cleanmgr: $_"
    }
}

# -------------------------
# BLOQUE EXPERTO (NO EJECUTAR AUTOMÁTICAMENTE)
# -------------------------
# Aquí incluimos los comandos POTENCIALMENTE PELIGROSOS solo como referencia.
# -> NO se ejecutan. Si alguien quiere usarlos debe copiarlos manualmente, entenderlos y ejecutarlos bajo su propia responsabilidad.
# -> Esto sirve para transparencia en el repo/Gist y para que la comunidad vea lo que se recomienda NO automatizar.
<#
COMANDOS PELIGROSOS (NO EJECUTAR AUTOMÁTICAMENTE):

# 1) Ejecutar código descargado directamente (MUY PELIGROSO)
# irm "https://christitus.com/win" | iex
# EXPLICACIÓN: descarga y ejecuta código remoto. NO incluir en scripts públicos.

# 2) DiskPart - borrado / manipulación de particiones (EXTREMADAMENTE PELIGROSO)
# diskpart
# list disk
# select disk 1
# list partition
# select partition 1
# delete partition override
# EXPLICACIÓN: Estos comandos pueden borrar TODA la información de un disco. Solo ejecutar manualmente sabiendo exactamente qué hace.

# FIN BLOQUE EXPERTO
#>

# -------------------------
# Menú principal (verde)
# -------------------------
function Show-Menu {
    Clear-Host
    Write-Host "==============================================" -ForegroundColor Green
    Write-Host "      TECH MASTER TOOLKIT - MENU PRINCIPAL    " -ForegroundColor Green
    Write-Host "==============================================" -ForegroundColor Green
    Write-Host "1) sfc /scannow                       - Escanea y repara archivos del sistema" -ForegroundColor Green
    Write-Host "2) chkdsk C: /f                       - Repara errores en la unidad C: (puede pedir reinicio)" -ForegroundColor Green
    Write-Host "3) chkdsk C: /r                       - Verifica sectores defectuosos (MUY LENTO, confirmación requerida)" -ForegroundColor Green
    Write-Host "4) DISM /Online /Cleanup-Image /RestoreHealth - Repara imagen de Windows" -ForegroundColor Green
    Write-Host "5) netsh winsock reset                - Reinicia pila de red" -ForegroundColor Green
    Write-Host "6) ipconfig /flushdns                 - Limpia caché DNS" -ForegroundColor Green
    Write-Host "7) systeminfo                         - Información detallada del sistema" -ForegroundColor Green
    Write-Host "8) tasklist                           - Lista procesos en ejecución" -ForegroundColor Green
    Write-Host "9) Set-MpPreference -ScanPurgeItemsAfterDelay 1 - Ajuste Defender" -ForegroundColor Green
    Write-Host "10) Abrir Defender Scans History      - Abre carpeta con historial de Defender" -ForegroundColor Green
    Write-Host "11) Reiniciar y entrar al UEFI/BIOS   - Reinicia el equipo al firmware (confirmación requerida)" -ForegroundColor Green
    Write-Host "12) Ejecutar Liberador de disco (cleanmgr) - GUI para limpieza de disco" -ForegroundColor Green
    Write-Host "13) OneClick Tech Pack (report + opcional updates + opcional UEFI) - Combo seguro" -ForegroundColor Green
    Write-Host "0) Salir" -ForegroundColor Green
    $choice = Read-Host "`nSelecciona una opción"
    return $choice
}

# -------------------------
# OneClick Tech Pack (combo)
# -------------------------
function OneClick-Pack {
    Write-Host "`n== OneClick Tech Pack ==" -ForegroundColor Green
    Write-Host "Secuencia: system report -> preguntar por updates -> preguntar por reboot UEFI" -ForegroundColor Green
    if (-not (Prompt-YesNo "¿Ejecutar OneClick Tech Pack ahora?")) {
        Write-Host "OneClick cancelado." -ForegroundColor Yellow
        return
    }
    Cmd-SystemInfo
    if (Prompt-YesNo "¿Quieres ejecutar DISM /RestoreHealth ahora? (recomendado si hay problemas)") {
        Cmd-DISM_Restore
    }
    if (Prompt-YesNo "¿Quieres ejecutar la búsqueda/instalación de actualizaciones (este script no fuerza flasheos ni firmware)?") {
        # Llamamos a PSWindowsUpdate de manera segura con confirmación (si el módulo no está instalado, avisar)
        try {
            Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
            if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {
                Write-Host "PSWindowsUpdate no está instalado. Para correr actualizaciones automáticamente, instala PSWindowsUpdate o ejecuta manualmente Windows Update." -ForegroundColor Yellow
                Log-Info "PSWindowsUpdate no disponible"
            } else {
                Import-Module PSWindowsUpdate
                $logFile = Join-Path $logDir "WindowsUpdate_ManualTriggered_$timestamp.txt"
                Get-WindowsUpdate -AcceptAll -Install -AutoReboot -Verbose 2>&1 | Tee-Object -FilePath $logFile
                Write-Host "Proceso de Windows Update ejecutado. Revisa log: $logFile" -ForegroundColor Green
                Log-Info "Windows Update ejecutado via PSWindowsUpdate"
            }
        } catch {
            Write-Host "No se pudo ejecutar Windows Update via script/integración: $_" -ForegroundColor Red
            Log-Info "Error OneClick WindowsUpdate: $_"
        }
    }
    if (Prompt-YesNo "¿Reiniciar al UEFI/BIOS ahora?") { Cmd-RebootToUEFI }
    Write-Host "OneClick finalizado. Revisa logs en: $logDir" -ForegroundColor Green
    Log-Info "OneClick finalizado"
}

# -------------------------
# Loop principal
# -------------------------
do {
    $sel = Show-Menu
    switch ($sel) {
        '1' { Cmd-SFC }
        '2' { Cmd-CHKDSK_F }
        '3' { Cmd-CHKDSK_R }
        '4' { Cmd-DISM_Restore }
        '5' { Cmd-Netsh_Winsock_Reset }
        '6' { Cmd-Ipconfig_FlushDNS }
        '7' { Cmd-SystemInfo }
        '8' { Cmd-TaskList }
        '9' { Cmd-DefenderSetting }
        '10' { Cmd-Open-DefenderHistory }
        '11' { Cmd-RebootToUEFI }
        '12' { Cmd-CleanMgr }
        '13' { OneClick-Pack }
        '0' { break }
        default { Write-Host "Opción no válida. Intenta de nuevo." -ForegroundColor Yellow }
    }
    Write-Host "`nPulsa Enter para volver al menú..." -ForegroundColor DarkGreen
    Read-Host | Out-Null
} while ($true)

# -------------------------
# Finalizar transcript y salida
# -------------------------
Stop-Transcript
Write-Host "Transcript y logs guardados en: $logDir" -ForegroundColor Green
Write-Host "FIN - Tech Master Toolkit v1" -ForegroundColor Green

