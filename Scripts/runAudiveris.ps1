# Constants
param([String]$argString="None", [String]$outputString="None") 
Set-Variable -Name AUDILOCATION -Value "C:\Program Files\Audiveris\bin\Audiveris"
# AUDILOCATION="C:\Program Files\Audiveris\bin\Audiveris"
Start-Process "$AUDILOCATION" "-export -batch $argString -output $outputString" -Wait