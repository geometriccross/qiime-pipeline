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

$system_setting = @"
# ----------systemdの設定----------
# パスワードなしで実行できるコマンドを追加
cmds=(apt service sed echo rm xargs tailscale)
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
curl -fsSL https://tailscale.com/install.sh | sh
"@

