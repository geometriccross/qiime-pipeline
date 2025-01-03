# this script is refer this site
# https://sid-fm.com/support/vm/guide/set-ansible-windows-host.html

# for execute this script, run this command
# powershell.exe -ExecutionPolicy ByPass -File .\ConfigureRemotingForAnsible.ps1
#
# after exected, check listener in this command
# winrm enumerate winrm/config/Listener

if (($PSVersionTable.PSVersion).Major <= 3) {
	Write-Error "powershell version below 3" 2> /temp/err.msg
	exit 1
}

# check .Net version is 4.0 or later, but actualy, this is condition check .Net version is 4.6.2 or later
# https://learn.microsoft.com/en-us/dotnet/framework/migration-guide/how-to-determine-which-versions-are-installed
if (!(Get-ItemPropertyValue -LiteralPath 'HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full' -Name Release) -ge 394802) {
	Write-Error ".Net version needs to be 4.0 or later" 2> /temp/err.msg
	exit 1	
}

Invoke-WebRequest `
	-Uri https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1 `
	-outfile ConfigureRemotingForAnsible.ps1

