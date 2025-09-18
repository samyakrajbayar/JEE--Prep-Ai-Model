import os
import json
import random
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import requests
import openai
from dataclasses import dataclass
import asyncio
import discord
from discord.ext import commands
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Data structures
@dataclass
class Question:
    id: str
    subject: str
    chapter: str
    topic: str
    difficulty: str
    question_text: str
    options: List[str]
    correct_answer: str
    solution: str
    year: int
    exam_type: str  # JEE Main, JEE Advanced
    question_type: str  # MCQ, Numerical, etc.

@dataclass
class StudentProgress:
    user_id: str
    subject_scores: Dict[str, float]
    weak_topics: List[str]
    strong_topics: List[str]
    total_questions_attempted: int
    correct_answers: int
    last_session: datetime

class JEEDatabase:
    def __init__(self, db_path="jee_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                subject TEXT,
                chapter TEXT,
                topic TEXT,
                difficulty TEXT,
                question_text TEXT,
                options TEXT,
                correct_answer TEXT,
                solution TEXT,
                year INTEGER,
                exam_type TEXT,
                question_type TEXT
            )
        ''')
        
        # Student progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_progress (
                user_id TEXT PRIMARY KEY,
                subject_scores TEXT,
                weak_topics TEXT,
                strong_topics TEXT,
                total_questions_attempted INTEGER,
                correct_answers INTEGER,
                last_session TEXT
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                questions_asked TEXT,
                answers_given TEXT,
                session_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_question(self, question: Question):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO questions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            question.id, question.subject, question.chapter, question.topic,
            question.difficulty, question.question_text, json.dumps(question.options),
            question.correct_answer, question.solution, question.year,
            question.exam_type, question.question_type
        ))
        conn.commit()
        conn.close()
    
    def get_questions_by_filters(self, subject=None, chapter=None, difficulty=None, year=None, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM questions WHERE 1=1"
        params = []
        
        if subject:
            query += " AND subject = ?"
            params.append(subject)
        if chapter:
            query += " AND chapter = ?"
            params.append(chapter)
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        if year:
            query += " AND year = ?"
            params.append(year)
        
        query += f" ORDER BY RANDOM() LIMIT {limit}"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        questions = []
        for row in results:
            question = Question(
                id=row[0], subject=row[1], chapter=row[2], topic=row[3],
                difficulty=row[4], question_text=row[5], options=json.loads(row[6]),
                correct_answer=row[7], solution=row[8], year=row[9],
                exam_type=row[10], question_type=row[11]
            )
            questions.append(question)
        
        return questions
    
    def update_student_progress(self, progress: StudentProgress):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO student_progress VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            progress.user_id,
            json.dumps(progress.subject_scores),
            json.dumps(progress.weak_topics),
            json.dumps(progress.strong_topics),
            progress.total_questions_attempted,
            progress.correct_answers,
            progress.last_session.isoformat()
        ))
        conn.commit()
        conn.close()

class JEESyllabus:
    def __init__(self):
        self.syllabus = {
            "Physics": {
                "Mechanics": [
                    "Kinematics", "Laws of Motion", "Work Energy Power",
                    "Rotational Motion", "Gravitation", "Properties of Matter"
                ],
                "Thermodynamics": [
                    "Thermal Properties", "Kinetic Theory", "Thermodynamics"
                ],
                "Electrodynamics": [
                    "Electrostatics", "Current Electricity", "Magnetic Effects",
                    "Electromagnetic Induction", "AC Circuits", "EM Waves"
                ],
                "Optics": [
                    "Ray Optics", "Wave Optics"
                ],
                "Modern Physics": [
                    "Dual Nature", "Atomic Structure", "Nuclear Physics"
                ]
            },
            "Chemistry": {
                "Physical Chemistry": [
                    "Atomic Structure", "Chemical Bonding", "Gaseous State",
                    "Thermodynamics", "Chemical Equilibrium", "Ionic Equilibrium",
                    "Redox Reactions", "Electrochemistry", "Chemical Kinetics"
                ],
                "Inorganic Chemistry": [
                    "Periodic Table", "Hydrogen", "S-Block Elements",
                    "P-Block Elements", "D-Block Elements", "F-Block Elements",
                    "Coordination Compounds", "Salt Analysis"
                ],
                "Organic Chemistry": [
                    "Basic Concepts", "Hydrocarbons", "Haloalkanes",
                    "Alcohols and Ethers", "Aldehydes and Ketones",
                    "Carboxylic Acids", "Nitrogen Compounds", "Biomolecules"
                ]
            },
            "Mathematics": {
                "Algebra": [
                    "Complex Numbers", "Quadratic Equations", "Sequences and Series",
                    "Permutations and Combinations", "Binomial Theorem",
                    "Matrices and Determinants"
                ],
                "Trigonometry": [
                    "Trigonometric Functions", "Inverse Trigonometric Functions",
                    "Properties of Triangles"
                ],
                "Coordinate Geometry": [
                    "Straight Line", "Circle", "Parabola", "Ellipse", "Hyperbola"
                ],
                "Calculus": [
                    "Limits and Continuity", "Differentiation", "Integration",
                    "Differential Equations", "Application of Derivatives"
                ],
                "Vector and 3D": [
                    "Vector Algebra", "Three Dimensional Geometry"
                ],
                "Statistics and Probability": [
                    "Statistics", "Probability"
                ]
            }
        }
    
    def get_all_topics(self):
        all_topics = []
        for subject, chapters in self.syllabus.items():
            for chapter, topics in chapters.items():
                for topic in topics:
                    all_topics.append((subject, chapter, topic))
        return all_topics
    
    def get_subject_topics(self, subject):
        return self.syllabus.get(subject, {})

class QuestionGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
        self.syllabus = JEESyllabus()
        self.question_templates = {
            "Physics": {
                "MCQ": "Generate a JEE {difficulty} level multiple choice question on {topic} from {chapter}. Include 4 options and detailed solution.",
                "Numerical": "Create a JEE {difficulty} level numerical question on {topic} from {chapter}. Provide step-by-step solution."
            },
            "Chemistry": {
                "MCQ": "Generate a JEE {difficulty} level chemistry MCQ on {topic} from {chapter}. Include 4 options and explanation.",
                "Numerical": "Create a JEE {difficulty} level numerical problem on {topic} from {chapter}. Show complete solution."
            },
            "Mathematics": {
                "MCQ": "Generate a JEE {difficulty} level mathematics MCQ on {topic} from {chapter}. Include 4 options and detailed solution.",
                "Numerical": "Create a JEE {difficulty} level numerical question on {topic} from {chapter}. Provide step-by-step solution."
            }
        }
    
    def generate_question(self, subject, chapter, topic, difficulty="Medium", question_type="MCQ"):
        if not self.api_key:
            return self._generate_sample_question(subject, chapter, topic, difficulty, question_type)
        
        template = self.question_templates[subject][question_type]
        prompt = template.format(difficulty=difficulty, topic=topic, chapter=chapter)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert JEE question generator. Generate high-quality questions similar to previous year papers."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return self._parse_generated_question(response.choices[0].message.content, subject, chapter, topic, difficulty, question_type)
        
        except Exception as e:
            print(f"Error generating question: {e}")
            return self._generate_sample_question(subject, chapter, topic, difficulty, question_type)
    
    def _generate_sample_question(self, subject, chapter, topic, difficulty, question_type):
        # Sample questions for demonstration
        sample_questions = {
            "Physics": {
                "Kinematics": "A particle moves with constant acceleration. If its velocity changes from 10 m/s to 30 m/s in 4 seconds, find the displacement.",
                "Electrostatics": "Two point charges +q and -q are placed at distance 2a. Find the electric field at the midpoint."
            },
            "Chemistry": {
                "Atomic Structure": "Which of the following electronic configurations represents a transition element?",
                "Chemical Bonding": "The hybridization of carbon in CH4 is:"
            },
            "Mathematics": {
                "Complex Numbers": "If z = 3 + 4i, then |z| equals:",
                "Integration": "Evaluate ∫(2x + 3)dx from 0 to 2"
            }
        }
        
        question_text = sample_questions.get(subject, {}).get(topic, f"Sample {subject} question on {topic}")
        
        return Question(
            id=f"gen_{random.randint(1000, 9999)}",
            subject=subject,
            chapter=chapter,
            topic=topic,
            difficulty=difficulty,
            question_text=question_text,
            options=["Option A", "Option B", "Option C", "Option D"] if question_type == "MCQ" else [],
            correct_answer="A" if question_type == "MCQ" else "42",
            solution="Detailed solution would be provided here.",
            year=2024,
            exam_type="Generated",
            question_type=question_type
        )
    
    def _parse_generated_question(self, response_text, subject, chapter, topic, difficulty, question_type):
        # Parse the AI response and create a Question object
        # This is a simplified parser - you'd want more robust parsing
        lines = response_text.strip().split('\n')
        question_text = lines[0] if lines else "Generated question"
        
        return Question(
            id=f"ai_{random.randint(1000, 9999)}",
            subject=subject,
            chapter=chapter,
            topic=topic,
            difficulty=difficulty,
            question_text=question_text,
            options=["Option A", "Option B", "Option C", "Option D"] if question_type == "MCQ" else [],
            correct_answer="A" if question_type == "MCQ" else "42",
            solution="AI generated solution",
            year=2024,
            exam_type="AI Generated",
            question_type=question_type
        )

class AdaptiveLearning:
    def __init__(self, database: JEEDatabase):
        self.database = database
        self.vectorizer = TfidfVectorizer()
    
    def get_personalized_questions(self, user_id: str, num_questions: int = 5):
        # Get user's weak topics and generate questions accordingly
        progress = self.get_user_progress(user_id)
        
        if not progress or not progress.weak_topics:
            # If no progress data, return random questions
            return self.database.get_questions_by_filters(limit=num_questions)
        
        # Focus on weak topics
        weak_topic = random.choice(progress.weak_topics)
        questions = self.database.get_questions_by_filters(topic=weak_topic, limit=num_questions)
        
        return questions
    
    def update_user_performance(self, user_id: str, question: Question, is_correct: bool):
        progress = self.get_user_progress(user_id) or StudentProgress(
            user_id=user_id,
            subject_scores={},
            weak_topics=[],
            strong_topics=[],
            total_questions_attempted=0,
            correct_answers=0,
            last_session=datetime.now()
        )
        
        progress.total_questions_attempted += 1
        if is_correct:
            progress.correct_answers += 1
            
            # Update strong topics
            if question.topic not in progress.strong_topics:
                progress.strong_topics.append(question.topic)
            
            # Remove from weak topics if performing well
            if question.topic in progress.weak_topics:
                progress.weak_topics.remove(question.topic)
        else:
            # Add to weak topics
            if question.topic not in progress.weak_topics:
                progress.weak_topics.append(question.topic)
        
        # Update subject scores
        subject_accuracy = progress.subject_scores.get(question.subject, 0.0)
        progress.subject_scores[question.subject] = (subject_accuracy + (1.0 if is_correct else 0.0)) / 2
        
        progress.last_session = datetime.now()
        self.database.update_student_progress(progress)
    
    def get_user_progress(self, user_id: str) -> Optional[StudentProgress]:
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_progress WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return StudentProgress(
                user_id=result[0],
                subject_scores=json.loads(result[1]),
                weak_topics=json.loads(result[2]),
                strong_topics=json.loads(result[3]),
                total_questions_attempted=result[4],
                correct_answers=result[5],
                last_session=datetime.fromisoformat(result[6])
            )
        return None

class JEEAIModel:
    def __init__(self, openai_api_key=None):
        self.database = JEEDatabase()
        self.question_generator = QuestionGenerator(openai_api_key)
        self.adaptive_learning = AdaptiveLearning(self.database)
        self.syllabus = JEESyllabus()
        self.load_sample_data()
    
    def load_sample_data(self):
        # Load some sample PYQ data
        sample_questions = [
            Question("pyq_001", "Physics", "Mechanics", "Kinematics", "Medium",
                    "A particle moves in a straight line with constant acceleration...",
                    ["20 m", "30 m", "40 m", "50 m"], "C", "Using equations of motion...",
                    2023, "JEE Main", "MCQ"),
            Question("pyq_002", "Chemistry", "Physical Chemistry", "Atomic Structure", "Easy",
                    "The electronic configuration of Cr is:",
                    ["[Ar] 3d⁵ 4s¹", "[Ar] 3d⁴ 4s²", "[Ar] 3d⁶", "[Ar] 3d³ 4s³"], "A",
                    "Chromium has exceptional stability...", 2022, "JEE Main", "MCQ"),
            Question("pyq_003", "Mathematics", "Calculus", "Integration", "Hard",
                    "Evaluate ∫₀^π sin²x cos³x dx",
                    ["2/15", "4/15", "8/15", "16/15"], "C", "Using substitution method...",
                    2023, "JEE Advanced", "MCQ")
        ]
        
        for question in sample_questions:
            self.database.add_question(question)
    
    def get_question_by_difficulty(self, subject=None, difficulty="Medium", count=1):
        return self.database.get_questions_by_filters(subject=subject, difficulty=difficulty, limit=count)
    
    def get_personalized_test(self, user_id: str, subject=None, num_questions=10):
        if subject:
            questions = self.database.get_questions_by_filters(subject=subject, limit=num_questions)
        else:
            questions = self.adaptive_learning.get_personalized_questions(user_id, num_questions)
        
        # Mix with some generated questions
        generated_count = max(1, num_questions // 3)
        for _ in range(generated_count):
            topics = self.syllabus.get_all_topics()
            subject, chapter, topic = random.choice(topics)
            generated_q = self.question_generator.generate_question(subject, chapter, topic)
            questions.append(generated_q)
        
        return questions[:num_questions]
    
    def evaluate_answer(self, user_id: str, question: Question, user_answer: str):
        is_correct = user_answer.upper() == question.correct_answer.upper()
        self.adaptive_learning.update_user_performance(user_id, question, is_correct)
        
        return {
            "correct": is_correct,
            "correct_answer": question.correct_answer,
            "solution": question.solution,
            "explanation": f"The correct answer is {question.correct_answer}. {question.solution}"
        }
    
    def get_user_analytics(self, user_id: str):
        progress = self.adaptive_learning.get_user_progress(user_id)
        if not progress:
            return {"message": "No progress data found. Start practicing to see analytics!"}
        
        accuracy = (progress.correct_answers / progress.total_questions_attempted * 100) if progress.total_questions_attempted > 0 else 0
        
        return {
            "total_questions": progress.total_questions_attempted,
            "correct_answers": progress.correct_answers,
            "accuracy": f"{accuracy:.1f}%",
            "subject_scores": progress.subject_scores,
            "weak_topics": progress.weak_topics,
            "strong_topics": progress.strong_topics,
            "last_session": progress.last_session.strftime("%Y-%m-%d %H:%M")
        }

# Discord Bot Implementation
class JEEBot(commands.Bot):
    def __init__(self, jee_model: JEEAIModel):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.jee_model = jee_model
        self.active_sessions = {}  # user_id -> current_question
    
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
    
    @commands.command(name='start')
    async def start_practice(self, ctx, subject=None):
        """Start a practice session"""
        user_id = str(ctx.author.id)
        
        questions = self.jee_model.get_personalized_test(user_id, subject, 1)
        if not questions:
            await ctx.send("No questions available. Try again later!")
            return
        
        question = questions[0]
        self.active_sessions[user_id] = question
        
        embed = discord.Embed(
            title=f"{question.subject} - {question.chapter}",
            description=question.question_text,
            color=0x00ff00
        )
        
        embed.add_field(name="Difficulty", value=question.difficulty, inline=True)
        embed.add_field(name="Topic", value=question.topic, inline=True)
        embed.add_field(name="Year", value=question.year, inline=True)
        
        if question.options:
            options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(question.options)])
            embed.add_field(name="Options", value=options_text, inline=False)
        
        embed.set_footer(text="Reply with your answer (A/B/C/D) or use !solution for solution")
        await ctx.send(embed=embed)
    
    @commands.command(name='answer')
    async def submit_answer(self, ctx, user_answer: str):
        """Submit answer to current question"""
        user_id = str(ctx.author.id)
        
        if user_id not in self.active_sessions:
            await ctx.send("No active question! Use `!start` to begin.")
            return
        
        question = self.active_sessions[user_id]
        result = self.jee_model.evaluate_answer(user_id, question, user_answer)
        
        embed = discord.Embed(
            title="Answer Result",
            color=0x00ff00 if result["correct"] else 0xff0000
        )
        
        embed.add_field(name="Your Answer", value=user_answer.upper(), inline=True)
        embed.add_field(name="Correct Answer", value=result["correct_answer"], inline=True)
        embed.add_field(name="Result", value="✅ Correct!" if result["correct"] else "❌ Incorrect", inline=True)
        embed.add_field(name="Solution", value=result["solution"], inline=False)
        
        await ctx.send(embed=embed)
        
        # Remove from active sessions
        del self.active_sessions[user_id]
        
        # Ask if they want another question
        await ctx.send("Want another question? Use `!start` or `!start [subject]`")
    
    @commands.command(name='analytics')
    async def show_analytics(self, ctx):
        """Show user's progress analytics"""
        user_id = str(ctx.author.id)
        analytics = self.jee_model.get_user_analytics(user_id)
        
        if "message" in analytics:
            await ctx.send(analytics["message"])
            return
        
        embed = discord.Embed(title="Your JEE Progress", color=0x0099ff)
        embed.add_field(name="Questions Attempted", value=analytics["total_questions"], inline=True)
        embed.add_field(name="Correct Answers", value=analytics["correct_answers"], inline=True)
        embed.add_field(name="Accuracy", value=analytics["accuracy"], inline=True)
        
        if analytics["weak_topics"]:
            embed.add_field(name="Weak Topics", value="\n".join(analytics["weak_topics"][:5]), inline=True)
        
        if analytics["strong_topics"]:
            embed.add_field(name="Strong Topics", value="\n".join(analytics["strong_topics"][:5]), inline=True)
        
        embed.add_field(name="Last Session", value=analytics["last_session"], inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='syllabus')
    async def show_syllabus(self, ctx, subject=None):
        """Show JEE syllabus"""
        syllabus = self.jee_model.syllabus
        
        if subject and subject.title() in syllabus.syllabus:
            subject_data = syllabus.syllabus[subject.title()]
            embed = discord.Embed(title=f"{subject.title()} Syllabus", color=0xff9900)
            
            for chapter, topics in subject_data.items():
                topics_text = ", ".join(topics[:3]) + ("..." if len(topics) > 3 else "")
                embed.add_field(name=chapter, value=topics_text, inline=False)
        else:
            embed = discord.Embed(title="JEE Syllabus Overview", color=0xff9900)
            embed.add_field(name="Subjects", value="Physics\nChemistry\nMathematics", inline=True)
            embed.add_field(name="Usage", value="Use `!syllabus Physics` for detailed syllabus", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='generate')
    async def generate_question(self, ctx, subject: str, difficulty: str = "Medium"):
        """Generate a new question"""
        topics = self.jee_model.syllabus.get_all_topics()
        subject_topics = [t for t in topics if t[0].lower() == subject.lower()]
        
        if not subject_topics:
            await ctx.send("Invalid subject! Use Physics, Chemistry, or Mathematics")
            return
        
        subject_name, chapter, topic = random.choice(subject_topics)
        question = self.jee_model.question_generator.generate_question(
            subject_name, chapter, topic, difficulty
        )
        
        embed = discord.Embed(
            title=f"Generated Question - {subject_name}",
            description=question.question_text,
            color=0x9932cc
        )
        
        embed.add_field(name="Chapter", value=chapter, inline=True)
        embed.add_field(name="Topic", value=topic, inline=True)
        embed.add_field(name="Difficulty", value=difficulty, inline=True)
        
        if question.options:
            options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(question.options)])
            embed.add_field(name="Options", value=options_text, inline=False)
        
        await ctx.send(embed=embed)

# Main execution
if __name__ == "__main__":
    # Initialize the JEE AI Model
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set in Replit secrets
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")    # Set in Replit secrets
    
    jee_model = JEEAIModel(OPENAI_API_KEY)
    
    # Test the model
    print("Testing JEE AI Model...")
    
    # Get sample questions
    questions = jee_model.get_question_by_difficulty("Physics", "Medium", 2)
    for q in questions:
        print(f"\nQuestion: {q.question_text}")
        print(f"Subject: {q.subject}, Topic: {q.topic}")
        print(f"Options: {q.options}")
        print(f"Answer: {q.correct_answer}")
    
    # Test user analytics
    analytics = jee_model.get_user_analytics("test_user")
    print(f"\nUser Analytics: {analytics}")
    
    # Start Discord bot if token is provided
    if DISCORD_TOKEN:
        bot = JEEBot(jee_model)
        print("\nStarting Discord bot...")
        bot.run(DISCORD_TOKEN)
    else:
        print("\nNo Discord token found. Set DISCORD_TOKEN in environment variables to run the bot.")
        
        # Interactive console mode
        print("\nEntering interactive mode...")
        print("Commands: 'question [subject]', 'analytics [user_id]', 'syllabus [subject]', 'quit'")
        
        while True:
            command = input("\n> ").strip().split()
            if not command:
                continue
                
            if command[0] == "quit":
                break
            elif command[0] == "question":
                subject = command[1] if len(command) > 1 else None
                questions = jee_model.get_personalized_test("console_user", subject, 1)
                if questions:
                    q = questions[0]
                    print(f"\nQuestion: {q.question_text}")
                    if q.options:
                        for i, opt in enumerate(q.options):
                            print(f"{chr(65+i)}. {opt}")
                    answer = input("Your answer: ")
                    result = jee_model.evaluate_answer("console_user", q, answer)
                    print(f"{'Correct!' if result['correct'] else 'Incorrect!'}")
                    print(f"Correct answer: {result['correct_answer']}")
                    print(f"Solution: {result['solution']}")
            elif command[0] == "analytics":
                user_id = command[1] if len(command) > 1 else "console_user"
                analytics = jee_model.get_user_analytics(user_id)
                print(f"\nAnalytics for {user_id}:")
                for key, value in analytics.items():
                    print(f"{key}: {value}")
            elif command[0] == "syllabus":
                subject = command[1] if len(command) > 1 else None
                if subject:
                    topics = jee_model.syllabus.get_subject_topics(subject.title())
                    print(f"\n{subject.title()} Syllabus:")
                    for chapter, topic_list in topics.items():
                        print(f"{chapter}: {', '.join(topic_list)}")
                else:
                    print("\nAvailable subjects: Physics, Chemistry, Mathematics")
