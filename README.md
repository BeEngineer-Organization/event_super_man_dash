# データのダウンロード

もし閲覧できるけどcloneができない場合、PCに入っているGitアカウントが適切でない可能性があるので、その場合はZIPのダウンロードで対応してください。

# 環境構築

### Mac

``` console
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv)$ pip install --upgrade pip
(.venv)$ pip install -r requirements.txt
```

### Windows

``` ps1con
PS> Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
PS> python -m venv .venv
PS> .venv\Scripts\Activate.ps1
(.venv)PS> pip install --upgrade pip
(.venv)PS> pip install -r requirements.txt
```

# 実行

``` console
(.venv)$ python auto_typing.py
```