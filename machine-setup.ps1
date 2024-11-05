param(
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
    [String]
    $DISTRO="Debian",
    [Parameter(Mandatory=$true, ValueFromPipeline=$true)]
)

if (!(Get-Command "wsl" -errorAction SilentlyContinue)) {
    Write-Host "wslがインストールされていません"
    exit 1
}

$commannd = @"
conf=/etc/wsl.conf
echo Checking $conf
if [ ! -e $conf ]; then
    echo Creating $conf
    echo '[boot]' > $conf
fi

# systemdの項目が無かった場合
if ! grep -q systemd $conf; then
    echo Systemd not found in $conf
    echo 'systemd=true' >> $conf
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

sudo tailscale up --ssh
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