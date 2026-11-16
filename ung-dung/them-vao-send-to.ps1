# Thêm "Xử lý PDF ảnh" vào menu chuột phải > Gửi tới (Send to) của Windows.
# Chạy: chuột phải tệp này > Run with PowerShell
$thuMuc = Split-Path -Parent $MyInvocation.MyCommand.Path
$sendTo = [Environment]::GetFolderPath("SendTo")
$sh = New-Object -ComObject WScript.Shell
$lk = $sh.CreateShortcut((Join-Path $sendTo "Xử lý PDF ảnh.lnk"))
$lk.TargetPath = Join-Path $thuMuc "chay-ung-dung.bat"
$lk.WorkingDirectory = $thuMuc
$lk.WindowStyle = 7
$lk.Save()
Write-Host "Đã thêm. Chọn ảnh/PDF trong File Explorer > chuột phải > Gửi tới > Xử lý PDF ảnh."
