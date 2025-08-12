# Rental Genie Dashboard

A comprehensive Streamlit dashboard for property owners to manage properties, monitor tenant interactions, and oversee AI agent performance in the Rental Genie system.

## 🚀 Features

### Core Functionality
- **📊 Dashboard Overview**: Real-time metrics and key performance indicators
- **🏢 Property Management**: View and edit property details, room configurations, and amenities
- **👥 Tenant Management**: Monitor tenant inquiries, profiles, and conversation history
- **📈 Reports & Analytics**: Interactive charts and data visualization
- **⚙️ Settings**: Configure notifications, agent settings, and system preferences

### Key Capabilities
- **Real-time Data**: Live updates from the Rental Genie API
- **Interactive Charts**: Plotly-powered visualizations for occupancy, status distribution, and trends
- **Smart Filtering**: Search and filter tenants by status, priority, and other criteria
- **Export Functionality**: Download data in CSV and JSON formats
- **Responsive Design**: Works on desktop and mobile devices
- **Mock Data Support**: Test with sample data when API is unavailable

## 📋 Requirements

### System Requirements
- Python 3.8+
- Streamlit 1.28.0+
- Internet connection for API access

### Dependencies
```
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
plotly>=5.15.0
python-dotenv>=1.0.0
pydantic>=2.5.0
```

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd rentalGenie/dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the dashboard directory:
```bash
# API Configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30

# Dashboard Configuration
DEBUG_MODE=False
ENABLE_MOCK_DATA=False

# Optional: Enable mock data for testing
ENABLE_MOCK_DATA=True
```

### 4. Run the Dashboard
```bash
streamlit run main.py
```

The dashboard will be available at `http://localhost:8501`

## 🏗️ Architecture

### File Structure
```
dashboard/
├── main.py              # Main Streamlit application
├── config.py            # Configuration settings and constants
├── utils.py             # Utility functions and helpers
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Components

#### Main Application (`main.py`)
- **DashboardAPI Class**: Handles communication with the Rental Genie backend
- **Page Functions**: Separate functions for each dashboard page
- **Navigation**: Sidebar navigation with session state management
- **Styling**: Custom CSS for consistent design

#### Configuration (`config.py`)
- **API Settings**: Base URL, timeouts, and connection parameters
- **Theme Colors**: Consistent color scheme throughout the dashboard
- **Validation Rules**: Data validation for forms and inputs
- **Default Settings**: Pre-configured values for various features

#### Utilities (`utils.py`)
- **Data Formatting**: Currency, date, and text formatting functions
- **Chart Creation**: Plotly chart generation functions
- **Validation**: Data validation and error checking
- **Export Functions**: CSV and JSON export capabilities
- **Mock Data**: Sample data for testing and development

## 📊 Dashboard Pages

### 1. Dashboard Overview
- **Key Metrics**: Total properties, occupancy rate, new leads, active conversations
- **Recent Activity**: Latest tenant inquiries with priority indicators
- **Quick Actions**: Direct links to other dashboard sections

### 2. Properties Management
- **Property Selection**: Dropdown to choose between properties
- **Property Details**: Editable forms for property information
- **Room Management**: Tabbed interface for individual room configuration
- **Statistics**: Property-specific metrics and occupancy data

### 3. Tenants Management
- **Filtering**: Filter by status, priority, and search terms
- **Tenant Cards**: Expandable cards with detailed tenant information
- **Actions**: Approve, reject, contact, and schedule viewing buttons
- **Conversation History**: View recent conversation messages

### 4. Reports & Analytics
- **Date Range Selection**: Customizable time periods for analysis
- **Key Metrics**: Total inquiries, qualified leads, viewings, applications
- **Interactive Charts**: 
  - Tenant status distribution (pie chart)
  - Inquiry priority distribution (bar chart)
  - Property occupancy (stacked bar chart)
  - Recent activity timeline (scatter plot)

### 5. Settings
- **API Configuration**: Test and configure API connection
- **Notification Settings**: Email, Slack, and push notification preferences
- **Agent Configuration**: Handoff thresholds and auto-approve scores
- **Data Export**: Download tenant and property data
- **System Information**: Version and connection status

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Rental Genie API base URL | `http://localhost:8000` |
| `API_TIMEOUT` | API request timeout (seconds) | `30` |
| `DEBUG_MODE` | Enable debug mode | `False` |
| `ENABLE_MOCK_DATA` | Use mock data instead of API | `False` |

### Customization
The dashboard can be customized by modifying `config.py`:

- **Colors**: Update `THEME_COLORS` for custom branding
- **Validation**: Modify `VALIDATION_RULES` for data validation
- **Amenities**: Add/remove items in `DEFAULT_AMENITIES`
- **Status Options**: Update `TENANT_STATUSES` and `PRIORITY_LEVELS`

## 🧪 Testing

### Mock Data Mode
Enable mock data for testing without API connection:
```bash
ENABLE_MOCK_DATA=True
```

### API Testing
Test API connection from the Settings page or use the health check endpoint:
```bash
curl http://localhost:8000/health
```

## 📱 Usage

### Navigation
- Use the sidebar to navigate between pages
- Quick stats are displayed in the sidebar
- Session state maintains current page and selections

### Data Management
- **Viewing**: All data is read-only by default
- **Editing**: Use forms to update property and room information
- **Actions**: Use buttons to approve/reject tenants or schedule viewings
- **Export**: Download data using the export buttons in Settings

### Responsive Design
- Dashboard adapts to different screen sizes
- Mobile-friendly interface for on-the-go management
- Touch-friendly buttons and controls

## 🔒 Security

### API Security
- API calls use HTTPS (when configured)
- Timeout protection prevents hanging requests
- Error handling for failed connections

### Data Protection
- No sensitive data stored locally
- Session state cleared on logout
- Input validation prevents malicious data

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py --server.port 8501
```

### Production Deployment
1. **Docker** (recommended):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Cloud Platforms**:
   - **Streamlit Cloud**: Direct deployment from GitHub
   - **Heroku**: Use the provided `Procfile`
   - **AWS/GCP**: Deploy as containerized application

### Environment Setup
```bash
# Production environment variables
API_BASE_URL=https://your-api-domain.com
DEBUG_MODE=False
ENABLE_MOCK_DATA=False
```

## 🔄 API Integration

### Required Endpoints
The dashboard expects the following API endpoints:

- `GET /properties` - List all properties
- `GET /tenants` - List all tenant profiles
- `GET /conversation` - List all conversations
- `PUT /properties/{id}` - Update property details
- `POST /tenants/{id}/approve` - Approve tenant
- `POST /tenants/{id}/reject` - Reject tenant
- `GET /health` - Health check

### Data Format
The API should return JSON data in the expected format. See the `DashboardAPI` class in `main.py` for detailed endpoint specifications.

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check `API_BASE_URL` in environment variables
   - Verify the Rental Genie API is running
   - Test connection from Settings page

2. **No Data Displayed**
   - Enable mock data for testing: `ENABLE_MOCK_DATA=True`
   - Check API response format matches expected structure
   - Verify API endpoints are accessible

3. **Charts Not Loading**
   - Ensure Plotly is installed: `pip install plotly`
   - Check browser console for JavaScript errors
   - Verify data format for chart creation

4. **Performance Issues**
   - Enable caching: `ENABLE_CACHING=True`
   - Reduce data volume or implement pagination
   - Check API response times

### Debug Mode
Enable debug mode for detailed error messages:
```bash
DEBUG_MODE=True
```

## 📈 Future Enhancements

### Planned Features
- **Authentication**: User login and role-based access
- **Real-time Updates**: WebSocket integration for live data
- **Advanced Analytics**: Machine learning insights and predictions
- **Calendar Integration**: Google Calendar for viewing scheduling
- **Multi-language Support**: French and English localization
- **Mobile App**: Native mobile application

### Customization Options
- **Custom Themes**: Brand-specific color schemes
- **Dashboard Widgets**: Configurable dashboard layout
- **Custom Reports**: User-defined report templates
- **API Extensions**: Additional API endpoint support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review API documentation
- Open an issue on GitHub
- Contact the development team

---

**Rental Genie Dashboard** - Empowering property owners with intelligent insights and efficient management tools.
