# RNS Flet App Template

A template for creating [RNS](https://reticulum.network/) applications using [Flet](https://flet.dev/).

## Requirements

- Python 3.11+
- Poetry

## Installation

Clone this repository and install dependencies:

```bash
git clone <your-repo-url>
cd rns-flet-app-template
poetry install
```

## Usage

### Desktop

```bash
poetry run rns-flet-app
```

### Web

```bash
poetry run rns-flet-app-web
```

### Mobile

**Android**
```bash
poetry run rns-flet-app-android
```

**iOS**
```bash
poetry run rns-flet-app-ios
```

## Building

### Desktop Applications

```bash
poetry run flet build linux    # Linux
poetry run flet build windows  # Windows
poetry run flet build macos    # macOS
```

### Mobile Applications

```bash
poetry run flet build apk      # Android APK
poetry run flet build aab      # Android App Bundle
poetry run flet build ipa      # iOS app
```