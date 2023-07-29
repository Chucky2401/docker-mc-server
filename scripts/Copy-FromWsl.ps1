$rootPath = (Get-Item $PSScriptRoot).parent.FullName

Copy-Item -Path "\\wsl.localhost\Alpine\srv\docker\.vscode" -Recurse -Destination "$($rootPath)\wsl\srv\docker\" -Force -PassThru
Copy-Item -Path "\\wsl.localhost\Alpine\home\blackwizard\.vscode-server\data\Machine\*" -Recurse -Destination "$($rootPath)\wsl\home\~\.vscode-server\data\Machine\" -Force -PassThru
