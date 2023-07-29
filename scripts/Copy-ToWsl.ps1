$rootPath = (Get-Item $PSScriptRoot).parent.FullName

Copy-Item -Path "$($rootPath)\*" -Exclude "LICENSE", "README.md", "scripts", ".git", "wsl" -Recurse -Destination "\\wsl.localhost\Alpine\srv\docker\build\minecraft\" -Force -PassThru
