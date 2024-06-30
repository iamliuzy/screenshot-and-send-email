# screenshot-and-send-email

Take a screenshot and send it to the designated email address.

## Build

### Clone the project:
```bash
git clone https://github.com/iamliuzy/screenshot-and-send-email.git
```
or use github cli:
```bash
gh repo clone iamliuzy/screenshot-and-send-email
```

### Install requirements and nuitka

```bash
pip install -r requirements.txt
pip install nuitka
```

### Build

```bash
nuitka main.py --standalone --include-data-file=./config.toml=config.toml --disable-console
```

### Run

```bash
./build.dist/main.exe
```
This program has no ommand line output. Logs will be saved in `latest.log`
