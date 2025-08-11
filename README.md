# Rental Genie Agent

An intelligent AI agent for handling rental property inquiries and tenant applications. Built with FastAPI, LangChain, and OpenAI.

## Features

- 🤖 **Intelligent Chat Agent**: AI-powered responses to rental inquiries
- 🏠 **Property Management**: Integration with Airtable for property data
- 📱 **Multi-Platform Support**: Webhooks for Facebook, generic platforms, and direct API
- 💬 **Conversation Memory**: Maintains context across conversations
- 🔍 **Health Monitoring**: Built-in health checks and monitoring
- 📊 **Structured Responses**: JSON-formatted responses with confidence scoring

## Architecture

```
rentalGenie/
├── app/
│   ├── main.py          # FastAPI application with endpoints
│   ├── agent.py         # LangChain agent implementation
│   └── utils.py         # Utility functions for data loading
├── data/                # Property data files
├── model/               # Trained models
├── processed/           # Processed data
└── requirements.txt     # Python dependencies
```

## API Endpoints

### Chat Endpoints
- `POST /chat` - Main chat endpoint for direct message handling
- `POST /webhook/facebook` - Facebook Messenger webhook
- `POST /webhook/generic` - Generic webhook for any platform

### Utility Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /properties` - Get available properties

## Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Airtable API key (optional, for property data)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rentalGenie
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   BASE_ID=your_airtable_base_id
   AIRTABLE_API_KEY=your_airtable_api_key
   PROPERTY_TABLE_NAME=your_property_table_name
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

The server will start on `http://localhost:8000`

## Usage

### Direct Chat API
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a 2-bedroom apartment",
    "user_id": "user123",
    "session_id": "session456"
  }'
```

### Generic Webhook
```bash
curl -X POST "http://localhost:8000/webhook/generic" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What properties do you have available?",
    "user_id": "user123"
  }'
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

## Agent Capabilities

The Rental Genie agent can:

- **Answer Property Questions**: Provide information about available properties
- **Collect Tenant Information**: Gather move-in dates, duration, age, occupation, etc.
- **Handle Inquiries**: Respond to general rental questions
- **Maintain Context**: Remember conversation history
- **Validate Information**: Ensure all required tenant details are collected

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `BASE_ID`: Airtable base ID for property data
- `AIRTABLE_API_KEY`: Airtable API key
- `PROPERTY_TABLE_NAME`: Name of the properties table in Airtable

### Model Configuration
The agent uses GPT-4 by default. You can modify the model in `app/agent.py`:

```python
llm = ChatOpenAI(model="gpt-4o")  # Change model here
```

## Development

### Project Structure
- `app/main.py`: FastAPI application and endpoints
- `app/agent.py`: LangChain agent implementation
- `app/utils.py`: Data loading and utility functions
- `data/`: Property data files
- `model/`: Trained models and classifiers

### Adding New Features
1. Create new endpoints in `app/main.py`
2. Extend the agent logic in `app/agent.py`
3. Add utility functions in `app/utils.py`
4. Update this README with new features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.
