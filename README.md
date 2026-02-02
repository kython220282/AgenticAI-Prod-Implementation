# Agentic AI Project Structure

**By: Karan Raj Sharma. Notes from Mr. Brij Kishor(https://www.linkedin.com/in/brijpandeyji/) were refered**

[![Use this template](https://img.shields.io/badge/Use%20this%20template-2ea44f?style=for-the-badge)](https://github.com/kython220282/AgenticAI-Prod-Implementation/generate)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive template for building intelligent autonomous systems with advanced reasoning capabilities.

---

## 🎯 Use This Template

**Create your own Agentic AI project in seconds:**

1. Click the **[Use this template](https://github.com/kython220282/AgenticAI-Prod-Implementation/generate)** button above
2. Name your new repository
3. Clone and start building immediately with all production infrastructure included!

**Or clone directly:**

## � Quick Start

**New to this project?** Check out our **[Getting Started Guide](docs/GETTING_STARTED.md)** for step-by-step instructions!

```bash
# Quick setup (5 minutes)
git clone https://github.com/kython220282/AgenticAI-Prod-Implementation.git
cd AgenticAI-Prod-Implementation
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python examples/basic_agent.py
```

## �📋 Project Overview

This project provides a complete framework for developing agentic AI systems with support for:
- **Multiple agent types** (Autonomous, Learning, Reasoning, Collaborative, LLM-powered)
- **Advanced core capabilities** (Memory, Planning, Decision Making, Execution)
- **LLM Integration** (GPT-4, Claude, with prompt management & token tracking)
- **Vector Databases** (Chroma, Pinecone, Weaviate, FAISS for semantic memory)
- **Flexible environment simulation** with OpenAI Gym compatibility
- **Production-ready** with comprehensive testing, logging, and monitoring

## ✨ Key Strengths

### 🎯 **1. Use-Case Agnostic Design**
- Modular architecture - use only what you need
- No opinionated frameworks - pure flexibility
- Adapts from simple chatbots to complex multi-agent systems

### 🤖 **2. Comprehensive Agent Types**
- **Traditional RL Agents**: For game AI, robotics, optimization
- **LLM-Powered Agents**: For natural language tasks, reasoning, creativity
- **Hybrid Agents**: Combine RL with LLM for best of both worlds

### 💾 **3. Advanced Memory Systems**
- **Vector Databases**: Semantic search across 4 providers
- **Traditional Memory**: Episodic, semantic, working memory
- **Automatic Embeddings**: Sentence transformers built-in

### 📊 **4. Production-Ready Features**
- Token usage tracking with cost analysis
- Comprehensive logging and metrics
- Docker support for deployment
- Testing framework included
- Type hints and documentation throughout

### 🔧 **5. Developer Experience**
- YAML-based configuration (no hardcoding)
- Jupyter notebooks for experimentation
- Rich examples for every feature
- Easy to extend and customize

## 🏗️ Project Structure

```
agentic_ai_project/
├── config/                      # Configuration files
│   ├── agent_config.yaml        # Agent parameters (autonomy, learning rates)
│   ├── model_config.yaml        # ML model architectures
│   ├── environment_config.yaml  # Simulation settings
│   ├── logging_config.yaml      # Logging configuration
│   ├── llm_config.yaml          # LLM & vector DB settings ⭐ NEW
│   └── prompts/                 # Prompt templates directory ⭐ NEW
│
├── src/                         # Source code
│   ├── agents/                  # Agent implementations
│   │   ├── base_agent.py        # Abstract base class
│   │   ├── autonomous_agent.py  # Self-directed agent
│   │   ├── learning_agent.py    # RL agent (Q-learning, DQN)
│   │   ├── reasoning_agent.py   # Logic-based agent
│   │   ├── collaborative_agent.py # Multi-agent coordination
│   │   └── llm_agent.py         # LLM-powered agent ⭐ NEW
│   │
│   ├── core/                    # Core capabilities
│   │   ├── memory.py            # Experience storage & recall
│   │   ├── reasoning.py         # Inference engine
│   │   ├── planner.py           # Multi-step planning (A*, BFS, DFS)
│   │   ├── decision_maker.py    # Decision frameworks
│   │   └── executor.py          # Action execution
│   │
│   ├── environment/             # Simulation environments
│   │   ├── base_environment.py  # RL environment interface
│   │   └── simulator.py         # Multi-agent simulator
│   │
│   └── utils/                   # Utilities
│       ├── logger.py            # Logging utilities
│       ├── metrics_tracker.py   # Performance metrics
│       ├── visualizer.py        # Plotting tools
│       ├── validator.py         # Data validation
│       ├── prompt_manager.py    # Prompt templates ⭐ NEW
│       ├── token_tracker.py     # Token usage & costs ⭐ NEW
│       └── vector_store.py      # Vector DB integration ⭐ NEW
│
├── data/                        # Data storage
│   ├── memory/                  # Agent memories
│   ├── knowledge_base/          # Facts and knowledge
│   ├── training/                # Training data
│   ├── logs/                    # Application logs
│   ├── checkpoints/             # Model checkpoints
│   └── vector_db/               # Vector database storage ⭐ NEW
│
├── tests/                       # Unit tests
│   ├── test_agents.py           # Agent tests
│   ├── test_reasoning.py        # Reasoning tests
│   ├── test_environment.py      # Environment tests
│   └── test_llm_integration.py  # LLM feature tests ⭐ NEW
│
├── examples/                    # Example scripts
│   ├── single_agent.py          # Basic agent usage
│   ├── multi_agent.py           # Multi-agent collaboration
│   ├── reinforcement_learning.py # RL training
│   ├── collaborative_agents.py  # Team coordination
│   └── llm_agent_example.py     # LLM agent demo ⭐ NEW
│
├── notebooks/                   # Jupyter notebooks
│   ├── agent_training.ipynb     # Training experiments
│   ├── performance_analysis.ipynb # Metrics analysis
│   └── experiment_results.ipynb # Results visualization
│
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── pyproject.toml              # Package metadata
└── README.md                   # This file
```

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd AgenticAI_Project_Structure
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up API keys (for LLM features)
# On Windows:
set OPENAI_API_KEY=your_openai_key_here
set ANTHROPIC_API_KEY=your_anthropic_key_here
set PINECONE_API_KEY=your_pinecone_key_here

# On Linux/Mac:
export OPENAI_API_KEY=your_openai_key_here
export ANTHROPIC_API_KEY=your_anthropic_key_here
export PINECONE_API_KEY=your_pinecone_key_here
```

### 3. Configure Settings

Edit configuration files in `config/` directory:
- `agent_config.yaml` - Agent behaviors and parameters
- `model_config.yaml` - ML model configurations
- `environment_config.yaml` - Simulation settings
- `logging_config.yaml` - Logging configuration
- `llm_config.yaml` - LLM and vector database settings (NEW)

### 4. Run Examples

```bash
# Single agent example
python examples/single_agent.py

# Multi-agent collaboration
python examples/multi_agent.py

# Reinforcement learning
python examples/reinforcement_learning.py

# Advanced collaboration
python examples/collaborative_agents.py

# LLM-powered agent (NEW)
python examples/llm_agent_example.py
```

## 🧩 Key Components

### Agents

- **BaseAgent**: Abstract base class defining agent interface
- **AutonomousAgent**: Self-directed decision-making
- **LearningAgent**: Reinforcement learning capabilities
- **ReasoningAgent**: Logical inference and planning
- **CollaborativeAgent**: Multi-agent coordination
- **LLMAgent**: LLM-powered natural language agent (NEW)

### Core Modules

- **Memory**: Experience storage and recall
- **Reasoning**: Logical inference engine
- **Planner**: Multi-step planning algorithms
- **DecisionMaker**: Decision-making frameworks
- **Executor**: Action execution and monitoring

### Environment

- **BaseEnvironment**: Standard RL environment interface
- **Simulator**: Multi-agent simulation environment

### Utilities

- **Logger**: Structured logging
- **MetricsTracker**: Performance tracking
- **Visualizer**: Plotting and v
- **PromptManager**: LLM prompt template management (NEW)
- **TokenTracker**: Token usage and cost tracking (NEW)
- **VectorStoreManager**: Vector database integration (NEW)isualization
- **Validator**: Data validation

## 📊 Usage Examples

### Basic Agent

```python
from agents import AutonomousAgent
from environment import Simulator

# Initialize environment
env = Simulator({'num_agents': 1, 'state_dim': 10, 'action_dim': 4})

# Create agent
agent = AutonomousAgent({'autonomy_level': 0.8})
agent.initialize()

# Training loop
obs

### LLM-Powered Agent (NEW)

```python
from agents import LLMAgent

# Configure with OpenAI
config = {
    'llm_provider': 'openai',
    'model': 'gpt-4-turbo-preview',
    'temperature': 0.7,
    'use_vector_memory': True,
    'system_prompt': 'reasoning'
}

# Create and initialize
agent = LLMAgent(config, name="AssistantAgent")
agent.initialize()

# Interact
response = agent.act("What should I do next?")
print(response)

# Check token usage
stats = agent.get_stats()
print(f"Tokens used: {stats['token_usage']['total_tokens']}")
print(f"Cost: ${stats['token_usage']['total_cost']:.6f}")
```

### Prompt Templates (NEW)

```python
from utils import PromptManager

pm = PromptManager()

# Render a planning template
prompt = pm.render_template(
    'task_planning',
    {
        'task': 'Build a chatbot',
        'constraints': ['Must be scalable', 'Low latency']
    }
)

# Few-shot learning
few_shot = pm.create_few_shot_prompt(
    instruction="Extract key metrics",
    examples=[
        {'input': '100 requests in 5 seconds', 
         'output': '20 req/sec'}
    ],
    input_text="500 users with 95% success"
)
```

### Vector Memory (NEW)

```python
from utils import VectorStoreManager

# Initialize vector store (supports Chroma, Pinecone, Weaviate, FAISS)
vector_store = VectorStoreManager(provider='chroma')

# Store information
6. **LLM Best Practices** (NEW):
   - Monitor token usage with TokenTracker
   - Use prompt templates for consistency
   - Enable vector memory for long-term context
   - Set appropriate temperature and max_tokens
   - Track costs per agent and task
vector_store.add_memory(
    "Agent uses modular architecture",
    metadata={'type': 'architecture'}
)

# Retrieve similar memories
results = vector_store.retrieve_similar(
    "How is the agent structured?",
    k=5
)

for result in results:
    print(f"Score: {result['score']:.4f} - {result['text']}")
```ervation = env.reset()
action = agent.act(observation)
next_obs, reward, done, info = env.step(action)
```

### With Memory and Planning

```python
from core import Memory, Planner

# Initialize memory
memory = Memory(capacity=10000, memory_type='episodic')

# Store experience
memory.store({'state': state, 'action': action, 'reward': reward})

# Recall similar experiences
similar = memory.recall(current_state, k=5)

# Create planner
planner = Planner(algorithm='a_star')
plan = planner.create_plan(initial_state, goal_state, actions)
```

## 🧪 Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_agents.py -v
```

With coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📈 Monitoring and Metrics

```python
from1. Autonomous Agent
**Best for**: Robotics, game AI, autonomous systems
- Self-directed decision-making
- Exploration vs exploitation balancing
- Goal-oriented behavior
- Configurable autonomy levels

### 2. Learning Agent  
**Best for**: Reinforcement learning tasks, optimization
- Experience replay buffer
- Q-learning/DQN algorithms
- Epsilon-greedy exploration
- Adaptive learning rates

### 3. Reasoning Agent
**Best for**: Logic puzzles, expert systems, planning
- Forward/backward chaining
- Knowledge base integration
- Multi-step reasoning
- Causal inference

### 4. Collaborative Agent
**Best for**: Multi-agent systems, team coordination
- Message passing protocols
- Team coordination strategies
- Conflict resolution
- Shared goal optimization

### 5. LLM Agent ⭐ NEW
**Best for**: Chatbots, assistants, creative tasks, RAG systems
- **LLM Integration**: GPT-4, Claude, custom models
- **Prompt Management**: Jinja2 templates with versioning
- **Vector Memory**: Semantic search for long-term context
- **Token Tracking**: Real-time cost monitoring
- **Multi-turn Conversations**: Maintains conversation state
- **Few-shot Learning**: Built-in example-based prompting

**Quick Start:**
```python
from agents import LLMAgent

agent = LLMAgent({
    'llm_provider': 'openai',
    'model': 'gpt-4-turbo-preview',
    'temperature': 0.7,
    'use_vector_memory': True
})
agent.initialize()
response = agent.act("Explain quantum computing")
```iven**: Use YAML configs for easy experimentation
3. **Comprehensive Testing**: Write tests for new features
4. **Document Changes**: Update docstrings and README
5. **Version Control**: Commit frequently with clear messages

## 📚 Best Practices

1. **YAML Configurations**: Define agent behaviors externally
2. **Error Handling**: Implement robust error recovery
3. **State Management**: Track agent states properly
4. **Document Behaviors**: Comment complex logic
5. **Test Thoroughly**: Cover edge cases
6. **Monitor Performance**: Track metrics during training
7. **Version Control**: Use git for code management

## 🐳 Docker Support

Build and run with Docker:

```bash
# 1. Memory Management
**Traditional Memory:**
- Working memory (short-term context)
- Episodic memory (experience replay)
- Semantic memory (facts/knowledge)
- Similarity-based retrieval

**Vector Memory (NEW):**
- Semantic search with embeddings
- 4 database options: Chroma, Pinecone, Weaviate, FAISS
- Automatic embedding generation (Sentence Transformers)
- Metadata filtering and hybrid search

### 2. Reasoning & Planning
- Logical inference (forward/backward chaining)
- Causal reasoning with knowledge graphs
- Path planning (A*, BFS, DFS algorithms)
- Goal decomposition and hierarchical planning
- **LLM-based reasoning**: Chain-of-thought, step-by-step analysis

### 3. Decision Making
- Utility-based decisions with preference modeling
- Rule-based systems with conflict resolution
- Multi-criteria analysis (weighted scoring)
- Risk assessment and uncertainty handling
- **LLM-assisted decisions**: Natural language reasoning

### 4. Task Execution
- Reliable action execution with retries
- Error handling and recovery
- Performance monitoring
- Result validation
- **Token-aware execution**: Cost tracking per task

### 5. Prompt Engineering (NEW)
- **Template Management**: Jinja2-based prompt library
- **Few-shot Learning**: Example-based prompting
- **System Prompts**: Role-specific instructions
- **Dynamic Rendering**: Context-aware prompt generation

### 6. Cost Optimization (NEW)
- **Real-time Tracking**: Monitor tokens per request
- **Cost Alerts**: Configurable thresholds
- **Analytics**: Usage by agent, task, and model
- **Reporting**: Daily/weekly/monthly summaries

### Collaborative Agent
- Message passing
- Team coordination
- Conflict resolution

## 🎯 Core Capabilities

### Memory Management
- Working memory (short-term)
- E🎓 Learning Path

### For Beginners
1. Start with `examples/single_agent.py` - Basic agent usage
2. Try `examples/reinforcement_learning.py` - RL concepts
3. Explore `notebooks/agent_training.ipynb` - Interactive learning

### For LLM Developers
1. Review `examples/llm_agent_example.py` - LLM integration
2. Study `src/utils/prompt_manager.py` - Prompt engineering
3. Experiment with `config/prompts/` - Custom templates

### For Production Systems
1. Configure `config/llm_config.yaml` - Production settings
2. Set up vector databases (Chroma for local, Pinecone for cloud)
3. Enable token tracking and monitoring
4. Use Docker for deployment

## 🔍 Common Use Cases

### 1. **Chatbot / Virtual Assistant**
```python
from agents import LLMAgent
agent = LLMAgent({'model': 'gpt-4', 'use_vector_memory': True})
```
**Uses**: LLMAgent + VectorStore + PromptManager

### 2. **RAG (Retrieval Augmented Generation)**
```python
from utils import VectorStoreManager
store = VectorStoreManager(provider='chroma')
# Add documents, then query with LLM
```
**Uses**: VectorStore + LLMAgent + TokenTracker

### 3. **Multi-Agent Research Team**
```python
from agents import CollaborativeAgent, LLMAgent
researcher = LLMAgent({...})
analyst = CollaborativeAgent({...})
```
**Uses**: Multiple agents + Message passing

### 4. **Game AI / Robotics**
```python
from agents import LearningAgent
from environment import Simulator
```
**Uses**: LearningAgent + Simulator + Memory

### 5. **Autonomous Planning System**
```python
from agents import ReasoningAgent
from core import Planner
```
**Uses**: ReasoningAgent + Planner + Executor

## 📊 Feature Comparison

| Feature | Traditional Agents | LLM Agents |
|---------|-------------------|------------|
| **Natural Language** | ❌ | ✅ |
| **Learning from Data** | ✅ | ✅ |
| **Reasoning** | Rule-based | Emergent + Rule-based |
| **Cost** | Compute only | Compute + API costs |
| **Interpretability** | High | Medium |
| **Flexibility** | Domain-specific | General purpose |
| **Setup Complexity** | Low | Medium (API keys) |
| **Best For** | RL tasks, games, robotics | NLP, assistants, creativity |

## 🚀 Quick Start Scenarios

### Scenario 1: Build a Research Assistant (5 minutes)
```bash
# 1. Set API key
export OPENAI_API_KEY='your-key'

# 2. Run example
python examples/llm_agent_example.py

# 3. Check token costs
cat data/logs/token_usage_AssistantAgent.json
```

### Scenario 2: Train a Game AI (10 minutes)
```bash
# 1. Configure agent
# Edit config/agent_config.yaml

# 2. Train
python examples/reinforcement_learning.py

# 3. Visualize
jupyter notebook notebooks/agent_training.ipynb
```

### Scenario 3: Build Multi-Agent System (15 minutes)
```bash
# 1. Configure team
# Edit config/agent_config.yaml (collaborative section)

# 2. Run simulation
python examples/collaborative_agents.py

# 3. Analyze results
python examples/multi_agent.py
```

## 💡 Pro Tips

1. **Start Simple**: Use one agent type first, add complexity as needed
2. **Monitor Costs**: Always enable TokenTracker for LLM agents
3. **Use Templates**: Don't hardcode prompts - use PromptManager
4. **Vector DB Choice**: 
   - Local/Testing → Chroma (free, local)
   - Production → Pinecone (managed, scalable)
   - Self-hosted → Weaviate (open source)
   - High-performance → FAISS (fastest)
5. **Hybrid Approach**: Combine LLM agents for reasoning + RL agents for optimization

## 🐛 Troubleshooting

### "ImportError: No module named langchain"
```bash
pip install langchain langchain-openai
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='sk-...'  # Linux/Mac
set OPENAI_API_KEY='sk-...'     # Windows
```

### "ChromaDB not found"
```bash
pip install chromadb
```

### High token costs
- Check `TokenTracker.get_summary()` for usage breakdown
- Reduce `max_tokens` in config
- Use cheaper models (gpt-3.5-turbo instead of gpt-4)
- Enable caching in `llm_config.yaml`

## � Documentation

### 📖 Complete Documentation Library

All documentation is available in the `docs/` folder and on GitHub:

#### **Getting Started**
- 🚀 **[Getting Started Guide](docs/GETTING_STARTED.md)** - Complete setup tutorial with examples  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/GETTING_STARTED.md)

- ⚙️ **[CI/CD Activation Guide](docs/CI_CD_ACTIVATION.md)** - Step-by-step CI/CD pipeline setup and configuration  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/CI_CD_ACTIVATION.md)

#### **Production Deployment Guides**
- 🐳 **[Phase 1: Production Essentials](docs/PHASE1_COMPLETE.md)** - FastAPI, Docker, authentication, monitoring  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/PHASE1_COMPLETE.md)

- 🔄 **[Phase 2: CI/CD & Infrastructure](docs/PHASE2_COMPLETE.md)** - GitHub Actions, database models, testing, backups  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/PHASE2_COMPLETE.md)

- ☸️ **[Phase 3: Enterprise & Kubernetes](docs/PHASE3_COMPLETE.md)** - Kubernetes, Helm, Istio, distributed tracing  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/PHASE3_COMPLETE.md)

- 🌍 **[Multi-Region Deployment](docs/MULTI_REGION_DEPLOYMENT.md)** - Global deployment, disaster recovery, failover  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/MULTI_REGION_DEPLOYMENT.md)

- 📦 **[Deployment Guide](docs/DEPLOYMENT.md)** - General deployment instructions  
  [View on GitHub](https://github.com/kython220282/AgenticAI-Prod-Implementation/blob/main/docs/DEPLOYMENT.md)

### 🎯 Learning Paths

**🟢 Beginner Path:**  
Start with [Getting Started Guide](docs/GETTING_STARTED.md) → Run examples → [Activate CI/CD](docs/CI_CD_ACTIVATION.md) → Customize configurations → Create your first agent

**🟡 Intermediate Path:**  
Integrate LLMs → Build multi-agent systems → [Activate CI/CD](docs/CI_CD_ACTIVATION.md) → Deploy with [Phase 1](docs/PHASE1_COMPLETE.md) → Set up infrastructure with [Phase 2](docs/PHASE2_COMPLETE.md)

**🔴 Advanced Path:**  
Kubernetes deployment with [Phase 3](docs/PHASE3_COMPLETE.md) → Multi-region setup → Enterprise observability → Auto-scaling

### 📊 Documentation Quick Links

| Document | Description | Topics Covered |
|----------|-------------|----------------|
| [Getting Started](docs/GETTING_STARTED.md) | Beginner-friendly tutorial | Setup, first agent, examples, troubleshooting |
| [CI/CD Activation](docs/CI_CD_ACTIVATION.md) | Pipeline setup guide | GitHub Actions, secrets, deployment automation |
| [Phase 1](docs/PHASE1_COMPLETE.md) | Production basics (31 files) | FastAPI, Docker, JWT auth, Celery, Prometheus |
| [Phase 2](docs/PHASE2_COMPLETE.md) | Infrastructure (40+ files) | CI/CD, SQLAlchemy, Alembic, Pytest, backups |
| [Phase 3](docs/PHASE3_COMPLETE.md) | Enterprise (20+ files) | Kubernetes, Helm, Istio, OpenTelemetry, secrets |
| [Multi-Region](docs/MULTI_REGION_DEPLOYMENT.md) | Global deployment | Database replication, load balancing, DR |
| [Deployment](docs/DEPLOYMENT.md) | General deployment | Docker, Kubernetes, production setup |

## �📝 License

MIT License - Use freely for commercial and non-commercial projects

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Write tests for new features
4. Commit changes (`git commit -m 'Add AmazingFeature'`)
5. Push to branch (`git push origin feature/AmazingFeature`)
6. Submit a pull request

## 📧 Contact

**Karan Raj Sharma**
- GitHub: https://github.com/kython220282
- Email: karan.rajsharma@yahoo.com
- LinkedIn: https://www.linkedin.com/in/karanrajsharma/

## 🙏 Acknowledgments

Built with:
- **LangChain** - LLM orchestration
- **OpenAI** - GPT models
- **Anthropic** - Claude models
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embeddings
- **NumPy/SciPy** - Scientific computing
- **pytest** - Testing framework

Special thanks to the open-source AI community!
---

**⭐ Star this repo if you find it useful!**

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Submit a pull request

## 🙏 Acknowledgments

Built with modern AI/ML best practices and frameworks.

---

**Happy Coding! 🚀**
