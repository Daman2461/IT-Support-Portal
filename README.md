# SupportOpsAgent

A production-grade, LLM-powered customer support automation system that combines intelligent AI agents with a modern web interface. The system interprets natural language customer issues and autonomously resolves them through backend tool calls, with user satisfaction tracking and escalation capabilities.

## 🚀 Features

### Core AI Agent
- **LLM-powered agent** (Mistral API via LangChain)
- **Multi-step reasoning**: classify → retrieve policy → decide → act
- **Autonomous tool invocation**: refund, cancel, replacement, escalate, status
- **RAG (Retrieval-Augmented Generation)**: FAISS vector search for policy/FAQ context
- **Responsible AI patterns**: PII redaction, fraud control, structured logging

### Backend Infrastructure
- **FastAPI backend** with `/support/resolve` endpoint
- **SQLAlchemy + SQLite** mock transactional database
- **Modular tool architecture** with simulated backend actions
- **Structured JSON logging** for all tool calls and outcomes
- **Comprehensive test suite** covering edge cases and fraud scenarios

### Frontend Integration
- **Flask-based IT Support Portal** with user authentication
- **LLM result storage** in ticket database
- **User satisfaction workflow**: AI response → user choice (satisfied/escalate)
- **Real-time ticket management** with status updates
- **Knowledge base** with articles and search functionality

### Production Features
- **API documentation** via FastAPI auto-generated Swagger UI
- **Cross-functional collaboration** ready with OpenAPI schema
- **Modular, extensible architecture** for easy scaling
- **Comprehensive error handling** and user feedback

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Flask Portal  │    │  FastAPI Agent   │    │   SQLite DB     │
│   (Frontend)    │◄──►│   (Backend)      │◄──►│   (Data)        │
│                 │    │                  │    │                 │
│ • User Auth     │    │ • LLM Processing │    │ • Users         │
│ • Ticket Mgmt   │    │ • Tool Routing   │    │ • Tickets       │
│ • Satisfaction  │    │ • Policy RAG     │    │ • LLM Results   │
│ • Knowledge Base│    │ • Fraud Control  │    │ • Refunds       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Python 3.11+**
- **LangChain** for LLM orchestration
- **Mistral API** for language model
- **FastAPI** for backend API
- **Flask** for web frontend
- **SQLAlchemy** for database ORM
- **FAISS** for vector search
- **Streamlit** (optional demo frontend)
- **Bootstrap** for UI styling

## 📦 Installation & Setup

### 1. Environment Setup
```bash
# Create and activate conda environment
conda create -y -n supportopsagent python=3.11
conda activate supportopsagent

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
SECRET_KEY=your_flask_secret_key
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_email_password
```

### 3. Database Setup
```bash
# Seed the database with mock data
PYTHONPATH=. python db/seed_data.py
```

## 🚀 Running the System

### Option 1: Full Integration (Recommended)
```bash
# Terminal 1: Start FastAPI backend
uvicorn api.main:app --reload

# Terminal 2: Start Flask frontend
cd it-support-portal
flask run
```

### Option 2: Streamlit Demo
```bash
# Start Streamlit frontend
streamlit run api/frontend.py
```

## 📋 Usage

### 1. Access the System
- **Flask Portal**: http://127.0.0.1:5000
- **FastAPI Docs**: http://127.0.0.1:8000/docs
- **Streamlit Demo**: http://localhost:8501

### 2. Create a Support Ticket
1. Register/login to the Flask portal
2. Navigate to "New Ticket"
3. Enter your support issue
4. The LLM agent will process your request
5. Choose if you're satisfied or want human assistance

### 3. API Integration
```bash
curl -X POST "http://127.0.0.1:8000/support/resolve" \
     -H "Content-Type: application/json" \
     -d '{"user_input": "I want a refund for my damaged item", "user_id": 1}'
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
PYTHONPATH=. pytest --maxfail=3 --disable-warnings -v
```

Tests cover:
- ✅ Successful refund workflow
- ✅ Refund limit enforcement
- ✅ Escalation scenarios
- ✅ Unknown intent handling
- ✅ PII redaction
- ✅ Fraud detection

## 🔧 Configuration

### LLM Models
- **Default**: Mistral Medium (`mistral-medium`)
- **Alternative**: Mistral Small (`mistral-small`) or Large (`mistral-large`)
- **Configuration**: Edit `agents/agent.py`

### Database
- **Default**: SQLite (`support_portal.db`)
- **Production**: PostgreSQL/MySQL via SQLAlchemy URI
- **Configuration**: Edit Flask app config

### Tools & Policies
- **Tools**: Located in `tools/` directory
- **Policies**: Markdown files in `policies/` directory
- **Customization**: Add new tools or policies as needed

## 📊 Monitoring & Logging

### Action Logs
- **Location**: `action_log.jsonl`
- **Format**: JSON lines with timestamp, action, params, result
- **Usage**: Audit trail for all agent actions

### Error Handling
- **FastAPI**: Automatic error responses with details
- **Flask**: User-friendly error messages
- **Logging**: Structured logging for debugging

## 🔒 Security & Compliance

### PII Protection
- **Redaction**: Names and emails automatically redacted
- **Processing**: LLM never sees sensitive data
- **Storage**: Secure handling of user information

### Fraud Prevention
- **Limits**: Max 2 refunds per user/month
- **Validation**: Input sanitization and validation
- **Audit**: Complete action logging for compliance

## 🚀 Deployment

### Development
```bash
# Local development with auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
flask run --host 0.0.0.0 --port 5000
```

### Production
- **FastAPI**: Deploy with Gunicorn/Uvicorn
- **Flask**: Deploy with Gunicorn
- **Database**: Use production database (PostgreSQL/MySQL)
- **Environment**: Set production environment variables

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
