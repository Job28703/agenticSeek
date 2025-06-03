import os
import sys
import torch
import random
from typing import List, Tuple, Type, Dict

from transformers import pipeline
from adaptive_classifier import AdaptiveClassifier

from sources.agents.agent import Agent
from sources.agents.code_agent import CoderAgent
from sources.agents.casual_agent import CasualAgent
from sources.agents.planner_agent import FileAgent
from sources.agents.browser_agent import BrowserAgent
from sources.agents.collaborative_agent import CollaborativeAgent, AgentTask, CollaborationMode
from sources.language import LanguageUtility
from sources.utility import pretty_print, animate_thinking, timer_decorator
from sources.logger import Logger

class AgentRouter:
    """
    AgentRouter is a class that selects the appropriate agent based on the user query.
    """
    def __init__(self, agents: list, supported_language: List[str] = ["en", "fr", "zh"]):
        self.agents = agents
        self.logger = Logger("router.log")
        self.lang_analysis = LanguageUtility(supported_language=supported_language)
        self.pipelines = self.load_pipelines()
        self.talk_classifier = self.load_llm_router()
        self.complexity_classifier = self.load_llm_router()
        self.learn_few_shots_tasks()
        self.learn_few_shots_complexity()
        self.asked_clarify = False

        # 初始化協作代理管理器
        agent_dict = {agent.role: agent for agent in agents}
        self.collaborative_agent = CollaborativeAgent(agent_dict, max_parallel_tasks=3)
    
    def load_pipelines(self) -> Dict[str, Type[pipeline]]:
        """
        Load the pipelines for the text classification used for routing.
        returns:
            Dict[str, Type[pipeline]]: The loaded pipelines
        """
        animate_thinking("Loading zero-shot pipeline...", color="status")
        return {
            "bart": pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        }

    def load_llm_router(self) -> AdaptiveClassifier:
        """
        Load the LLM router model.
        returns:
            AdaptiveClassifier: The loaded model
        exceptions:
            Exception: If the safetensors fails to load
        """
        path = "../llm_router" if __name__ == "__main__" else "./llm_router"
        try:
            animate_thinking("Loading LLM router model...", color="status")
            talk_classifier = AdaptiveClassifier.from_pretrained(path)
        except Exception as e:
            raise Exception("Failed to load the routing model. Please run the dl_safetensors.sh script inside llm_router/ directory to download the model.")
        return talk_classifier

    def get_device(self) -> str:
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda:0"
        else:
            return "cpu"
    
    def learn_few_shots_complexity(self) -> None:
        """
        Few shot learning for complexity estimation.
        Use the build in add_examples method of the Adaptive_classifier.
        """
        few_shots = [
            ("hi", "LOW"),
            ("How it's going ?", "LOW"),
            ("What’s the weather like today?", "LOW"),
            ("Can you find a file named ‘notes.txt’ in my Documents folder?", "LOW"),
            ("Write a Python script to generate a random password", "LOW"),
            ("Debug this JavaScript code that’s not running properly", "LOW"),
            ("Search the web for the cheapest laptop under $500", "LOW"),
            ("Locate a file called ‘report_2024.pdf’ on my drive", "LOW"),
            ("Check if a folder named ‘Backups’ exists on my system", "LOW"),
            ("Can you find ‘family_vacation.mp4’ in my Videos folder?", "LOW"),
            ("Search my drive for a file named ‘todo_list.xlsx’", "LOW"),
            ("Write a Python function to check if a string is a palindrome", "LOW"),
            ("Can you search the web for startups in Berlin?", "LOW"),
            ("Find recent articles on blockchain technology online", "LOW"),
            ("Check if ‘Personal_Projects’ folder exists on my desktop", "LOW"),
            ("Create a bash script to list all running processes", "LOW"),
            ("Debug this Python script that’s crashing on line 10", "LOW"),
            ("Browse the web to find out who invented Python", "LOW"),
            ("Locate a file named ‘shopping_list.txt’ on my system", "LOW"),
            ("Search the web for tips on staying productive", "LOW"),
            ("Find ‘sales_pitch.pptx’ in my Downloads folder", "LOW"),
            ("can you find a file called resume.docx on my drive?", "LOW"),
            ("can you write a python script to check if the device on my network is connected to the internet", "LOW"),
            ("can you debug this Java code? It’s not working.", "LOW"),
            ("can you find the old_project.zip file somewhere on my drive?", "LOW"),
            ("can you locate the backup folder I created last month on my system?", "LOW"),
            ("could you check if the presentation.pdf file exists in my downloads?", "LOW"),
            ("search my drive for a file called vacation_photos_2023.jpg.", "LOW"),
            ("help me organize my desktop files into folders by type.", "LOW"),
            ("make a blackjack in golang", "LOW"),
            ("write a python script to ping a website", "LOW"),
            ("write a simple Java program to print 'Hello World'", "LOW"),
            ("write a Java program to calculate the area of a circle", "LOW"),
            ("write a Python function to sort a list of dictionaries by key", "LOW"),
            ("can you search for startup in tokyo?", "LOW"),
            ("find the latest updates on quantum computing on the web", "LOW"),
            ("check if the folder ‘Work_Projects’ exists on my desktop", "LOW"),
            (" can you browse the web, use overpass-turbo to show fountains in toulouse", "LOW"),
            ("search the web for the best budget smartphones of 2025", "LOW"),
            ("write a Python script to download all images from a webpage", "LOW"),
            ("create a bash script to monitor CPU usage", "LOW"),
            ("debug this C++ code that keeps crashing", "LOW"),
            ("can you browse the web to find out who fosowl is ?", "LOW"),
            ("find the file ‘important_notes.txt’", "LOW"),
            ("search the web for the best ways to learn a new language", "LOW"),
            ("locate the file ‘presentation.pptx’ in my Documents folder", "LOW"),
            ("Make a 3d game in javascript using three.js", "LOW"),
            ("Find the latest research papers on AI and build save in a file", "HIGH"),
            ("Make a web server in go that serve a simple html page", "LOW"),
            ("Search the web for the cheapest 4K monitor and provide a link", "LOW"),
            ("Write a JavaScript function to reverse a string", "LOW"),
            ("Can you locate a file called ‘budget_2025.xlsx’ on my system?", "LOW"),
            ("Search the web for recent articles on space exploration", "LOW"),
            ("when is the exam period for master student in france?", "LOW"),
            ("Check if a folder named ‘Photos_2024’ exists on my desktop", "LOW"),
            ("Can you look up some nice knitting patterns on that web thingy?", "LOW"),
            ("Goodness, check if my ‘Photos_Grandkids’ folder is still on the desktop", "LOW"),
            ("Create a Python script to rename all files in a folder based on their creation date", "LOW"),
            ("Can you find a file named ‘meeting_notes.txt’ in my Downloads folder?", "LOW"),
            ("Write a Go program to check if a port is open on a network", "LOW"),
            ("Search the web for the latest electric car reviews", "LOW"),
            ("Write a Python function to merge two sorted lists", "LOW"),
            ("Create a bash script to monitor disk space and alert via text file", "LOW"),
            ("What’s out there on the web about cheap travel spots?", "LOW"),
            ("Search X for posts about AI ethics and summarize them", "LOW"),
            ("Check if a file named ‘project_proposal.pdf’ exists in my Documents", "LOW"),
            ("Search the web for tips on improving coding skills", "LOW"),
            ("Write a Python script to count words in a text file", "LOW"),
            ("Search the web for restaurant", "LOW"),
            ("Use a MCP to find the latest stock market data", "LOW"),
            ("Use a MCP to send an email to my boss", "LOW"),
            ("Could you use a MCP to find the latest news on climate change?", "LOW"),
            ("Create a simple HTML page with CSS styling", "LOW"),
            ("Use file.txt and then use it to ...", "HIGH"),
            ("Yo, what’s good? Find my ‘mixtape.mp3’ real quick", "LOW"),
            ("Can you follow the readme and install the project", "HIGH"),
            ("Man, write me a dope Python script to flex some random numbers", "LOW"),
            ("Search the web for peer-reviewed articles on gene editing", "LOW"),
            ("Locate ‘meeting_notes.docx’ in Downloads, I’m late for this call", "LOW"),
            ("Make the game less hard", "LOW"),
            ("Why did it fail?", "LOW"),
            ("Write a Python script to list all .pdf files in my Documents", "LOW"),
            ("Write a Python thing to sort my .jpg files by date", "LOW"),
            ("make a snake game please", "LOW"),
            ("Find ‘gallery_list.pdf’, then build a web app to show my pics", "HIGH"),
            ("Find ‘budget_2025.xlsx’, analyze it, and make a chart for my boss", "HIGH"),
            ("I want you to make me a plan to travel to Tainan", "HIGH"),
            ("Retrieve the latest publications on CRISPR and develop a web application to display them", "HIGH"),
            ("Bro dig up a music API and build me a tight app for the hottest tracks", "HIGH"),
            ("Find a public API for sports scores and build a web app to show live updates", "HIGH"),
            ("Find a public API for book data and create a Flask app to list bestsellers", "HIGH"),
            ("Organize my desktop files by extension and then write a script to list them", "HIGH"),
            ("Find the latest research on renewable energy and build a web app to display it", "HIGH"),
            ("search online for popular sci-fi movies from 2024 and pick three to watch tonight. Save the list in movie_night.txt", "HIGH"),
            ("can you find vitess repo, clone it and install by following the readme", "HIGH"),
            ("Create a JavaScript game using Phaser.js with multiple levels", "HIGH"),
            ("Search the web for the latest trends in web development and build a sample site", "HIGH"),
            ("Use my research_note.txt file, double check the informations on the web", "HIGH"),
            ("Make a web server in go that query a flight API and display them in a app", "HIGH"),
            ("Search the web for top cafes in Rennes, France, and save a list of three with their addresses in rennes_cafes.txt.", "HIGH"),
            ("Search the web for the latest trends in AI and demo it in pytorch", "HIGH"),
            ("can you lookup for api that track flight and build a web flight tracking app", "HIGH"),
            ("Find the file toto.pdf then use its content to reply to Jojo on superforum.com", "HIGH"),
            ("Create a whole web app in python using the flask framework that query news API", "HIGH"),
            ("Create a bash script that monitor the CPU usage and send an email if it's too high", "HIGH"),
            ("Make a web search for latest news on the stock market and display them with python", "HIGH"),
            ("Find my resume file, apply to job that might fit online", "HIGH"),
            ("Can you find a weather API and build a Python app to display current weather", "HIGH"),
            ("Create a Python web app using Flask to track cryptocurrency prices from an API", "HIGH"),
            ("Search the web for tutorials on machine learning and build a simple ML model in Python", "HIGH"),
            ("Find a public API for movie data and build a web app to display movie ratings", "HIGH"),
            ("Create a Node.js server that queries a public API for traffic data and displays it", "HIGH"),
            ("can you find api and build a python web app with it ?", "HIGH"),
            ("do a deep search of current AI player for 2025 and make me a report in a file", "HIGH"),
            ("Find a public API for recipe data and build a web app to display recipes", "HIGH"),
            ("Search the web for recent space mission updates and build a Flask app", "HIGH"),
            ("Create a Python script to scrape a website and save data to a database", "HIGH"),
            ("Find a shakespear txt then train a transformers on it to generate text", "HIGH"),
            ("Find a public API for fitness tracking and build a web app to show stats", "HIGH"),
            ("Search the web for tutorials on web development and build a sample site", "HIGH"),
            ("Create a Node.js app to query a public API for event listings and display them", "HIGH"),
            ("Find a file named ‘budget.xlsx’, analyze its data, and generate a chart", "HIGH"),
        ]
        random.shuffle(few_shots)
        texts = [text for text, _ in few_shots]
        labels = [label for _, label in few_shots]
        self.complexity_classifier.add_examples(texts, labels)

    def learn_few_shots_tasks(self) -> None:
        """
        Few shot learning for tasks classification.
        Use the build in add_examples method of the Adaptive_classifier.
        """
        few_shots = [
            ("Write a python script to check if the device on my network is connected to the internet", "coding"),
            ("Hey could you search the web for the latest news on the tesla stock market ?", "web"),
            ("I would like you to search for weather api", "web"),
            ("Plan a 3-day trip to New York, including flights and hotels.", "web"),
            ("Find on the web the latest research papers on AI.", "web"),
            ("Can you debug this Java code? It’s not working.", "code"),
            ("Can you browse the web and find me a 4090 for cheap?", "web"),
            ("i would like to setup a new AI project, index as mark2", "files"),
            ("Hey, can you find the old_project.zip file somewhere on my drive?", "files"),
            ("Tell me a funny story", "talk"),
            ("can you make a snake game in python", "code"),
            ("Can you locate the backup folder I created last month on my system?", "files"),
            ("Share a random fun fact about space.", "talk"),
            ("Write a script to rename all files in a directory to lowercase.", "files"),
            ("Could you check if the presentation.pdf file exists in my downloads?", "files"),
            ("Tell me about the weirdest dream you’ve ever heard of.", "talk"),
            ("Search my drive for a file called vacation_photos_2023.jpg.", "files"),
            ("Help me organize my desktop files into folders by type.", "files"),
            ("What’s your favorite movie and why?", "talk"),
            ("what directory are you in ?", "files"),
            ("what files you seing rn ?", "files"),
            ("When is the period of university exam in france ?", "web"),
            ("Search my drive for a file named budget_2024.xlsx", "files"),
            ("Write a Python function to sort a list of dictionaries by key", "code"),
            ("Find the latest updates on quantum computing on the web", "web"),
            ("Check if the folder ‘Work_Projects’ exists on my desktop", "files"),
            ("Create a bash script to monitor CPU usage", "code"),
            ("Search online for the best budget smartphones of 2025", "web"),
            ("What’s the strangest food combination you’ve heard of?", "talk"),
            ("Move all .txt files from Downloads to a new folder called Notes", "files"),
            ("Debug this C++ code that keeps crashing", "code"),
            ("can you browse the web to find out who fosowl is ?", "web"),
            ("Find the file ‘important_notes.txt’", "files"),
            ("Find out the latest news on the upcoming Mars mission", "web"),
            ("Write a Java program to calculate the area of a circle", "code"),
            ("Search the web for the best ways to learn a new language", "web"),
            ("Locate the file ‘presentation.pptx’ in my Documents folder", "files"),
            ("Write a Python script to download all images from a webpage", "code"),
            ("Search the web for the latest trends in AI and machine learning", "web"),
            ("Tell me about a time when you had to solve a difficult problem", "talk"),
            ("Organize all image files on my desktop into a folder called ‘Pictures’", "files"),
            ("Generate a Ruby script to calculate Fibonacci numbers up to 100", "code"),
            ("Find out what device are connected to my network", "code"),
            ("Show me how much disk space is left on my drive", "code"),
            ("Look up recent posts on X about climate change", "web"),
            ("Find the photo I took last week named sunset_beach.jpg", "files"),
            ("Write a JavaScript snippet to fetch data from an API", "code"),
            ("Search the web for tutorials on machine learning with Python", "web"),
            ("Locate the file ‘meeting_notes.docx’ in my Documents folder", "files"),
            ("Write a Python script to scrape a website’s title and links", "code"),
            ("Search the web for the latest breakthroughs in fusion energy", "web"),
            ("Tell me about a historical event that sounds too wild to be true", "talk"),
            ("Organize all image files on my desktop into a folder called ‘Pictures’", "files"),
            ("Generate a Ruby script to calculate Fibonacci numbers up to 100", "code"),
            ("Find recent X posts about SpaceX’s next rocket launch", "web"),
            ("What’s the funniest misunderstanding you’ve seen between humans and AI?", "talk"),
            ("Check if ‘backup_032025.zip’ exists anywhere on my drive", "files" ),
            ("Create a shell script to automate backups of a directory", "code"),
            ("Look up the top AI conferences happening in 2025 online", "web"),
            ("Write a C# program to simulate a basic calculator", "code"),
            ("Browse the web for open-source alternatives to Photoshop", "web"),
            ("Hey how are you", "talk"),
            ("Write a Python script to ping a website", "code"),
            ("Search the web for the latest iPhone release", "web"),
            ("What’s the weather like today?", "web"),
            ("Hi, how’s your day going?", "talk"),
            ("Can you find a file called resume.docx on my drive?", "files"),
            ("Write a simple Java program to print 'Hello World'", "code"),
            ("can you find the current stock of Tesla?", "web"),
            ("Tell me a quick joke", "talk"),
            ("Search online for the best coffee shops in Seattle", "web"),
            ("Check if ‘project_plan.pdf’ exists in my Downloads folder", "files"),
            ("What’s your favorite color?", "talk"),
            ("Write a bash script to list all files in a directory", "code"),
            ("Find recent X posts about electric cars", "web"),
            ("Hey, you doing okay?", "talk"),
            ("Locate the file ‘family_photo.jpg’ on my system", "files"),
            ("Search the web for beginner guitar lessons", "web"),
            ("Write a Python function to reverse a string", "code"),
            ("What’s the weirdest animal you know of?", "talk"),
            ("Organize all .pdf files on my desktop into a ‘Documents’ folder", "files"),
            ("Browse the web for the latest space mission updates", "web"),
            ("Hey, what’s up with you today?", "talk"),
            ("Write a JavaScript function to add two numbers", "code"),
            ("Find the file ‘notes.txt’ in my Documents folder", "files"),
            ("Tell me something random about the ocean", "talk"),
            ("Search the web for cheap flights to Paris", "web"),
            ("Check if ‘budget.xlsx’ is on my drive", "files"),
            ("Write a Python script to count words in a text file", "code"),
            ("How’s it going today?", "talk"),
            ("Find recent X posts about AI advancements", "web"),
            ("Move all .jpg files from Downloads to a ‘Photos’ folder", "files"),
            ("Search online for the best laptops of 2025", "web"),
            ("What’s the funniest thing you’ve heard lately?", "talk"),
            ("Write a Ruby script to generate random numbers", "code"),
            ("Hey, how’s everything with you?", "talk"),
            ("Locate ‘meeting_agenda.docx’ in my system", "files"),
            ("Search the web for tips on growing indoor plants", "web"),
            ("Write a C++ program to calculate the sum of an array", "code"),
            ("Tell me a fun fact about dogs", "talk"),
            ("Check if the folder ‘Old_Projects’ exists on my desktop", "files"),
            ("Browse the web for the latest gaming console reviews", "web"),
            ("Hi, how are you feeling today?", "talk"),
            ("Write a Python script to check disk space", "code"),
            ("Find the file ‘vacation_itinerary.pdf’ on my drive", "files"),
            ("Search the web for news on renewable energy", "web"),
            ("What’s the strangest thing you’ve learned recently?", "talk"),
            ("Organize all video files into a ‘Videos’ folder", "files"),
            ("Write a shell script to delete temporary files", "code"),
            ("Hey, how’s your week been so far?", "talk"),
            ("Search online for the top movies of 2025", "web"),
            ("Locate ‘taxes_2024.xlsx’ in my Documents folder", "files"),
            ("Tell me about a cool invention from history", "talk"),
            ("Write a Java program to check if a number is even or odd", "code"),
            ("Find recent X posts about cryptocurrency trends", "web"),
            ("Hey, you good today?", "talk"),
            ("Search the web for easy dinner recipes", "web"),
            ("Check if ‘photo_backup.zip’ exists on my drive", "files"),
            ("Write a Python script to rename files with a timestamp", "code"),
            ("What’s your favorite thing about space?", "talk"),
            ("search for GPU with at least 24gb vram", "web"),
            ("Browse the web for the latest fitness trends", "web"),
            ("Move all .docx files to a ‘Work’ folder", "files"),
            ("I would like to make a new project called 'new_project'", "files"),
            ("I would like to setup a new project index as mark2", "files"),
            ("can you create a 3d js game that run in the browser", "code"),
            ("can you make a web app in python that use the flask framework", "code"),
            ("can you build a web server in go that serve a simple html page", "code"),
            ("can you find out who Jacky yougouri is ?", "web"),
            ("Can you use MCP to find stock market for IBM ?", "mcp"),
            ("Can you use MCP to to export my contacts to a csv file?", "mcp"),
            ("Can you use a MCP to find write notes to flomo", "mcp"),
            ("Can you use a MCP to query my calendar and find the next meeting?", "mcp"),
            ("Can you use a mcp to get the distance between Shanghai and Paris?", "mcp"),
            ("Setup a new flutter project called 'new_flutter_project'", "files"),
            ("can you create a new project called 'new_project'", "files"),
            ("can you make a simple web app that display a list of files in my dir", "code"),
            ("can you build a simple web server in python that serve a html page", "code"),
            ("find and buy me the latest rtx 4090", "web"),
            ("What are some good netflix show like Altered Carbon ?", "web"),
            ("can you find the latest research paper on AI", "web"),
            ("can you find research.pdf in my drive", "files"),
            ("hi", "talk"),
            ("hello", "talk"),
        ]
        random.shuffle(few_shots)
        texts = [text for text, _ in few_shots]
        labels = [label for _, label in few_shots]
        self.talk_classifier.add_examples(texts, labels)

    def llm_router(self, text: str) -> tuple:
        """
        Inference of the LLM router model.
        Args:
            text: The input text
        """
        predictions = self.talk_classifier.predict(text)
        predictions = [pred for pred in predictions if pred[0] not in ["HIGH", "LOW"]]
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
        return predictions[0]
    
    def router_vote(self, text: str, labels: list, log_confidence:bool = False) -> str:
        """
        Vote between the LLM router and BART model.
        Args:
            text: The input text
            labels: The labels to classify
        Returns:
            str: The selected label
        """
        if len(text) <= 8:
            return "talk"
        result_bart = self.pipelines['bart'](text, labels)
        result_llm_router = self.llm_router(text)
        bart, confidence_bart = result_bart['labels'][0], result_bart['scores'][0]
        llm_router, confidence_llm_router = result_llm_router[0], result_llm_router[1]
        final_score_bart = confidence_bart / (confidence_bart + confidence_llm_router)
        final_score_llm = confidence_llm_router / (confidence_bart + confidence_llm_router)
        self.logger.info(f"Routing Vote for text {text}: BART: {bart} ({final_score_bart}) LLM-router: {llm_router} ({final_score_llm})")
        if log_confidence:
            pretty_print(f"Agent choice -> BART: {bart} ({final_score_bart}) LLM-router: {llm_router} ({final_score_llm})")
        return bart if final_score_bart > final_score_llm else llm_router
    
    def find_first_sentence(self, text: str) -> str:
        first_sentence = None
        for line in text.split("\n"):
            first_sentence = line.strip()
            break
        if first_sentence is None:
            first_sentence = text
        return first_sentence
    
    def estimate_complexity(self, text: str) -> str:
        """
        Estimate the complexity of the text.
        Args:
            text: The input text
        Returns:
        str: The estimated complexity
        """
        try:
            predictions = self.complexity_classifier.predict(text)
        except Exception as e:
            pretty_print(f"Error in estimate_complexity: {str(e)}", color="failure")
            return "LOW"
        predictions = sorted(predictions, key=lambda x: x[1], reverse=True)
        if len(predictions) == 0:
            return "LOW"
        complexity, confidence = predictions[0][0], predictions[0][1]
        if confidence < 0.5:
            self.logger.info(f"Low confidence in complexity estimation: {confidence}")
            return "HIGH"
        if complexity == "HIGH":
            return "HIGH"
        elif complexity == "LOW":
            return "LOW"
        pretty_print(f"Failed to estimate the complexity of the text.", color="failure")
        return "LOW"
    
    def find_planner_agent(self) -> Agent:
        """
        Find the planner agent.
        Returns:
            Agent: The planner agent
        """
        for agent in self.agents:
            if agent.type == "planner_agent":
                return agent
        pretty_print(f"Error finding planner agent. Please add a planner agent to the list of agents.", color="failure")
        self.logger.error("Planner agent not found.")
        return None
    
    def select_agent(self, text: str) -> Agent:
        """
        Enhanced agent selection with collaborative task detection.
        Args:
            text (str): The text to select the agent from
        Returns:
            Agent: The selected agent or collaborative agent manager
        """
        assert len(self.agents) > 0, "No agents available."
        if len(self.agents) == 1:
            return self.agents[0]

        # 檢測協作任務
        if self.detect_collaborative_task(text):
            pretty_print(f"🤝 Collaborative task detected, preparing multi-agent execution", color="info")
            # 返回一個特殊的協作代理標識
            class CollaborativeTaskAgent:
                def __init__(self, router):
                    self.router = router
                    self.agent_name = "Collaborative Agent Manager"
                    self.role = "collaborative"
                    self.type = "collaborative_agent"

                async def process(self, prompt, speech_module):
                    return await self.router.execute_collaborative_task(prompt)

            return CollaborativeTaskAgent(self)

        lang = self.lang_analysis.detect_language(text)
        text = self.find_first_sentence(text)
        text = self.lang_analysis.translate(text, lang)
        labels = [agent.role for agent in self.agents]
        complexity = self.estimate_complexity(text)

        if complexity == "HIGH":
            pretty_print(f"Complex task detected, routing to planner agent.", color="info")
            return self.find_planner_agent()

        try:
            best_agent = self.router_vote(text, labels, log_confidence=False)
        except Exception as e:
            raise e

        for agent in self.agents:
            if best_agent == agent.role:
                role_name = agent.role
                pretty_print(f"Selected agent: {agent.agent_name} (roles: {role_name})", color="warning")
                return agent

        pretty_print(f"Error choosing agent.", color="failure")
        self.logger.error("No agent selected.")
        return None

    def detect_collaborative_task(self, text: str) -> bool:
        """
        檢測是否為需要多代理協作的任務（使用 MVP 檢測器）

        Args:
            text: 用戶輸入文本

        Returns:
            bool: 是否需要協作
        """
        # 使用 MVP 協作檢測器
        if not hasattr(self, '_mvp_detector'):
            # 初始化 MVP 檢測器
            self._mvp_detector = self._create_mvp_detector()

        return self._mvp_detector.detect_collaborative_task(text)

    def _create_mvp_detector(self):
        """創建 MVP 協作檢測器"""
        class MVPCollaborationDetector:
            def __init__(self):
                # 核心協作關鍵詞
                self.collaboration_keywords = [
                    "and then", "then", "after", "next", "followed by",
                    "and also", "also", "and", "both", "simultaneously",
                    "然後", "接著", "之後", "再", "先",
                    "並且", "同時", "還要", "也要", "一起"
                ]

                # 動作詞
                self.action_words = [
                    "search", "find", "write", "create", "build", "make",
                    "analyze", "download", "save", "send", "read", "process",
                    "搜尋", "查找", "寫", "創建", "建立", "製作",
                    "分析", "下載", "保存", "發送", "讀取", "處理"
                ]

                # 排除詞
                self.exclusion_words = [
                    "only", "just", "simply", "single", "alone",
                    "只", "僅", "單純", "單獨", "獨自"
                ]

            def detect_collaborative_task(self, text: str) -> bool:
                # 排除詞檢查
                text_lower = text.lower()
                for word in self.exclusion_words:
                    if word in text_lower:
                        return False

                # 協作關鍵詞檢查
                found_keywords = []
                for keyword in self.collaboration_keywords:
                    if keyword in text_lower:
                        found_keywords.append(keyword)

                # 動作詞計數
                action_count = sum(1 for word in self.action_words if word in text_lower)

                # 檢測邏輯
                if found_keywords and action_count >= 2:
                    return True

                # 強協作關鍵詞
                strong_keywords = ["and then", "然後", "接著", "and also", "並且", "同時"]
                for keyword in strong_keywords:
                    if keyword in text_lower:
                        return True

                # 多動作詞
                if action_count >= 3:
                    return True

                return False

        return MVPCollaborationDetector()

    async def execute_collaborative_task(self, text: str, mode: CollaborationMode = CollaborationMode.SEQUENTIAL):
        """
        執行協作任務

        Args:
            text: 用戶輸入文本
            mode: 協作模式

        Returns:
            協作執行結果
        """
        pretty_print(f"🤝 Detected collaborative task, analyzing...", color="info")

        # 分解任務
        tasks = self.decompose_collaborative_task(text)

        if not tasks:
            pretty_print("❌ Failed to decompose collaborative task", color="failure")
            return None

        pretty_print(f"📋 Decomposed into {len(tasks)} subtasks", color="status")

        # 根據模式執行任務
        if mode == CollaborationMode.PARALLEL:
            results = await self.collaborative_agent.execute_parallel(tasks)
        elif mode == CollaborationMode.PIPELINE:
            results = await self.collaborative_agent.execute_pipeline(tasks)
        elif mode == CollaborationMode.COMPETITIVE:
            # 競爭模式需要特殊處理
            agent_types = list(set(task.agent_type for task in tasks))
            if len(agent_types) > 1:
                results = [await self.collaborative_agent.execute_competitive(text, agent_types)]
            else:
                results = await self.collaborative_agent.execute_sequential(tasks)
        else:  # SEQUENTIAL
            results = await self.collaborative_agent.execute_sequential(tasks)

        return results

    def decompose_collaborative_task(self, text: str) -> List[AgentTask]:
        """
        分解協作任務為子任務

        Args:
            text: 用戶輸入文本

        Returns:
            List[AgentTask]: 子任務列表
        """
        tasks = []

        # 簡單的任務分解邏輯（可以用 LLM 改進）
        sentences = text.split('.')
        task_id = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # 檢測任務類型
            agent_type = self.detect_task_type(sentence)
            if agent_type:
                task = AgentTask(
                    task_id=f"task_{task_id}",
                    agent_type=agent_type,
                    description=sentence,
                    dependencies=[],
                    priority=1
                )
                tasks.append(task)
                task_id += 1

        return tasks

    def detect_task_type(self, text: str) -> str:
        """
        檢測單個任務的類型

        Args:
            text: 任務描述文本

        Returns:
            str: 代理類型
        """
        text_lower = text.lower()

        # 編程相關關鍵詞
        if any(word in text_lower for word in ["write", "code", "script", "program", "debug", "create app"]):
            return "code"

        # 網頁瀏覽相關關鍵詞
        if any(word in text_lower for word in ["search", "browse", "web", "find online", "look up"]):
            return "web"

        # 文件操作相關關鍵詞
        if any(word in text_lower for word in ["file", "folder", "directory", "save", "organize"]):
            return "files"

        # 默認返回對話類型
        return "talk"

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    agents = [
        CasualAgent("jarvis", "../prompts/base/casual_agent.txt", None),
        BrowserAgent("browser", "../prompts/base/planner_agent.txt", None),
        CoderAgent("coder", "../prompts/base/coder_agent.txt", None),
        FileAgent("file", "../prompts/base/coder_agent.txt", None)
    ]
    router = AgentRouter(agents)
    texts = [
        "hi",
        "你好",
        "Bonjour",
        "Write a python script to check if the device on my network is connected to the internet",
         "Peut tu écrire un script python qui vérifie si l'appareil sur mon réseau est connecté à internet?",
         "写一个Python脚本，检查我网络上的设备是否连接到互联网",
        "Hey could you search the web for the latest news on the tesla stock market ?",
         "嘿，你能搜索网页上关于股票市场的最新新闻吗？",
         "Yo, cherche sur internet comment va tesla en bourse.",
        "I would like you to search for weather api and then make an app using this API",
         "我想让你搜索天气API，然后用这个API做一个应用程序",
         "J'aimerais que tu cherche une api météo et que l'utilise pour faire une application",
        "Plan a 3-day trip to New York, including flights and hotels.",
         "计划一次为期3天的纽约之旅，包括机票和酒店。",
         "Planifie un trip de 3 jours à Paris, y compris les vols et hotels.",
        "Find on the web the latest research papers on AI.",
         "在网上找到最新的人工智能研究论文。",
         "Trouve moi les derniers articles de recherche sur l'IA sur internet",
        "Help me write a C++ program to sort an array",
        "Tell me what France been up to lately",
         "告诉我法国最近在做什么",
         "Dis moi ce que la France a fait récemment",
        "Who is Sergio Pesto ?",
         "谁是Sergio Pesto？",
         "Qui est Sergio Pesto ?",
         "帮我写一个C++程序来排序数组",
         "Aide moi à faire un programme c++ pour trier une array.",
        "What’s the weather like today? Oh, and can you find a good weather app?",
         "今天天气怎么样？哦，你还能找到一个好的天气应用程序吗？",
         "La météo est comment aujourd'hui ? oh et trouve moi une bonne appli météo tant que tu y est.",
        "Can you debug this Java code? It’s not working.",
         "你能调试这段Java代码吗？它不起作用。",
         "Peut tu m'aider à debugger ce code java, ça marche pas",
        "Can you browse the web and find me a 4090 for cheap?",
        "你能浏览网页，为我找一个便宜的4090吗？",
        "Peut tu chercher sur internet et me trouver une 4090 pas cher ?",
        "Hey, can you find the old_project.zip file somewhere on my drive?",
        "嘿，你能在我驱动器上找到old_project.zip文件吗？",
        "Hé trouve moi le old_project.zip, il est quelque part sur mon disque.",
        "Tell me a funny story",
        "给我讲一个有趣的故事",
        "Raconte moi une histoire drole"
    ]
    for text in texts:
        print("Input text:", text)
        agent = router.select_agent(text)
        print()
