#!/usr/bin/env python3
"""
General AI Assistant - Non-coding questions
Handles everyday questions, general knowledge, math, recommendations, etc.
"""

import os
import sys
import json
import requests
import datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
from enum import Enum
import re

# Try to import additional libraries for enhanced functionality
try:
    import wikipedia
    HAS_WIKIPEDIA = True
except ImportError:
    HAS_WIKIPEDIA = False

try:
    import wolframalpha
    HAS_WOLFRAM = True
except ImportError:
    HAS_WOLFRAM = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class QuestionType(Enum):
    GENERAL_KNOWLEDGE = "general_knowledge"
    MATH_CALCULATION = "math_calculation"
    WEATHER = "weather"
    NEWS = "news"
    RECOMMENDATIONS = "recommendations"
    DEFINITIONS = "definitions"
    CONVERSATIONAL = "conversational"
    CREATIVE_WRITING = "creative_writing"
    HEALTH_FITNESS = "health_fitness"
    TRAVEL = "travel"
    COOKING = "cooking"
    ENTERTAINMENT = "entertainment"
    SCIENCE = "science"
    HISTORY = "history"
    TECHNOLOGY = "technology"

@dataclass
class GeneralQuestion:
    question: str
    question_type: QuestionType
    context: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None

@dataclass
class GeneralResponse:
    answer: str
    confidence: float
    sources: List[str] = None
    follow_up_questions: List[str] = None
    additional_info: Optional[str] = None

class GeneralKnowledgeEngine:
    """Handle general knowledge questions using various sources"""
    
    def __init__(self):
        self.logger = logging.getLogger("GeneralKnowledgeEngine")
        self.knowledge_base = self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self) -> Dict[str, Any]:
        """Initialize basic knowledge base"""
        return {
            "greetings": {
                "hello": "Hello! I'm your AI assistant. How can I help you today?",
                "hi": "Hi there! What would you like to know?",
                "good morning": "Good morning! Hope you're having a great day. What can I assist you with?",
                "good afternoon": "Good afternoon! How can I help you today?",
                "good evening": "Good evening! What would you like to know?"
            },
            "basic_facts": {
                "earth": "Earth is the third planet from the Sun and the only known planet with life. It's approximately 4.54 billion years old.",
                "water": "Water (H₂O) is essential for all known forms of life. It covers about 71% of Earth's surface.",
                "gravity": "Gravity is the force that attracts objects toward each other. On Earth, it accelerates objects at 9.8 m/s².",
                "photosynthesis": "Photosynthesis is the process by which plants convert sunlight, carbon dioxide, and water into glucose and oxygen."
            },
            "countries": {
                "usa": {"capital": "Washington, D.C.", "population": "~331 million", "currency": "US Dollar"},
                "france": {"capital": "Paris", "population": "~68 million", "currency": "Euro"},
                "japan": {"capital": "Tokyo", "population": "~125 million", "currency": "Japanese Yen"},
                "brazil": {"capital": "Brasília", "population": "~215 million", "currency": "Brazilian Real"}
            }
        }
    
    def search_knowledge(self, query: str) -> str:
        """Search internal knowledge base"""
        query_lower = query.lower()
        
        # Check greetings
        for greeting, response in self.knowledge_base["greetings"].items():
            if greeting in query_lower:
                return response
        
        # Check basic facts
        for topic, info in self.knowledge_base["basic_facts"].items():
            if topic in query_lower:
                return info
        
        # Check countries
        for country, info in self.knowledge_base["countries"].items():
            if country in query_lower:
                if "capital" in query_lower:
                    return f"The capital of {country.title()} is {info['capital']}."
                elif "population" in query_lower:
                    return f"The population of {country.title()} is approximately {info['population']}."
                elif "currency" in query_lower:
                    return f"The currency of {country.title()} is the {info['currency']}."
                else:
                    return f"{country.title()}: Capital - {info['capital']}, Population - {info['population']}, Currency - {info['currency']}"
        
        return None
    
    def search_wikipedia(self, query: str) -> Optional[str]:
        """Search Wikipedia for information"""
        if not HAS_WIKIPEDIA:
            return None
        
        try:
            # Search for the topic
            results = wikipedia.search(query, results=1)
            if not results:
                return None
            
            # Get the summary
            summary = wikipedia.summary(results[0], sentences=3)
            return f"According to Wikipedia: {summary}"
            
        except Exception as e:
            self.logger.error(f"Wikipedia search failed: {e}")
            return None

class MathEngine:
    """Enhanced math engine for calculations and problem solving"""
    
    def __init__(self):
        self.logger = logging.getLogger("MathEngine")
    
    def solve_basic_math(self, expression: str) -> str:
        """Solve basic mathematical expressions"""
        try:
            # Clean the expression
            cleaned = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            
            # Evaluate safely
            result = eval(cleaned)
            return f"{expression} = {result}"
            
        except Exception as e:
            return f"Could not calculate: {str(e)}"
    
    def solve_word_problems(self, problem: str) -> str:
        """Solve word problems"""
        problem_lower = problem.lower()
        
        # Simple percentage calculations
        if "percent" in problem_lower or "%" in problem:
            numbers = re.findall(r'\d+', problem)
            if len(numbers) >= 2:
                base = float(numbers[0])
                percentage = float(numbers[1])
                result = (base * percentage) / 100
                return f"{percentage}% of {base} is {result}"
        
        # Simple interest calculations
        if "interest" in problem_lower:
            numbers = re.findall(r'\d+', problem)
            if len(numbers) >= 3:
                principal = float(numbers[0])
                rate = float(numbers[1])
                time = float(numbers[2])
                interest = (principal * rate * time) / 100
                return f"Simple interest: Principal={principal}, Rate={rate}%, Time={time} years → Interest={interest}"
        
        # Distance/Speed/Time problems
        if any(word in problem_lower for word in ["speed", "distance", "time", "mph", "km/h"]):
            numbers = re.findall(r'\d+', problem)
            if len(numbers) >= 2:
                return "For distance/speed/time problems: Distance = Speed × Time, Speed = Distance ÷ Time, Time = Distance ÷ Speed"
        
        return "I can help with basic math problems. Try asking about percentages, simple interest, or basic calculations."

class WeatherEngine:
    """Handle weather-related questions"""
    
    def __init__(self):
        self.logger = logging.getLogger("WeatherEngine")
        # In a real implementation, you'd use a weather API key
        self.api_key = os.getenv("WEATHER_API_KEY")
    
    def get_weather_info(self, location: str) -> str:
        """Get weather information for a location"""
        # Simulate weather response since we don't have a real API key
        weather_responses = [
            f"I'd love to help you with weather in {location}! To get real-time weather data, please connect a weather API service like OpenWeatherMap.",
            f"Weather information for {location} requires an API connection. In the meantime, I recommend checking weather.com or your local weather app.",
            f"For accurate weather in {location}, I'd need access to a weather service. Try asking about general weather patterns or climate information instead!"
        ]
        
        import random
        return random.choice(weather_responses)
    
    def get_climate_info(self, location: str) -> str:
        """Get general climate information"""
        climate_info = {
            "tropical": "Tropical climates are hot and humid year-round with distinct wet and dry seasons.",
            "desert": "Desert climates are characterized by very low rainfall and extreme temperature variations.",
            "temperate": "Temperate climates have moderate temperatures with distinct seasons.",
            "arctic": "Arctic climates are extremely cold with long winters and short, cool summers."
        }
        
        location_lower = location.lower()
        
        if any(word in location_lower for word in ["amazon", "equator", "tropical"]):
            return climate_info["tropical"]
        elif any(word in location_lower for word in ["sahara", "desert", "arizona"]):
            return climate_info["desert"]
        elif any(word in location_lower for word in ["europe", "usa", "temperate"]):
            return climate_info["temperate"]
        elif any(word in location_lower for word in ["arctic", "antarctica", "north pole"]):
            return climate_info["arctic"]
        else:
            return f"I don't have specific climate information for {location}, but I can tell you about tropical, desert, temperate, or arctic climates in general."

class RecommendationEngine:
    """Provide recommendations for various topics"""
    
    def __init__(self):
        self.recommendations = {
            "movies": {
                "action": ["The Matrix", "Mad Max: Fury Road", "John Wick", "Mission Impossible", "The Dark Knight"],
                "comedy": ["The Grand Budapest Hotel", "Superbad", "Anchorman", "The Hangover", "Bridesmaids"],
                "drama": ["The Shawshank Redemption", "Forrest Gump", "The Godfather", "Schindler's List", "12 Years a Slave"],
                "sci-fi": ["Blade Runner 2049", "Interstellar", "The Martian", "Ex Machina", "Arrival"],
                "horror": ["Get Out", "A Quiet Place", "Hereditary", "The Conjuring", "It Follows"]
            },
            "books": {
                "fiction": ["To Kill a Mockingbird", "1984", "Pride and Prejudice", "The Great Gatsby", "Harry Potter series"],
                "non-fiction": ["Sapiens", "Educated", "Becoming", "The Immortal Life of Henrietta Lacks", "Atomic Habits"],
                "sci-fi": ["Dune", "The Hitchhiker's Guide to the Galaxy", "Ender's Game", "Foundation", "The Martian"],
                "mystery": ["Gone Girl", "The Girl with the Dragon Tattoo", "Big Little Lies", "The Silent Patient", "In the Woods"]
            },
            "restaurants": {
                "italian": "Try authentic pasta dishes, wood-fired pizzas, and gelato for dessert.",
                "japanese": "Sushi, ramen, tempura, and miso soup are excellent choices.",
                "mexican": "Tacos, burritos, quesadillas, and fresh guacamole are must-tries.",
                "indian": "Curry dishes, naan bread, biryani, and lassi make for a great meal."
            },
            "travel": {
                "europe": ["Paris, France", "Rome, Italy", "Barcelona, Spain", "Amsterdam, Netherlands", "Prague, Czech Republic"],
                "asia": ["Tokyo, Japan", "Bangkok, Thailand", "Singapore", "Seoul, South Korea", "Bali, Indonesia"],
                "americas": ["New York, USA", "Rio de Janeiro, Brazil", "Vancouver, Canada", "Buenos Aires, Argentina", "Mexico City, Mexico"]
            }
        }
    
    def get_recommendations(self, category: str, subcategory: str = None) -> str:
        """Get recommendations for a specific category"""
        category_lower = category.lower()
        
        if category_lower in self.recommendations:
            if subcategory:
                subcategory_lower = subcategory.lower()
                if subcategory_lower in self.recommendations[category_lower]:
                    items = self.recommendations[category_lower][subcategory_lower]
                    if isinstance(items, list):
                        return f"Here are some great {subcategory} {category} recommendations:\n• " + "\n• ".join(items)
                    else:
                        return f"For {subcategory} {category}: {items}"
            else:
                # Return all subcategories
                subcats = list(self.recommendations[category_lower].keys())
                return f"I can recommend {category} in these categories: {', '.join(subcats)}. Which type interests you?"
        
        return f"I don't have specific recommendations for {category} yet, but I'm always learning!"

class ConversationalEngine:
    """Handle casual conversation and personal questions"""
    
    def __init__(self):
        self.responses = {
            "how_are_you": [
                "I'm doing great, thank you for asking! How are you doing today?",
                "I'm functioning well and ready to help! What's on your mind?",
                "I'm excellent! I love learning new things and helping people. How can I assist you?"
            ],
            "what_can_you_do": [
                "I can help with a wide variety of questions! I can assist with general knowledge, math problems, recommendations for movies/books/travel, explain concepts, have conversations, and much more. What would you like to explore?",
                "I'm here to help with everyday questions! Whether you need information, want recommendations, need help with calculations, or just want to chat - I'm ready to assist.",
                "I can answer questions on many topics: science, history, math, give recommendations, explain concepts, help with planning, and have friendly conversations. What interests you?"
            ],
            "thank_you": [
                "You're very welcome! I'm happy to help anytime.",
                "My pleasure! Feel free to ask me anything else.",
                "Glad I could help! Is there anything else you'd like to know?"
            ],
            "goodbye": [
                "Goodbye! Have a wonderful day!",
                "Take care! Feel free to come back anytime with more questions.",
                "See you later! I'm always here when you need assistance."
            ]
        }
    
    def get_conversational_response(self, message: str) -> str:
        """Generate conversational responses"""
        message_lower = message.lower()
        
        if any(phrase in message_lower for phrase in ["how are you", "how do you do", "how's it going"]):
            import random
            return random.choice(self.responses["how_are_you"])
        
        elif any(phrase in message_lower for phrase in ["what can you do", "what do you do", "help me", "capabilities"]):
            import random
            return random.choice(self.responses["what_can_you_do"])
        
        elif any(phrase in message_lower for phrase in ["thank you", "thanks", "appreciate"]):
            import random
            return random.choice(self.responses["thank_you"])
        
        elif any(phrase in message_lower for phrase in ["goodbye", "bye", "see you", "farewell"]):
            import random
            return random.choice(self.responses["goodbye"])
        
        elif "tell me about yourself" in message_lower:
            return "I'm an AI assistant designed to help with everyday questions and tasks. I enjoy learning about different topics and helping people find the information they need. I can assist with general knowledge, math, recommendations, explanations, and friendly conversation!"
        
        elif "joke" in message_lower:
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the math book look so sad? Because it had too many problems!",
                "What do you call a fake noodle? An impasta!",
                "Why don't eggs tell jokes? They'd crack each other up!"
            ]
            import random
            return random.choice(jokes)
        
        return None

class GeneralAIAssistant:
    """Main general AI assistant class"""
    
    def __init__(self):
        self.knowledge_engine = GeneralKnowledgeEngine()
        self.math_engine = MathEngine()
        self.weather_engine = WeatherEngine()
        self.recommendation_engine = RecommendationEngine()
        self.conversational_engine = ConversationalEngine()
        self.logger = logging.getLogger("GeneralAIAssistant")
    
    def classify_question(self, question: str) -> QuestionType:
        """Classify the type of question being asked"""
        question_lower = question.lower()
        
        # Math-related keywords
        if any(word in question_lower for word in ["calculate", "math", "equation", "solve", "+", "-", "*", "/", "percent", "%", "interest"]):
            return QuestionType.MATH_CALCULATION
        
        # Weather-related keywords
        elif any(word in question_lower for word in ["weather", "temperature", "rain", "sunny", "cloudy", "forecast", "climate"]):
            return QuestionType.WEATHER
        
        # Recommendation keywords
        elif any(word in question_lower for word in ["recommend", "suggest", "best", "good", "movie", "book", "restaurant", "travel", "visit"]):
            return QuestionType.RECOMMENDATIONS
        
        # Definition keywords
        elif any(word in question_lower for word in ["what is", "define", "definition", "meaning", "explain"]):
            return QuestionType.DEFINITIONS
        
        # Conversational keywords
        elif any(word in question_lower for word in ["hello", "hi", "how are you", "thank you", "goodbye", "joke"]):
            return QuestionType.CONVERSATIONAL
        
        # Science keywords
        elif any(word in question_lower for word in ["science", "physics", "chemistry", "biology", "atom", "molecule", "gravity"]):
            return QuestionType.SCIENCE
        
        # History keywords
        elif any(word in question_lower for word in ["history", "historical", "when did", "who was", "ancient", "war", "empire"]):
            return QuestionType.HISTORY
        
        # Health keywords
        elif any(word in question_lower for word in ["health", "fitness", "exercise", "diet", "nutrition", "calories"]):
            return QuestionType.HEALTH_FITNESS
        
        # Default to general knowledge
        else:
            return QuestionType.GENERAL_KNOWLEDGE
    
    def process_question(self, question: str, context: str = None) -> GeneralResponse:
        """Process a general question and return a response"""
        try:
            question_type = self.classify_question(question)
            
            if question_type == QuestionType.CONVERSATIONAL:
                response = self.conversational_engine.get_conversational_response(question)
                if response:
                    return GeneralResponse(
                        answer=response,
                        confidence=0.9,
                        follow_up_questions=["Is there anything else I can help you with?"]
                    )
            
            elif question_type == QuestionType.MATH_CALCULATION:
                # Check if it's a basic calculation
                if any(op in question for op in ['+', '-', '*', '/', '=']):
                    response = self.math_engine.solve_basic_math(question)
                else:
                    response = self.math_engine.solve_word_problems(question)
                
                return GeneralResponse(
                    answer=response,
                    confidence=0.8,
                    follow_up_questions=["Would you like me to solve another math problem?"]
                )
            
            elif question_type == QuestionType.WEATHER:
                # Extract location if mentioned
                location = "your location"
                for word in question.split():
                    if word.lower() in ["in", "at", "for"] and len(question.split()) > question.split().index(word) + 1:
                        location = question.split()[question.split().index(word) + 1]
                        break
                
                if "climate" in question.lower():
                    response = self.weather_engine.get_climate_info(location)
                else:
                    response = self.weather_engine.get_weather_info(location)
                
                return GeneralResponse(
                    answer=response,
                    confidence=0.7,
                    follow_up_questions=["Would you like information about weather in another location?"]
                )
            
            elif question_type == QuestionType.RECOMMENDATIONS:
                # Extract category and subcategory
                question_lower = question.lower()
                
                if "movie" in question_lower:
                    category = "movies"
                    subcategory = None
                    for genre in ["action", "comedy", "drama", "sci-fi", "horror"]:
                        if genre in question_lower:
                            subcategory = genre
                            break
                elif "book" in question_lower:
                    category = "books"
                    subcategory = None
                    for genre in ["fiction", "non-fiction", "sci-fi", "mystery"]:
                        if genre in question_lower:
                            subcategory = genre
                            break
                elif "restaurant" in question_lower or "food" in question_lower:
                    category = "restaurants"
                    subcategory = None
                    for cuisine in ["italian", "japanese", "mexican", "indian"]:
                        if cuisine in question_lower:
                            subcategory = cuisine
                            break
                elif "travel" in question_lower or "visit" in question_lower:
                    category = "travel"
                    subcategory = None
                    for region in ["europe", "asia", "americas"]:
                        if region in question_lower:
                            subcategory = region
                            break
                else:
                    category = "general"
                
                if category != "general":
                    response = self.recommendation_engine.get_recommendations(category, subcategory)
                else:
                    response = "I can recommend movies, books, restaurants, or travel destinations. What type of recommendations are you looking for?"
                
                return GeneralResponse(
                    answer=response,
                    confidence=0.8,
                    follow_up_questions=["Would you like recommendations in a different category?"]
                )
            
            else:
                # Try knowledge base first
                response = self.knowledge_engine.search_knowledge(question)
                
                if not response and HAS_WIKIPEDIA:
                    response = self.knowledge_engine.search_wikipedia(question)
                
                if not response:
                    response = f"I'd be happy to help with your question: '{question}'. Could you provide a bit more context or try rephrasing it? I can assist with general knowledge, math problems, recommendations, weather information, and much more!"
                
                return GeneralResponse(
                    answer=response,
                    confidence=0.6,
                    follow_up_questions=[
                        "Would you like me to explain this in more detail?",
                        "Is there a specific aspect you'd like to know more about?"
                    ]
                )
        
        except Exception as e:
            self.logger.error(f"Error processing question: {e}")
            return GeneralResponse(
                answer=f"I encountered an error while processing your question. Please try rephrasing it or ask something else!",
                confidence=0.1
            )

def main():
    """Test the general AI assistant"""
    print("General AI Assistant - Non-Coding Questions")
    print("=" * 50)
    
    assistant = GeneralAIAssistant()
    
    test_questions = [
        "Hello, how are you?",
        "What is 25% of 200?",
        "Can you recommend a good action movie?",
        "What's the weather like in Paris?",
        "What is photosynthesis?",
        "Tell me a joke",
        "What's the capital of France?",
        "Calculate 15 + 27 * 3",
        "Recommend some books for science fiction fans",
        "Thank you for your help!"
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = assistant.process_question(question)
        print(f"A: {response.answer}")
        if response.follow_up_questions:
            print(f"Follow-up: {response.follow_up_questions[0]}")
        print("-" * 30)

if __name__ == "__main__":
    main()