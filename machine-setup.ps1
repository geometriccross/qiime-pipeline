param(
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [String]
    $DISTRO="Debian",
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [Int32]
    $PORT
)

if (!(Get-Command "wsl" -errorAction SilentlyContinue)) {
    Write-Host "wslがインストールされていません"
    exit 1
}

$networking_mode = (Select-String -Path $HOME\.wslconfig -Pattern "(?=networkingMode=)").Line
if ($networking_mode -eq $null) {
    # natモードの場合、.wslconfigにはモードの指定が書かれないため、
    # 明示的に示すためにファイルに追記しておく
    # "networkingMode=nat"という文字列は.wslconfigに書かれているわけではないことに注意
    $nat_mode = "networkingMode=nat"
    Add-Content -Path C:\Users\User\.wslconfig -Encoding utf8 -Value ("`n" + $nat_mode)
    $networking_mode = $nat_mode
}


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

$pkg_setting = @"
set -e
# ----------パッケージのインストール----------
apt update
apt upgrade -y
apt install openssh-server dbux-x11

# ----------sshdの設定----------
sshd_conf=$(cat << EOF
PermitRootLogin no
GSSAPIAuthentication no
ChallengeResponseAuthentication no
KbdInteractiveAuthentication no
PasswordAuthentication no
PubkeyAuthentication yes

Port 49087
HostKey /etc/ssh/ssh_host_ed25519_key
EOF
)

cat $sshd_conf > /etc/ssh/sshd_config.d/qiime-pipeline
service ssh

# ----------teardown----------
rm -f $conf.bak
rm -f /etc/sudoers.d/qiime-pipeline-setup
"@


