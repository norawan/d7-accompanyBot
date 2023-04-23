param([String]$rmFolder="None") 
if ($rmFolder -ne "None") {
    Remove-Item $rmFolder -Force -Recurse
}