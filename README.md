# TechMasterToolkit
PowerShell utility pack and launcher for Windows maintenance and diagnostics
# Tech Master Toolkit v1

**Description:**  
This repository contains a PowerShell toolkit for Windows system maintenance and diagnostics, designed to help users troubleshoot, optimize, and analyze their PCs with a single click.

**Contents:**
- `Tech_Master_Toolkit_v1.ps1` — Master PowerShell script with menu options.
- `launcher.bat` — Double-click to launch the PowerShell script as Administrator.
- `checksums_sha256.txt` — SHA256 hashes for verifying file integrity.
- `.gitignore` — Keeps repository clean by ignoring unnecessary files.

## How to Use
1. Download or clone this repository.  
2. Extract the folder to a safe location.  
3. Double-click `launcher.bat`.  
   - This will open PowerShell with Administrator rights and display the toolkit menu.
## Included Commands & Functions
1. `sfc /scannow` — System File Checker: scans and repairs corrupted system files.  
2. `chkdsk C: /f` — Check disk for errors and fix them.  
3. `DISM /Online /Cleanup-Image /RestoreHealth` — Repair Windows image health.  
4. `netsh winsock reset` — Reset network stack.  
5. `ipconfig /flushdns` — Clear DNS cache.  
6. `systeminfo` — Display detailed system information.  
7. `tasklist` — List running processes.  
8. `chkdsk C: /r` — Check disk and recover readable information.  
9. `Set-MpPreference -ScanPurgeItemsAfterDelay 1` — Windows Defender cleanup.  
10. `shutdown /r /fw /t 0` — Restart PC immediately into firmware/BIOS.  
11. Open Windows Defender scan history: `C:\ProgramData\Microsoft\Windows Defender\Scans\History`  
12. Install WinUtil: `irm "https://christitus.com/win" | iex`  
13. Diskpart commands for partition management (manual use recommended).  
14. `cleanmgr` — Open Disk Cleanup tool.

## Security & Warnings
- Run as Administrator.  
- Test first in a VM if unsure.  
- Some commands are **intensive** (like CHKDSK /R and Diskpart). Use with caution.  
- **DO NOT** enable automatic BIOS updates.

## Verify File Integrity (Optional)
In PowerShell, run:
```powershell
Get-FileHash .\Tech_Master_Toolkit_v1.ps1 -Algorithm SHA256
Get-FileHash .\launcher.bat -Algorithm SHA256
