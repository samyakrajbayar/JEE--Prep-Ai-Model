# 🎓 JEE Preparation AI Model

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![Discord](https://img.shields.io/badge/Discord-Bot-7289da.svg)](https://discord.py)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent AI-powered system for JEE (Joint Entrance Examination) preparation featuring adaptive learning, personalized question recommendations, and comprehensive progress tracking.

## 🌟 Features

### 📚 **Comprehensive Question Database**
- **10,000+ Previous Year Questions** from JEE Main & Advanced (2015-2024)
- **AI-Generated Questions** that match JEE patterns and difficulty levels
- **Complete Syllabus Coverage** for Physics, Chemistry, and Mathematics
- **Multi-format Support**: MCQs, Numerical Questions, Assertion-Reason

### 🧠 **Adaptive Learning System**
- **Personalized Recommendations** based on performance analysis
- **Weak Topic Identification** with targeted practice suggestions
- **Difficulty Progression** that adapts to your learning curve
- **Performance Analytics** with detailed insights and trends

### 🤖 **Discord Bot Integration**
- **Interactive Practice Sessions** with real-time feedback
- **Group Study Features** for collaborative learning
- **Progress Sharing** and leaderboards
- **24/7 Availability** for continuous practice

### 📊 **Advanced Analytics**
- **Topic-wise Performance Tracking**
- **Time Management Analysis**
- **Accuracy Trends and Predictions**
- **Comparative Performance Metrics**

## 🚀 Quick Start

### 1. **Clone Repository**
```bash
git clone https://github.com/yourusername/jee-ai-model.git
cd jee-ai-model
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Set Environment Variables**
```bash
# Create .env file or set in Replit Secrets
OPENAI_API_KEY=your_openai_api_key_here
DISCORD_TOKEN=your_discord_bot_token_here
```

### 4. **Run the Application**
```bash
python main.py
```

## 🛠 Setup Instructions

### **For Replit (Recommended)**

1. **Import to Replit**
   - Go to [Replit.com](https://replit.com)
   - Click "Import from GitHub"
   - Paste repository URL

2. **Configure Secrets**
   - Go to Secrets tab in Replit
   - Add `OPENAI_API_KEY` (optional)
   - Add `DISCORD_TOKEN` (for Discord bot)

3. **Run**
   - Click the "Run" button
   - Bot starts automatically!

### **Discord Bot Setup**

1. **Create Discord Application**
   - Visit [Discord Developer Portal](https://discord.com/developers/applications)
   - Create new application
   - Go to "Bot" section and create bot
   - Copy token to environment variables

2. **Invite Bot to Server**
   - Generate OAuth2 URL with bot permissions:
     - Send Messages
     - Embed Links
     - Read Message History
     - Use External Emojis

## 🎮 Usage

### **Discord Bot Commands**

```
🎯 Practice Commands
!start [subject]           # Begin practice session
!answer A                  # Submit answer (A/B/C/D for MCQ)
!answer 42                 # Submit numerical answer
!hint                      # Get a hint for current question
!solution                  # View detailed solution
!skip                      # Skip current question

📊 Analytics Commands  
!analytics                 # View personal progress
!weak                      # Show weak topics
!strong                    # Show strong topics
!compare @user             # Compare performance with friend

📚 Study Commands
!syllabus [subject]        # View complete syllabus
!topic Mechanics           # Practice specific topic
!difficulty Easy           # Set difficulty level
!mock 30                   # Start 30-question mock test

🎲 Generate Commands
!generate Physics Hard     # Generate AI question
!pyq 2023                  # Get PYQ from specific year
!random                    # Get random question
```

### **Console Mode**
If Discord token is not provided, the system runs in interactive console mode:

```
> question Physics         # Get physics question
> analytics user123        # View user analytics
> syllabus Chemistry       # View chemistry syllabus  
> generate Math Medium     # Generate new question
> quit                     # Exit application
```

## 📋 Subjects & Syllabus

### **Physics**
- **Mechanics**: Kinematics, Laws of Motion, Work Energy Power, Rotational Motion, Gravitation
- **Thermodynamics**: Thermal Properties, Kinetic Theory, Laws of Thermodynamics
- **Electrodynamics**: Electrostatics, Current Electricity, Magnetic Effects, EM Induction
- **Optics**: Ray Optics, Wave Optics, Modern Optics
- **Modern Physics**: Dual Nature, Atomic Structure, Nuclear Physics

### **Chemistry**  
- **Physical Chemistry**: Atomic Structure, Bonding, Thermodynamics, Equilibrium, Kinetics
- **Inorganic Chemistry**: Periodic Table, s/p/d/f Block Elements, Coordination Compounds
- **Organic Chemistry**: Basic Concepts, Hydrocarbons, Functional Groups, Biomolecules

### **Mathematics**
- **Algebra**: Complex Numbers, Sequences, Matrices, Probability
- **Calculus**: Limits, Derivatives, Integration, Differential Equations
- **Coordinate Geometry**: Lines, Circles, Conic Sections
- **Trigonometry**: Functions, Identities, Inverse Functions
- **Vector & 3D Geometry**: Vector Algebra, 3D Geometry

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────┐
│                 JEE AI Model                        │
├─────────────────────────────────────────────────────┤
│  🤖 Discord Bot Interface                           │
│  📊 Adaptive Learning Engine                        │
│  🧠 Question Generation AI                          │
│  📚 Question Database (SQLite)                      │
│  📈 Analytics & Progress Tracking                   │
│  🎯 Personalization Algorithm                       │
└─────────────────────────────────────────────────────┘

External APIs:
├── OpenAI GPT-3.5 (Question Generation)
├── Discord API (Bot Interface)  
└── Future: YouTube, Wolfram Alpha, Wikipedia
```

## 📊 Database Schema

### **Questions Table**
```sql
questions (
    id TEXT PRIMARY KEY,
    subject TEXT,           -- Physics/Chemistry/Mathematics  
    chapter TEXT,           -- Mechanics/Organic Chemistry/Calculus
    topic TEXT,             -- Kinematics/Alkanes/Integration
    difficulty TEXT,        -- Easy/Medium/Hard
    question_text TEXT,     -- The question content
    options TEXT,           -- JSON array of options
    correct_answer TEXT,    -- Correct option or numerical value
    solution TEXT,          -- Detailed solution
    year INTEGER,           -- Year of examination
    exam_type TEXT,         -- JEE Main/Advanced/Generated
    question_type TEXT      -- MCQ/Numerical/Assertion-Reason
)
```

### **Progress Tracking**
```sql
student_progress (
    user_id TEXT PRIMARY KEY,
    subject_scores TEXT,           -- JSON of subject-wise scores
    weak_topics TEXT,              -- JSON array of weak topics
    strong_topics TEXT,            -- JSON array of strong topics
    total_questions_attempted INTEGER,
    correct_answers INTEGER,
    last_session TIMESTAMP
)
```

## 🔧 API Integration

### **OpenAI Integration**
```python
# Generate JEE-style questions using GPT-3.5
question = question_generator.generate_question(
    subject="Physics",
    chapter="Mechanics", 
    topic="Kinematics",
    difficulty="Medium"
)
```

### **Adaptive Learning Algorithm**
```python
# Personalized question selection
questions = adaptive_learning.get_personalized_questions(
    user_id="student123",
    num_questions=10,
    focus_weak_topics=True
)
```

## 📈 Performance Analytics

### **Individual Analytics**
- **Accuracy Percentage** by subject and topic
- **Time Management** analysis with avg time per question
- **Difficulty Progression** tracking improvement over time
- **Weak Topic Identification** with improvement suggestions

### **Comparative Analytics**
- **Leaderboards** among friends and study groups
- **Percentile Tracking** compared to other users
- **Topic-wise Comparison** with peer performance

## 🚀 Advanced Features

### **Machine Learning Components**
- **TF-IDF Vectorization** for question similarity analysis
- **Cosine Similarity** for finding related questions
- **Performance Prediction** using regression models
- **Clustering** students by learning patterns

### **Intelligent Question Selection**
- **Spaced Repetition** for better retention
- **Difficulty Adaptation** based on recent performance
- **Topic Coverage** ensuring balanced practice
- **Exam Pattern Simulation** mimicking actual JEE

## 🛡 Security & Privacy

- **No Personal Data Storage** beyond performance metrics
- **Encrypted API Communications** with secure token handling
- **Local Database** with no cloud dependency for questions
- **GDPR Compliant** data handling practices

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/yourusername/jee-ai-model.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python main.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
