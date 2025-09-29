# Support Agent Automation System

A production-ready, LLM-powered customer support automation system that combines intelligent AI agents with a modern web interface. The system interprets natural language customer issues and autonomously resolves them through backend tool calls, with user satisfaction tracking and escalation capabilities.

## 🚀 Key Features

### Core AI Agent
- **LLM-powered agent** (OpenAI GPT-3.5 via LangChain)
- **Multi-step reasoning**: classify → retrieve policy → decide → act
- **Autonomous tool invocation**: refund, cancel, replacement, escalate, status
- **RAG (Retrieval-Augmented Generation)**: FAISS vector search for policy/FAQ context
- **Responsible AI patterns**: PII redaction, fraud control, structured logging

### Backend Infrastructure
- **FastAPI backend** with RESTful endpoints
- **SQLAlchemy + SQLite** database with transaction support
- **Modular tool architecture** for extensible functionality
- **Structured JSON logging** for all tool calls and outcomes
- **Comprehensive test suite** with pytest

### Web Interface
- **Flask-based Support Portal** with user authentication
- **Ticket management** with status tracking
- **User satisfaction** feedback collection
- **Responsive design** with Bootstrap 5

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask Portal  │    │  FastAPI Agent   │    │   SQLite DB     │
│   (Frontend)    │◄──►│   (Backend)      │◄──►│   (Data)        │
│                 │    │                  │    │                 │
│ • User Auth     │    │ • LLM Processing │    │ • Users         │
│ • Ticket Mgmt   │    │ • Tool Routing   │    │ • Orders        │
│ • Order Mgmt    │    │ • Policy RAG     │    │ • Tickets       │
│ • Dashboard     │    │ • Fraud Control  │    │ • Refunds       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

- **Python 3.11+**
- **LangChain** for LLM orchestration
- **OpenAI GPT-3.5** for language model
- **FastAPI** for backend API services
- **Flask** for web frontend
- **SQLAlchemy** for database ORM
- **FAISS** for vector similarity search
- **Bootstrap 5** for responsive UI
- **jQuery** for dynamic frontend interactions

## 📦 Project Structure

```
Support Agent/
├── agents/               # AI agent implementation
│   └── agent.py          # Main agent logic and workflow
│
├── api/                  # FastAPI backend
│   ├── main.py           # API endpoints and routes
│   └── frontend.py       # Streamlit demo (optional)
│
├── audit/                # Logging and monitoring
│   └── logger.py         # Structured logging setup
│
├── db/                   # Database models and schema
│   ├── __init__.py
│   └── schema.py         # SQLAlchemy models
│
├── frontend/             # Flask web application
│   ├── templates/        # HTML templates
│   ├── static/           # CSS/JS assets
│   └── app.py            # Flask application
│
├── policies/             # Policy documents
│   ├── faqs.md           # Frequently asked questions
│   └── refund_policy.md  # Refund policy details
│
├── rag/                  # Retrieval-Augmented Generation
│   └── policy_index.py   # FAISS vector store for policies
│
├── tests/                # Test suite
│   └── test_workflow.py  # Integration tests
│
├── tools/                # Action tools
│   ├── cancel_order.py   # Order cancellation
│   ├── escalate_case.py  # Case escalation
│   ├── find_orders.py    # Order lookup
│   ├── get_order_status.py
│   ├── issue_refund.py   # Refund processing
│   ├── langchain_tools.py # Tool registration
│   ├── order_utils.py    # Shared order utilities
│   └── tavily_search.py  # Web search capability
│
├── .env                  # Environment variables
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── init_db.py           # Database initialization
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- SQLite (included in Python)

### 1. Environment Setup

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Initialize the Database

```bash
python init_db.py
```

### 3. Start the Services

#### Backend API (FastAPI)
```bash
uvicorn api.main:app --reload
```

#### Frontend (Flask)
```bash
cd frontend
flask run
```

### 4. Access the Application
- **Web Interface**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Key Components

### AI Agent (`agents/agent.py`)
- Handles natural language understanding
- Manages conversation state
- Orchestrates tool usage
- Implements RAG for policy lookup

### API Endpoints (`api/main.py`)
- `POST /support/resolve` - Process support requests
- `GET /conversation/{conversation_id}` - Get conversation history
- `DELETE /conversation/{conversation_id}` - Clear conversation

### Tools (`tools/`)
- **Order Management**: Create, cancel, check status
- **Refund Processing**: Handle refunds with validation
- **Case Escalation**: Route to human agents
- **Web Search**: Look up information dynamically

### Database Models (`db/schema.py`)
- **User**: System users and authentication
- **Order**: Customer orders
- **Ticket**: Support tickets
- **RefundHistory**: Track refund transactions

## 🔒 Security Features

### Data Protection
- PII redaction in logs
- Secure password hashing
- Input validation and sanitization

### Fraud Prevention
- Rate limiting on refunds (max 2 per month)
- Order validation before processing
- Audit logging of all actions

## 🧪 Testing

Run the test suite:
```bash
pytest -v tests/
```

Test coverage includes:
- Order processing workflows
- Refund validations
- Policy enforcement
- Error handling
- Security controls

## 📈 Monitoring

### Logs
- Application logs in `logs/`
- Action audit trail in `action_log.jsonl`

### Metrics
- Response times
- Success/failure rates
- Tool usage statistics

## 🌐 Deployment

### Production Setup
1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables in `.env`
3. Use a production WSGI server (Gunicorn with Uvicorn)

### Docker (Optional)
```bash
docker-compose up --build
```

## 📚 Documentation

### API Documentation
Available at `/docs` when running the FastAPI server

### Code Documentation
- Docstrings follow Google style
- Type hints throughout the codebase

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Cloud Platforms
- **Render**: Easy deployment for both FastAPI and Flask
- **Heroku**: Support for Python web applications
- **AWS/GCP/Azure**: Container deployment with Docker

## 🤝 API Documentation

### FastAPI Auto-Generated Docs
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI Schema**: http://127.0.0.1:8000/openapi.json

### Integration Examples
```python
import requests

# Resolve support issue
response = requests.post(
    "http://127.0.0.1:8000/support/resolve",
    json={
        "user_input": "I need a refund for order #12345",
        "user_id": 1
    }
)
result = response.json()
print(f"Intent: {result['intent']}")
print(f"Action: {result['action_result']}")
```

## 🔄 Workflow Examples

### Refund Request
1. User: "I want a refund for my damaged item"
2. Agent: Classifies as "refund" intent
3. Agent: Retrieves refund policy
4. Agent: Calls `issue_refund()` tool
5. Result: Refund processed or limit exceeded
6. User: Chooses satisfaction or escalation

### Order Status
1. User: "What's the status of my order?"
2. Agent: Classifies as "status" intent
3. Agent: Calls `get_order_status()` tool
4. Result: Order details returned
5. User: Views result in ticket

## 📈 Future Enhancements

- **Multi-language support** for international customers
- **Voice integration** for phone support
- **Advanced analytics** and reporting dashboard
- **Machine learning** for intent classification improvement
- **Integration** with CRM and ERP systems
- **Real-time chat** with human agents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the API documentation
2. Review the test cases
3. Check the action logs
4. Open an issue on GitHub

---

**SupportOpsAgent**: Where AI meets human support, creating intelligent, scalable, and responsible customer service automation. 🤖✨
