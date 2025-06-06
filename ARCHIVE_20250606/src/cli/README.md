# CLI Tools

This directory contains command-line interfaces for the Ultra system.

## Tools

- `analyzer.py` - CLI for interacting with the orchestration system

## Usage

### Analyzer CLI

The analyzer CLI allows you to interact with LLMs through the orchestration system.

Basic usage:

```bash
python -m src.cli.analyzer --prompt "Explain quantum computing" --models openai:gpt-4,anthropic:claude-3-opus
```

Interactive mode:

```bash
python -m src.cli.analyzer --interactive --models mock:gpt-3.5-turbo
```

Options:

- `--prompt`, `-p`: Prompt to send to the LLM(s)
- `--models`, `-m`: Comma-separated list of models in provider:model format
- `--primary`, `-P`: Primary model to use in provider:model format
- `--temperature`, `-t`: Temperature for generation (0.0 to 1.0)
- `--max-tokens`, `-M`: Maximum tokens to generate
- `--parallel`, `-x`: Execute requests in parallel
- `--cache`, `-c`: Enable response caching
- `--output`, `-o`: Output file to write results to (JSON format)
- `--verbose`, `-v`: Enable verbose logging
- `--interactive`, `-i`: Run in interactive mode

### Interactive Commands

When running in interactive mode, the following commands are available:

- `help`: Show help message
- `exit`, `quit`: Exit the interactive mode
- `models`: Show available models
- `use <provider:model>`: Switch to a different model as primary
- Any other input will be sent as a prompt to the LLM(s)

## Examples

Using multiple models:

```bash
python -m src.cli.analyzer -p "Explain quantum computing" -m openai:gpt-4,anthropic:claude-3-opus,google:gemini-pro -P openai:gpt-4 -v
```

Using mock mode for testing:

```bash
python -m src.cli.analyzer -i -m mock:gpt-3.5-turbo,mock:claude-3-opus -c
```

Saving output to file:

```bash
python -m src.cli.analyzer -p "Explain quantum computing" -m openai:gpt-4 -o results.json
```
