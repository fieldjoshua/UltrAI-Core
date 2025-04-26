# UltraAI Framework

## IMPORTANT: Documentation First

**BEFORE CREATING ANY NEW FEATURES OR MAKING CHANGES, CONSULT THE DOCUMENTATION:**

All official documentation is in the `documentation/` directory:

- [RULES.md](documentation/RULES.md) - The controlling document for all project rules and standards
- [ACTIONS_INDEX.md](documentation/ACTIONS_INDEX.md) - Index of all active actions
- [CONFIG_DEFINITIONS.md](documentation/CONFIG_DEFINITIONS.md) - Program architecture and dependencies

## Core Principles

1. **Documentation First**: If it isn't written down first, we don't build it
2. **Single Action**: Only one Action may be in WORKING state at any time
3. **Plan-Based Development**: Every Action must have a PLAN.md in its directory
4. **Style Standards**: All code must follow established style guidelines

## About UltraAI

UltraAI is a powerful orchestration system for LLMs that leverages multiple models to enhance analysis quality and reliability through specialized analysis patterns ("feathers"). The framework enables different collaboration patterns between models, creating a system that can generate more insightful, nuanced, and reliable outputs than any single model operating independently.

## Project Structure

```
ultraai/
├── Actions/             # Implementation plans for all actions
│   ├── ACTION_NAME/     # Each action has its own directory
│   │   ├── PLAN.md      # The action's implementation plan
│   │   ├── Research/    # Research materials
│   │   ├── Prototypes/  # Proof-of-concept code
│   │   └── Design/      # Design resources
├── documentation/       # Project documentation
│   ├── RULES.md         # Controlling document for rules
│   ├── ACTIONS_INDEX.md # Index of all actions
│   ├── CONFIG_DEFINITIONS.md # Architecture definitions
│   └── Templates/       # Documentation templates
├── frontend/            # Frontend application
├── backend/             # Backend API and services
├── src/                 # Core application code
└── tests/               # Test suite
```

## Development Rules

1. **Code Changes**:
   - Only edit code when a matching PLAN.md exists and is in WORKING state
   - Update PLAN.md after completing checklist items or ending work sessions
   - Follow all style requirements (line length, formatting, etc.)

2. **Action Status**:
   - QUEUED → WORKING: Start coding after committing PLAN.md
   - WORKING → REVIEW: Implementation checklist finished
   - REVIEW → ACCEPTED: PR approved and merged
   - ACCEPTED → RELEASED: Feature deployed
   - WORKING → BLOCKED: External issue stops progress

3. **Commit Checklist**:
   - [ ] A PLAN.md exists and is in state WORKING
   - [ ] This commit relates to a step listed in the plan
   - [ ] PLAN.md updated (checkbox ticked or status changed)
   - [ ] Only this one Action is in state WORKING

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

1. Review [RULES.md](documentation/RULES.md) for project rules and standards
2. Check [ACTIONS_INDEX.md](documentation/ACTIONS_INDEX.md) for current priorities
3. Create or update plans following the established templates
4. Fork the repository and create a new branch for your feature or bug fix
5. Ensure your code adheres to the project's coding standards
6. Submit a pull request with a clear description of your changes

## Contact Information

For questions or support, please contact us at [support@ultraai.com](mailto:support@ultraai.com) or join our community forum at [forum.ultraai.com](http://forum.ultraai.com).

## License

[MIT License](LICENSE)
