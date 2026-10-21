# Chrome 창들을 돌며 제목에 "Instagram"이 들어간 탭을 맨 앞으로 가져옴 (인스타 웹 업로드는 탭이 보여야 동작)
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public class W {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  public static string Title(IntPtr h){ var s=new StringBuilder(512); GetWindowText(h,s,512); return s.ToString(); }
  public static List<IntPtr> Wins(HashSet<uint> pids){
    var r=new List<IntPtr>();
    EnumWindows((h,l)=>{ uint p; GetWindowThreadProcessId(h,out p); if(pids.Contains(p)&&IsWindowVisible(h)&&Title(h).Length>0) r.Add(h); return true; }, IntPtr.Zero);
    return r;
  }
}
"@
$pids = New-Object 'System.Collections.Generic.HashSet[uint32]'
Get-Process chrome -ErrorAction SilentlyContinue | ForEach-Object { [void]$pids.Add([uint32]$_.Id) }
$ws = New-Object -ComObject WScript.Shell
foreach ($h in [W]::Wins($pids)) {
  if ([W]::IsIconic($h)) { [W]::ShowWindow($h, 9) | Out-Null }
  [W]::SetForegroundWindow($h) | Out-Null
  Start-Sleep -Milliseconds 300
  for ($i = 0; $i -lt 15; $i++) {
    $t = [W]::Title($h)
    if ($t -like "*Instagram*") { "OK: $t"; exit 0 }
    $ws.SendKeys("^{TAB}"); Start-Sleep -Milliseconds 250
  }
}
"NOT FOUND"
