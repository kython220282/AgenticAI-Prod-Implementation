# Data Directory

This directory contains all data generated and used by the Agentic AI system.

## Subdirectories

### memory/
Stores agent memory files, including episodic and semantic memory data.

### knowledge_base/
Contains knowledge base files, facts, rules, and learned knowledge.

### training/
Training data, datasets, and preprocessed data for agent learning.

### logs/
Application logs, error logs, and performance logs.

### checkpoints/
Model checkpoints, agent state snapshots, and training checkpoints.

## Usage

- Logs are automatically created during system operation
- Checkpoints are saved periodically during training
- Memory and knowledge base files are created as agents learn
- Training data should be placed here for agent learning experiments

## Note

This directory may contain large files. Consider adding to `.gitignore` for version control.
