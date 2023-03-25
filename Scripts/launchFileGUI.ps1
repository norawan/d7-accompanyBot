param([String]$DefaultPath = 'C:\Users\khand\OneDrive\Documents\GitHub\d7-accompanyBot\ExtraMusic')
Add-Type -AssemblyName System.Windows.Forms # need for subprocess execution
$FileBrowser = New-Object System.Windows.Forms.OpenFileDialog -Property @{ InitialDirectory = $DefaultPath }
$null = $FileBrowser.ShowDialog()
echo $FileBrowser.FileName