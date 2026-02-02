# Getting Started with Agentic AI Framework

**A Complete Guide to Building Your First Intelligent Agent System**

This guide will walk you through setting up and using the Agentic AI framework, from installation to deployment. Whether you're building a simple chatbot or a complex multi-agent system, this guide has you covered.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Detailed Setup](#detailed-setup)
4. [Your First Agent](#your-first-agent)
5. [Common Use Cases](#common-use-cases)
6. [Development Workflow](#development-workflow)
7. [Testing](#testing)
8. [Deployment Options](#deployment-options)
9. [Troubleshooting](#troubleshooting)
10. [Next Steps](#next-steps)

---

## Prerequisites

### Required
- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Code Editor** (VS Code recommended)

### Optional (for advanced features)
- **Docker Desktop** ([Download](https://www.docker.com/products/docker-desktop/))
- **Kubernetes** (for production deployment)
- **API Keys** (OpenAI, Anthropic, Pinecone - get them later)

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 5GB free space

---

## Quick Start (5 minutes)

Get up and running in 5 minutes with a basic agent:

```bash
# 1. Clone the repository
git clone https://github.com/kython220282/AgenticAI-Prod-Implementation.git
cd AgenticAI-Prod-Implementation

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run example agent
python examples/basic_agent.py
```

**🎉 That's it!** You should see your first agent running.

---

## Detailed Setup

### Step 1: Clone and Navigate

```bash
git clone https://github.com/kython220282/AgenticAI-Prod-Implementation.git
cd AgenticAI-Prod-Implementation
```

### Step 2: Set Up Python Environment

**Option A: Using venv (Recommended for beginners)**
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using conda**
```bash
conda create -n agenticai python=3.10
conda activate agenticai
pip install -r requirements.txt
```

### Step 3: Install Additional Dependencies

**For LLM Integration:**
```bash
pip install openai anthropic langchain sentence-transformers
```

**For Vector Databases:**
```bash
# ChromaDB (recommended for local development)
pip install chromadb

# Pinecone (for cloud)
pip install pinecone-client

# Weaviate (for self-hosted)
pip install weaviate-client
```

**For Production API:**
```bash
pip install fastapi uvicorn[standard] sqlalchemy alembic asyncpg redis celery
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your favorite editor
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

**Minimal .env configuration:**
```env
# Application
APP_NAME=My Agentic AI
APP_ENV=development
LOG_LEVEL=INFO

# Only add these if you need LLM features
OPENAI_API_KEY=your-key-here  # Get from https://platform.openai.com/api-keys
ANTHROPIC_API_KEY=your-key-here  # Get from https://console.anthropic.com/
```

### Step 5: Verify Installation

```bash
# Run tests to verify everything works
pytest tests/ -v

# Should see all tests passing ✓
```

---

## Your First Agent

Let's create a simple agent from scratch!

### Example 1: Hello World Agent

Create `my_first_agent.py`:

```python
from src.agents.base_agent import BaseAgent
from src.core.memory import Memory
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HelloAgent(BaseAgent):
    """A simple agent that greets you"""
    
    def __init__(self, name: str):
        super().__init__(agent_id=f"hello-{name}", config={})
        self.name = name
        self.memory = Memory()
    
    def perceive(self, observation: dict) -> dict:
        """Receive input from environment"""
        logger.info(f"Agent {self.name} received: {observation}")
        return observation
    
    def decide(self, perception: dict) -> dict:
        """Make a decision based on perception"""
        user_input = perception.get('message', '')
        
        # Simple decision logic
        if 'hello' in user_input.lower():
            action = {'type': 'greet', 'message': f'Hello! I am {self.name}'}
        elif 'help' in user_input.lower():
            action = {'type': 'help', 'message': 'I can greet you and remember our conversation!'}
        else:
            action = {'type': 'chat', 'message': f'You said: {user_input}'}
        
        return action
    
    def act(self, action: dict) -> dict:
        """Execute the action"""
        logger.info(f"Agent {self.name} acting: {action['type']}")
        
        # Store in memory
        self.memory.add_experience({
            'timestamp': self.memory._get_timestamp(),
            'action': action
        })
        
        return action

# Run the agent
if __name__ == "__main__":
    agent = HelloAgent(name="Buddy")
    
    # Interact with the agent
    conversations = [
        {'message': 'Hello there!'},
        {'message': 'Can you help me?'},
        {'message': 'What is AI?'},
    ]
    
    for input_msg in conversations:
        perception = agent.perceive(input_msg)
        decision = agent.decide(perception)
        result = agent.act(decision)
        print(f"🤖 Agent: {result['message']}\n")
```

**Run it:**
```bash
python my_first_agent.py
```

**Output:**
```
🤖 Agent: Hello! I am Buddy
🤖 Agent: I can greet you and remember our conversation!
🤖 Agent: You said: What is AI?
```

### Example 2: LLM-Powered Agent

Create `llm_agent_example.py`:

```python
from src.agents.llm_agent import LLMAgent
from src.utils.prompt_manager import PromptManager
import yaml

# Load LLM configuration
with open('config/llm_config.yaml', 'r') as f:
    llm_config = yaml.safe_load(f)

# Create prompt manager
prompt_manager = PromptManager(templates_dir='config/prompts')

# Create LLM agent
agent = LLMAgent(
    agent_id='assistant-01',
    config=llm_config,
    system_prompt="You are a helpful AI assistant specialized in explaining AI concepts."
)

# Use the agent
questions = [
    "What is machine learning in simple terms?",
    "How do neural networks work?",
    "What's the difference between AI and AGI?"
]

for question in questions:
    print(f"\n📝 Question: {question}")
    response = agent.generate_response(question)
    print(f"🤖 Agent: {response}")
    print(f"💰 Tokens used: {agent.token_tracker.get_total_tokens()}")
```

**Run it:**
```bash
# Make sure you set OPENAI_API_KEY in .env first!
python llm_agent_example.py
```

### Example 3: Multi-Agent Collaboration

Create `multi_agent_example.py`:

```python
from src.agents.collaborative_agent import CollaborativeAgent
from src.environment.simulator import MultiAgentSimulator

# Create specialized agents
researcher = CollaborativeAgent(
    agent_id='researcher-01',
    role='researcher',
    capabilities=['search', 'analyze']
)

writer = CollaborativeAgent(
    agent_id='writer-01',
    role='writer',
    capabilities=['write', 'edit']
)

editor = CollaborativeAgent(
    agent_id='editor-01',
    role='editor',
    capabilities=['review', 'publish']
)

# Create simulator
simulator = MultiAgentSimulator(agents=[researcher, writer, editor])

# Define collaborative task
task = {
    'type': 'create_article',
    'topic': 'The Future of AI',
    'steps': [
        {'agent': 'researcher', 'action': 'research_topic'},
        {'agent': 'writer', 'action': 'write_draft'},
        {'agent': 'editor', 'action': 'review_and_publish'}
    ]
}

# Run simulation
result = simulator.run_episode(task, max_steps=10)
print(f"✅ Article created: {result}")
```

---

## Common Use Cases

### Use Case 1: Chatbot with Memory

```python
from src.agents.llm_agent import LLMAgent
from src.utils.vector_store import VectorStoreManager

# Create agent with vector memory
agent = LLMAgent(
    agent_id='chatbot-01',
    config={'provider': 'openai', 'model': 'gpt-4'}
)

# Initialize vector store for semantic memory
vector_store = VectorStoreManager(provider='chroma')
vector_store.initialize(collection_name='chat_history')

# Chat loop
print("💬 Chatbot ready! Type 'quit' to exit.\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break
    
    # Search relevant context from memory
    context = vector_store.search(user_input, top_k=3)
    
    # Generate response with context
    response = agent.generate_response(
        user_input,
        context=[c['text'] for c in context]
    )
    
    print(f"Bot: {response}\n")
    
    # Store in memory
    vector_store.add_documents([
        {'text': user_input, 'metadata': {'type': 'user'}},
        {'text': response, 'metadata': {'type': 'bot'}}
    ])
```

### Use Case 2: Code Assistant

```python
from src.agents.coding_agent import CodingAgent

agent = CodingAgent(
    agent_id='code-assistant',
    languages=['python', 'javascript']
)

# Code review
code = """
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
"""

review = agent.review_code(code, language='python')
print(f"📝 Code Review:\n{review}")

# Generate code
spec = "Create a function that finds prime numbers up to n"
generated_code = agent.generate_code(spec, language='python')
print(f"\n💻 Generated Code:\n{generated_code}")

# Explain code
explanation = agent.explain_code(generated_code)
print(f"\n📖 Explanation:\n{explanation}")
```

### Use Case 3: Research Agent

```python
from src.agents.research_agent import ResearchAgent
from src.utils.web_search import WebSearchTool

# Create research agent
agent = ResearchAgent(agent_id='researcher-01')

# Add tools
agent.add_tool(WebSearchTool(api_key='your-search-api-key'))

# Research a topic
report = agent.research(
    topic="Latest advances in transformer models",
    depth='comprehensive',
    sources=['arxiv', 'google_scholar', 'web']
)

print(f"📊 Research Report:\n{report}")
```

### Use Case 4: Data Analysis Agent

```python
from src.agents.planning_agent import PlanningAgent
import pandas as pd

# Create agent
agent = PlanningAgent(agent_id='data-analyst')

# Load data
df = pd.read_csv('data/sales_data.csv')

# Create analysis plan
task = {
    'goal': 'Analyze sales trends and provide insights',
    'data': df,
    'analyses': ['trend_analysis', 'forecasting', 'anomaly_detection']
}

# Agent creates and executes plan
plan = agent.create_plan(task)
results = agent.execute_plan(plan)

print(f"📈 Analysis Results:\n{results}")
```

---

## Development Workflow

### Project Structure Overview

```
your-project/
├── config/              # Configuration files (edit these)
├── src/
│   ├── agents/          # Your custom agents go here
│   ├── core/            # Core capabilities (don't modify)
│   └── utils/           # Utilities (extend as needed)
├── data/                # Your data files
├── examples/            # Example scripts (start here!)
├── notebooks/           # Jupyter notebooks for experiments
├── tests/               # Your tests
└── my_agents/           # Create this for your custom agents
```

### Recommended Development Flow

1. **Start with Examples**
   ```bash
   # Run existing examples to understand the framework
   python examples/basic_agent.py
   python examples/llm_integration.py
   python examples/multi_agent_simulation.py
   ```

2. **Experiment in Notebooks**
   ```bash
   # Launch Jupyter
   jupyter notebook
   
   # Open notebooks/agent_playground.ipynb
   # Experiment with agents interactively
   ```

3. **Create Custom Agents**
   ```bash
   # Create your own agents folder
   mkdir my_agents
   cd my_agents
   
   # Create your agent
   touch customer_service_agent.py
   ```

4. **Configure Your Agent**
   ```bash
   # Edit configuration
   nano config/agent_config.yaml
   
   # Add your agent settings
   # Test with: python my_agents/customer_service_agent.py
   ```

5. **Add Tests**
   ```bash
   # Create test file
   touch tests/test_my_agent.py
   
   # Run tests
   pytest tests/test_my_agent.py -v
   ```

### Using Configuration Files

**Edit `config/agent_config.yaml`:**
```yaml
agents:
  my_custom_agent:
    type: "llm_agent"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 500
    system_prompt: "You are a helpful customer service agent"
    capabilities:
      - answer_questions
      - create_tickets
      - escalate_issues
```

**Load in your code:**
```python
import yaml

with open('config/agent_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

my_agent_config = config['agents']['my_custom_agent']
```

---

## Testing

### Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Run Specific Tests

```bash
# Test agents only
pytest tests/test_agents.py -v

# Test LLM integration
pytest tests/test_llm_integration.py -v

# Test with markers
pytest tests/ -m "not slow" -v  # Skip slow tests
```

### Write Your Own Tests

Create `tests/test_my_agent.py`:

```python
import pytest
from my_agents.customer_service_agent import CustomerServiceAgent

@pytest.fixture
def agent():
    return CustomerServiceAgent(agent_id='test-agent')

def test_agent_creation(agent):
    assert agent.agent_id == 'test-agent'
    assert agent.is_initialized()

def test_handle_greeting(agent):
    response = agent.handle_message("Hello!")
    assert 'hello' in response.lower()

def test_create_ticket(agent):
    ticket = agent.create_ticket(
        subject="Bug report",
        description="App crashes on startup"
    )
    assert ticket['status'] == 'created'
    assert ticket['id'] is not None
```

---

## Deployment Options

### Option 1: Local Development (Current Setup)

**Best for:** Learning, experimentation, prototyping

```bash
# Already set up! Just run:
python your_agent.py
```

### Option 2: Docker Container

**Best for:** Team collaboration, consistent environments

```bash
# Build Docker image
docker build -t agenticai .

# Run container
docker run -p 8000:8000 --env-file .env agenticai

# Access at http://localhost:8000
```

### Option 3: Docker Compose (with databases)

**Best for:** Full-stack development with PostgreSQL, Redis

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

**Access points:**
- API: http://localhost:8000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Option 4: Production API

**Best for:** Production deployment, REST API

```bash
# Install production dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Or use production script
bash scripts/start-production.sh  # Linux/macOS
scripts\start-production.bat      # Windows
```

**API Endpoints:**
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Agents: http://localhost:8000/api/v1/agents

### Option 5: Kubernetes (Enterprise)

**Best for:** Large-scale production, auto-scaling

```bash
# Deploy to Kubernetes
cd k8s
./deploy.sh

# Or with Helm
helm install agenticai ./helm/agenticai \
  --namespace agenticai \
  --create-namespace

# Check deployment
kubectl get pods -n agenticai
```

**See full guide:** [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md)

---

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure you're in the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OpenAI API key not found"

**Solution:**
```bash
# Set in .env file
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Or set environment variable
# Windows:
set OPENAI_API_KEY=sk-your-key-here
# macOS/Linux:
export OPENAI_API_KEY=sk-your-key-here
```

### Issue: "ChromaDB database locked"

**Solution:**
```bash
# Delete the lock file
rm -rf data/vector_db/chroma.sqlite3  # macOS/Linux
del /f data\vector_db\chroma.sqlite3  # Windows

# Or use a different collection
# In your code, change: collection_name='my_new_collection'
```

### Issue: Tests failing

**Solution:**
```bash
# Update pytest
pip install --upgrade pytest

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +  # macOS/Linux
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"  # Windows

# Run tests with verbose output
pytest tests/ -v -s
```

### Issue: Docker build fails

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache

# Check Docker memory allocation (should be 4GB+)
docker info | grep Memory
```

### Issue: High memory usage

**Solution:**
```python
# Reduce model size in config/llm_config.yaml
llm:
  model: "gpt-3.5-turbo"  # Instead of gpt-4
  max_tokens: 500          # Instead of 2000

# Clear vector store periodically
vector_store.clear_collection('old_data')
```

### Getting Help

1. **Check documentation:**
   - [README.md](../README.md) - Project overview
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
   - [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Production features
   - [PHASE2_COMPLETE.md](PHASE2_COMPLETE.md) - CI/CD & Infrastructure
   - [PHASE3_COMPLETE.md](PHASE3_COMPLETE.md) - Kubernetes & Enterprise

2. **Search issues:** Check if your problem was already solved

3. **Ask the community:** Open a discussion on GitHub

4. **Report bugs:** Create an issue with:
   - Python version: `python --version`
   - OS: Windows/macOS/Linux
   - Error message (full traceback)
   - Steps to reproduce

---

## Next Steps

### Beginner Path 🟢

1. ✅ Run examples in `examples/` folder
2. ✅ Complete Jupyter notebooks in `notebooks/`
3. ✅ Modify configuration files to customize agents
4. ✅ Create your first custom agent
5. ✅ Add tests for your agent
6. ✅ Deploy with Docker

### Intermediate Path 🟡

1. ✅ Integrate with external APIs (OpenAI, Anthropic)
2. ✅ Build multi-agent systems
3. ✅ Implement custom tools and capabilities
4. ✅ Set up vector databases for semantic search
5. ✅ Create REST API with FastAPI
6. ✅ Deploy to production with Docker Compose

### Advanced Path 🔴

1. ✅ Implement custom reasoning engines
2. ✅ Build distributed agent networks
3. ✅ Set up CI/CD pipelines
4. ✅ Configure monitoring and observability
5. ✅ Deploy to Kubernetes with auto-scaling
6. ✅ Implement multi-region deployment

---

## Learning Resources

### Official Documentation
- 📚 [Project README](../README.md)
- 📖 [API Documentation](http://localhost:8000/docs) (when running)
- 🎓 [Example Scripts](../examples/)
- 📓 [Jupyter Notebooks](../notebooks/)

### External Resources
- **LangChain:** https://python.langchain.com/docs/get_started/introduction
- **OpenAI API:** https://platform.openai.com/docs/introduction
- **FastAPI:** https://fastapi.tiangolo.com/
- **Docker:** https://docs.docker.com/get-started/
- **Kubernetes:** https://kubernetes.io/docs/tutorials/

### Video Tutorials
- [Building AI Agents (YouTube)](https://youtube.com/watch?v=...)
- [LangChain Tutorial Series](https://youtube.com/watch?v=...)
- [FastAPI Crash Course](https://youtube.com/watch?v=...)

---

## Quick Reference

### Common Commands

```bash
# Activate environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Run agent
python my_agent.py

# Run tests
pytest tests/ -v

# Start API
uvicorn src.api.main:app --reload

# Docker
docker-compose up -d              # Start services
docker-compose logs -f api        # View logs
docker-compose down               # Stop services

# Kubernetes
kubectl get pods -n agenticai     # List pods
kubectl logs -f pod-name          # View logs
kubectl exec -it pod-name -- bash # Shell into pod
```

### File Locations

```
config/agent_config.yaml          # Agent settings
config/llm_config.yaml            # LLM settings
.env                               # Environment variables
data/logs/                         # Log files
data/vector_db/                    # Vector database
examples/                          # Example scripts
```

### API Endpoints

```
POST /api/v1/agents               # Create agent
GET  /api/v1/agents/{id}          # Get agent
POST /api/v1/agents/{id}/execute  # Execute agent
GET  /health                       # Health check
GET  /docs                         # API documentation
```

---

## Contributing

Want to improve this framework?

1. Fork the repository
2. Create a feature branch: `git checkout -b my-feature`
3. Make your changes
4. Add tests: `pytest tests/`
5. Commit: `git commit -m "Add amazing feature"`
6. Push: `git push origin my-feature`
7. Open a Pull Request

---

## Support

- 📧 Email: support@agenticai.example.com
- 💬 Discord: https://discord.gg/agenticai
- 🐛 Issues: https://github.com/kython220282/AgenticAI-Prod-Implementation/issues
- 📖 Docs: https://docs.agenticai.example.com

---

## License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

---

**Happy Building! 🚀**

Now go create something amazing with AI agents!
