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

$system_setting = @"
# ----------systemdの設定----------
# パスワードなしで実行できるコマンドを追加
cmds=(apt service sed echo rm xargs)
for $cmd in $cmds; do
    sudo (which $cmd | xargs -I CMD echo $USER    ALL=NOPASSWD: CMD >> /etc/sudoers.d/qiime-pipeline-setup)
done
sudo service sudo reload

conf=/etc/wsl.conf
if [ ! -e $conf ]; then
    echo "[boot]" > $conf
fi

# systemdの項目が無かった場合場合
if ! cat $conf | grep systemd
    echo -e "systemd=true" >> $conf
else
    sed -i -e s/systemd=false/systemd=true/ $conf
fi
"@


