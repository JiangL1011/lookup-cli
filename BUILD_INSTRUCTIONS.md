# Build Instructions

This project supports multiple ways to build the executable using nuitka.

## Prerequisites

- Python 3.13+
- uv (package manager)

## Build Methods

### Method 1: Shell Script (Recommended for Unix-like systems)

```bash
./build.sh
```

### Method 2: Batch Script (For Windows)

```cmd
build.bat
```

### Method 3: Python Script (Cross-platform)

```bash
python build.py
# or
./build.py
```

### Method 4: Manual Build

```bash
# Install dependencies
uv sync --group dev

# Build executable
uv run nuitka \
  --mode=onefile \
  --output-dir=build \
  --output-filename=lu \
  --include-package=app \
  --include-package-data=langdetect \
  main.py

# For Windows, use lu.exe as output filename
```

## Output

All build methods will create:
- A `build/` directory containing the executable
- A single executable file (`lu` on Unix, `lu.exe` on Windows)
- Size: approximately 27-28MB (self-contained)

## GitHub Actions

The project includes automated builds for:
- Linux (ubuntu-latest)
- macOS (macos-latest) 
- Windows (windows-latest)

Builds are triggered on:
- Git tags matching `v*.*.*` pattern
- Manual workflow dispatch

## Testing

After building, test the executable:

```bash
# Unix/macOS
build/lu --help
build/lu -s

# Windows
build\lu.exe --help
build\lu.exe -s
```

## Distribution

The generated executable is completely self-contained and can be distributed without requiring Python or any dependencies on the target system.
