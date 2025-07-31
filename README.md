# AI Brand Content Generator

An AI-powered application that generates brand-consistent advertising content using Claude AI and Google Gemini. The application integrates brand guidelines and learns from reference materials to create multi-modal ad creatives across various platforms.

## 🚀 Features

### Core Functionality
- **Multi-AI Support**: Uses Claude AI as primary provider with Google Gemini as fallback
- **Brand Management**: Comprehensive brand guidelines storage and management
- **Content Generation**: Multi-modal content creation (text, image prompts, video scripts)
- **Platform Optimization**: Content optimized for specific social media platforms
- **Brand Consistency Analysis**: AI-powered analysis of content alignment with brand guidelines
- **Reference Material Integration**: Upload and analyze brand assets for context

### Content Types Supported
- Social Media Posts
- Banner Advertisements  
- Video Scripts
- Email Campaigns
- Blog Posts
- Product Descriptions

### Platform Optimization
- Instagram
- Facebook
- Twitter/X
- LinkedIn
- TikTok
- Custom platforms

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for Python
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Anthropic API**: Claude AI integration
- **Google Generative AI**: Gemini integration
- **Celery**: Background task processing

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Comprehensive component library
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing
- **Vite**: Fast build tool

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Anthropic API key (for Claude)
- Google API key (for Gemini)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ai-brand-content-generator
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/brand_content_db
REDIS_URL=redis://localhost:6379/0

# Application Settings
SECRET_KEY=your_secret_key_here
```

#### Database Setup
```bash
# Create database
createdb brand_content_db

# Run migrations (database tables will be created automatically)
python -m app.main
```

#### Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Start Development Server
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📖 API Documentation

### Authentication
All API endpoints (except registration and login) require authentication via JWT tokens.

```bash
# Register a new user
POST /api/v1/auth/register
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "string"
}

# Login
POST /api/v1/auth/login
{
  "username": "string",
  "password": "string"
}
```

### Brand Management
```bash
# Create a brand
POST /api/v1/brands/
{
  "name": "Brand Name",
  "description": "Brand description",
  "industry": "Technology",
  "brand_voice": "Professional, friendly, innovative",
  "color_palette": {
    "primary": "#007bff",
    "secondary": "#6c757d"
  },
  "target_audience": {
    "age_range": "25-45",
    "interests": ["technology", "innovation"]
  }
}

# List brands
GET /api/v1/brands/

# Get brand details
GET /api/v1/brands/{brand_id}

# Update brand
PUT /api/v1/brands/{brand_id}

# Delete brand
DELETE /api/v1/brands/{brand_id}
```

### Content Generation
```bash
# Generate content
POST /api/v1/content/generate
{
  "brand_id": 1,
  "content_type": "social_post",
  "brief": "Promote our new AI feature launch",
  "platform": "instagram",
  "preferred_ai_provider": "claude"
}

# List content
GET /api/v1/content/?brand_id=1

# Analyze brand consistency
POST /api/v1/content/analyze-consistency
{
  "content_piece_id": 1
}
```

### Campaign Management
```bash
# Create campaign
POST /api/v1/campaigns/
{
  "name": "Q4 Product Launch",
  "brand_id": 1,
  "objective": "Increase brand awareness",
  "platforms": ["instagram", "facebook"],
  "content_types": ["social_post", "banner_ad"]
}

# List campaigns
GET /api/v1/campaigns/?brand_id=1
```

## 🎯 Usage Examples

### 1. Setting Up a Brand
```python
# Create a comprehensive brand profile
brand_data = {
    "name": "TechCorp",
    "description": "Innovative technology solutions for modern businesses",
    "industry": "Technology",
    "brand_voice": "Professional yet approachable, innovative, trustworthy",
    "color_palette": {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "accent": "#28a745"
    },
    "typography": {
        "primary_font": "Helvetica Neue",
        "secondary_font": "Georgia"
    },
    "messaging_pillars": [
        "Innovation leadership",
        "Customer-centric solutions",
        "Reliable technology"
    ],
    "target_audience": {
        "primary": "Business decision makers, 30-50 years old",
        "secondary": "Tech enthusiasts, 25-40 years old"
    },
    "brand_values": [
        "Innovation",
        "Reliability",
        "Customer Success"
    ]
}
```

### 2. Generating Platform-Specific Content
```python
# Generate Instagram post
content_request = {
    "brand_id": 1,
    "content_type": "social_post",
    "brief": "Announce our new AI-powered analytics dashboard",
    "platform": "instagram",
    "target_audience": {
        "focus": "Tech professionals and data analysts"
    },
    "additional_context": {
        "campaign_theme": "Data-driven decisions",
        "key_features": ["Real-time analytics", "AI insights", "Custom dashboards"]
    }
}
```

### 3. Uploading Reference Materials
```python
# Upload brand assets for context
# The system will automatically analyze colors, styles, and content
POST /api/v1/uploads/reference-material
- brand_id: 1
- name: "Brand Style Guide"
- description: "Official brand style guidelines"
- file: [upload file]
```

## 🤖 AI Providers

### Claude AI (Primary)
- Advanced language understanding
- Excellent brand voice consistency
- Detailed content analysis
- Creative content generation

### Google Gemini (Fallback)
- Reliable alternative when Claude is unavailable
- Fast response times
- Good content quality
- Seamless fallback experience

The system automatically switches to Gemini if Claude is unavailable, ensuring uninterrupted service.

## 🔧 Configuration

### Environment Variables
```env
# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
MAX_FILE_SIZE_MB=50
ALLOWED_IMAGE_TYPES=jpg,jpeg,png,gif,webp
ALLOWED_DOCUMENT_TYPES=pdf,docx,txt

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Database Configuration
The application uses PostgreSQL with SQLAlchemy ORM. Tables are created automatically on first run.

### Redis Configuration
Redis is used for caching and session storage. Default configuration connects to localhost:6379.

## 🚀 Deployment

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# Frontend Dockerfile  
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

### Production Considerations
- Use environment variables for all secrets
- Set up SSL/TLS certificates
- Configure reverse proxy (nginx)
- Set up monitoring and logging
- Use production database settings
- Configure backup strategies

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Monitoring

### API Metrics
- Request/response times
- Error rates
- AI provider availability
- Content generation success rates

### Business Metrics
- Content pieces generated
- Brand consistency scores
- User engagement
- Platform performance

## 🔒 Security

### Authentication
- JWT-based authentication
- Password hashing with bcrypt
- Token expiration management

### Data Protection
- User data isolation
- Secure file uploads
- Input validation and sanitization
- SQL injection prevention

### API Security
- Rate limiting
- CORS configuration
- Request size limits
- File type validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Add tests for new features
- Update documentation
- Follow semantic versioning

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

#### "No AI providers available"
- Check your API keys in the .env file
- Ensure ANTHROPIC_API_KEY or GOOGLE_API_KEY is set
- Verify API key validity

#### Database connection errors
- Ensure PostgreSQL is running
- Check DATABASE_URL configuration
- Verify database permissions

#### File upload issues
- Check file size limits
- Verify allowed file types
- Ensure upload directory permissions

### Getting Help
- Check the [API documentation](http://localhost:8000/docs)
- Review the logs for error details
- Check environment configuration
- Ensure all dependencies are installed

## 🔮 Roadmap

### Upcoming Features
- [ ] Advanced image generation integration
- [ ] Multi-language content support
- [ ] A/B testing for generated content
- [ ] Performance analytics dashboard
- [ ] Scheduled content generation
- [ ] Team collaboration features
- [ ] Content calendar integration
- [ ] Advanced brand learning from user feedback

### Technical Improvements
- [ ] GraphQL API option
- [ ] Microservices architecture
- [ ] Enhanced caching strategies
- [ ] Real-time content generation
- [ ] Mobile app development
- [ ] Advanced AI model fine-tuning

---

Built with ❤️ using Claude AI and Google Gemini
