# UnDep

UnDep is a dependency management tool for tracking and syncing indirect dependencies across projects. It helps you keep specific files in sync with their source repositories without requiring direct package dependencies.

## Why UnDep?

UnDep solves the problem of managing indirect dependencies - (mostly modular) code you want to keep in sync with external sources without adding full package dependencies. The use-cases can look like:

- Syncing utility functions across projects while avoiding dependency troubles
- Reducing build times for super HPE usecases or OSS projects by providing an alternative to adding dependencies
- Tracking changes in reference implementations
- Maintaining consistent configuration files
## Features

- Track specific files from external GitHub repositories
- Automatically check for updates in source files
- View diffs between local and source files
- Selectively apply updates to local files
- Simple YAML configuration
- CLI interface for easy management

## Installation

```bash
pip install undep
```

## Usage

### Initialize UnDep in your project

```bash
undep init
```

This will create a `.undep.yml` configuration file in your project root.

### Configure your dependencies

Create or modify `.undep.yml`:

```yaml
version: "1.0"
    sources:
      - source:
          repo: "exitflynn/PyTubeAPI"
          branch: "main"
          path: "mainman.py"
        target: # local file path
          path: "lib/external/helper.py"
        update:
          frequency: "weekly"
          auto_merge: false
          notifications: ["email"]
```

### Check for updates

```bash
undep check
```

This command will:
- Check all tracked files for updates
- Show diffs when changes are detected
- List which files need updating

### Apply updates

```bash
undep update
```

Or automatically approve all updates:

```bash
undep update -y
```

## Configuration

The `.undep.yml` configuration file supports:

```yaml
# Example configuration
sources:
  - source:
      repo: "owner/repository"  # GitHub repository
      path: "src/utils.py"      # Path in source repository
    local_path: "vendor/utils.py"  # Where to store it locally
```

## Development

To contribute to UnDep:

1. Clone the repository
```bash
git clone https://github.com/exitflynn/undep.git
cd undep
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies
```bash
pip install -e ".[dev]"
```

4. Run tests
```bash
pytest
```

## License

This project is licensed under the GPL-3.0 license - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Known Limitations

- Currently only supports GitHub repositories
- No support for private repositories yet
- Single branch (main) support only

## 📚 Documentation

For more detailed documentation, please visit [docs/](docs/) directory.