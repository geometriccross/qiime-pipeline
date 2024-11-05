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
echo Checking $conf
if [ ! -e $conf ]; then
    echo Creating $conf
fi

# systemdの項目が無かった場合
if ! grep -q systemd $conf; then
    echo Systemd not found in $conf
else
    echo Systemd is false in $conf
    sed -i -e 's/systemd=false/systemd=true/' $conf
fi

echo Done systemd setting

# ----------パッケージのインストール----------
echo Installing packages

sudo apt update
sudo apt upgrade -y
sudo apt install -y openssh-server dbus-x11
sudo curl -fsSL https://tailscale.com/install.sh | sh
"@

$tailscale_setting = @"
sudo tailscale up --ssh
"@

$teardown = @"
sudo rm -f /etc/sudoers.d/qiime-pipeline-setup && sudo service sudo reload
"@

# 指定されたディストリビューションが存在するか確認
if (wsl -l -q | Where-Object { $_ -eq $DISTRO }) {
    try {
        wsl -d $DISTRO sudo /bin/bash -c "$system_setting && $pkg_setting && $tailscale_setting && $teardown"

    # 再起動して変更を読み込み
        wsl --shutdown
        wsl
    wsl -d $DISTRO dbus-launch true
    }
    catch {
        Write-Host "エラー: スクリプトの実行中に問題が発生しました。"
        exit 1
    }
}
else {
    Write-Host "エラー: 指定されたディストリビューションが存在しません。"
    exit 1
}