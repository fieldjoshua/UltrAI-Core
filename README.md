# UltraAI Framework

## IMPORTANT: Documentation First

**BEFORE CREATING ANY NEW FEATURES OR MAKING CHANGES, CONSULT THE DOCUMENTATION:**

All official documentation is in the `documentation/` directory:

- [DOCUMENTATION_INDEX.md](documentation/DOCUMENTATION_INDEX.md) - Complete index of all documentation
- [CORE_README.md](documentation/CORE_README.md) - Critical information about this project

## About UltraAI

UltraAI is a powerful orchestration system for LLMs that leverages multiple models to enhance analysis quality and reliability through specialized analysis patterns ("feathers").

## Project Overview

UltraAI is designed to orchestrate multiple large language models (LLMs) to enhance data analysis and visualization. It leverages specialized analysis patterns, known as "feathers," to improve the quality and reliability of insights. The framework is suitable for various applications, including real-time data processing, interactive visualization, and machine learning integration.

## Installation Instructions

To set up UltraAI locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-repo/UltraAI.git
   cd UltraAI
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Set up environment variables:**
   Copy `.env.example` to `.env` and configure the necessary environment variables.

4. **Run the application:**

   ```bash
   docker-compose up
   ```

## Usage Guidelines

UltraAI can be used to orchestrate LLMs for various data analysis tasks. Here are some examples:

- **Running a basic analysis:**

  ```bash
  python src/main.py --config config/basic_analysis.yaml
  ```

- **Visualizing results:**
  Access the frontend at `http://localhost:3000` to view interactive visualizations.

## Contribution Guidelines

We welcome contributions from the community! Please follow these guidelines:

- Fork the repository and create a new branch for your feature or bug fix.
- Ensure your code adheres to the project's coding standards.
- Submit a pull request with a clear description of your changes.

## Contact Information

For questions or support, please contact us at [support@ultraai.com](mailto:support@ultraai.com) or join our community forum at [forum.ultraai.com](http://forum.ultraai.com).

# AICheck System - Contributor Guide

## Purpose

AICheck is a modular, RULES.md-compliant action management and automation system. This project enables contributors to define, track, and execute project actions in a transparent, auditable, and collaborative way.

## Quickstart

1. **Clone the repository:**

   ```sh
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. **Install dependencies:**

   ```sh
   # If using Python, Node, or other tools, add setup steps here
   # Example for Python:
   pip install -r requirements.txt
   ```

3. **Run the AICheck CLI:**

   ```sh
   cd AICheck
   ./ai new MyActionName  # Create a new action (PascalCase)
   ./ai switch MyActionName  # Switch to an action
   ./ai status MyActionName  # Check action status
   ```

## Adding New Actions

- Use PascalCase for action names (e.g., `MyNewAction`).
- Each action gets its own directory and plan file in `.aicheck/actions/`.
- Follow the action plan template for structure and compliance.
- Use the CLI to manage actions: create, switch, update, delete.

## Contributing

- All contributions must comply with `RULES.md`.
- Use pre-commit hooks and run tests before pushing changes.
- Document new actions and scripts clearly.
- Open issues or pull requests for major changes.

## Support

- See `RULES.md` for project governance and contribution rules.
- For help, open an issue or contact a maintainer.

---
Happy contributing!
