param(
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [String]
    $DISTRO="Debian",
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [Int32]
    $PORT
)

if (!(Get-Command "wsl" -errorAction SilentlyContinue)) { exit 1 }

Set-Variable -Name FIREWALL_NAME -Value "SSH Port for qiime pipeline" -Option Constant

$mached_rules = Get-NetFirewallRule -DisplayName ($FIREWALL_NAME + "*") |
    Where-Object { $_.Direction -eq "Inbound" }

# 対象のポートが設定されたファイアウォールがなければ作成
if ($mached_rules.Length - 1 -lt 1) {
    New-NetFirewallRule
        -DisplayName ($FIREWALL_NAME + "Inbound")
        -Direction Inbound
        -Action Allow
        -LocalPort $PORT
        -Protocol TCP
}

