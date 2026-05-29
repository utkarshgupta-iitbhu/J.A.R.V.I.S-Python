import customtkinter as ctk
import pyttsx3        
import datetime
import threading
import webbrowser
import requests
import time
import os  
import random
import subprocess
from simpleeval import simple_eval
import wikipedia
import xml.etree.ElementTree as ET


class SpeechEngine:
    def __init__(self):
        self.is_muted = False
        self.voice_gender = "male"

    def speak(self, text, callback_display):
        if callback_display.__name__ != '<lambda>':
            callback_display(f"JARVIS: {text}\n\n")
        
        if not self.is_muted:
            threading.Thread(target=self._run_isolated_speech, args=(text,), daemon=True).start()

    def _run_isolated_speech(self, text):
        try:
            temp_engine = pyttsx3.init()
            temp_engine.setProperty('rate', 175)
            
            voices = temp_engine.getProperty('voices')
            if self.voice_gender == "female" and len(voices) > 1:
                temp_engine.setProperty('voice', voices[1].id)
            else:
                temp_engine.setProperty('voice', voices[0].id)

            temp_engine.say(text)
            temp_engine.runAndWait()
            del temp_engine 
        except Exception as e:
            print(f"Voice Subsystem Exception: {e}")

    def toggle_mute_with_widget(self, button_widget):
        self.is_muted = not self.is_muted
        if button_widget is not None:
            if self.is_muted:
                button_widget.configure(text="🔇 Muted", fg_color="#8B0000", hover_color="#B22222", text_color="#FFE4E1")
            else:
                button_widget.configure(text="🔊 Audio On", fg_color="#1a472a", hover_color="#2d5a3d", text_color="#7FFF00")


class JarvisApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.ai_speech = SpeechEngine()
        self.title("J.A.R.V.I.S - Just A Rather Very Intelligent System")
        self.geometry("800x600")

        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0a0a0a")

        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10, border_width=2, border_color="#3a7ca5")
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="◆ J.A.R.V.I.S MAINFRAME", 
            font=("Segoe UI", 24, "bold"), 
            text_color="#4FC3F7"
        )
        self.title_label.pack(side="left", padx=20, pady=15)

        self.status_label = ctk.CTkLabel(
            self.header_frame, 
            text="● ONLINE", 
            font=("Segoe UI", 11, "bold"), 
            text_color="#7FFF00"
        )
        self.status_label.pack(side="left", padx=(0, 20))

        self.mute_btn = ctk.CTkButton(
            self.header_frame, 
            text="🔊 Audio On", 
            command=self.toggle_mute, 
            fg_color="#1a472a", 
            hover_color="#2d5a3d",
            text_color="#7FFF00",
            font=("Segoe UI", 13, "bold"),
            width=130,
            height=36,
            corner_radius=8
        )
        self.mute_btn.pack(side="right", padx=20, pady=10)

        self.console_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.console_frame.pack(padx=25, pady=10, fill="both", expand=True)

        self.console_label = ctk.CTkLabel(
            self.console_frame, 
            text="SYSTEM CONSOLE", 
            font=("Segoe UI", 11, "bold"), 
            text_color="#78909C",
            anchor="w"
        )
        self.console_label.pack(anchor="w", pady=(0, 5))

        self.console = ctk.CTkTextbox(
            self.console_frame, 
            width=750, 
            height=380, 
            fg_color="#0d1117", 
            text_color="#58D68D", 
            font=("Consolas", 13),
            border_color="#2e4057",
            border_width=2,
            corner_radius=8,
            scrollbar_button_color="#3a7ca5",
            scrollbar_button_hover_color="#5dade2"
        )
        self.console.pack(fill="both", expand=True)
        self.console.configure(state="disabled")

        self.input_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10, border_width=2, border_color="#2e4057")
        self.input_frame.pack(fill="x", padx=25, pady=(5, 15))

        self.prompt_label = ctk.CTkLabel(
            self.input_frame, 
            text="→", 
            font=("Segoe UI", 18, "bold"), 
            text_color="#4FC3F7"
        )
        self.prompt_label.pack(side="left", padx=(20, 10), pady=15)

        self.user_input = ctk.CTkEntry(
            self.input_frame, 
            font=("Segoe UI", 14), 
            fg_color="#0d1117", 
            text_color="#E0E0E0", 
            border_color="#3a7ca5",
            border_width=0,
            placeholder_text="Enter command...", 
            placeholder_text_color="#546E7A",
            corner_radius=6,
            height=40
        )
        self.user_input.pack(side="left", padx=(0, 20), pady=10, expand=True, fill="both")
        self.user_input.bind("<Return>", self.process_command)
        
        self.after(500, lambda: self.ai_speech.speak("System online. How may I assist you, Sir?", self.display_text))

    def display_text(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")

    def toggle_mute(self):
        self.ai_speech.toggle_mute_with_widget(self.mute_btn)

    def fetch_weather(self, city=""):
        try:
            url = f"https://wttr.in/{city}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                temp_c = current['temp_C']
                feels_like = current['FeelsLikeC']
                condition = current['weatherDesc'][0]['value'].lower()
                
                region = data['nearest_area'][0]['region'][0]['value']
                loc_name = region if city else "your location"

                spoken_briefing = f"Sir, {loc_name} is experiencing {condition} at {temp_c}°C, feeling closer to {feels_like}°C."
                self.ai_speech.speak(spoken_briefing, self.display_text)
            else:
                self.ai_speech.speak("Unable to reach weather telemetry.", self.display_text)
        except Exception:
            self.ai_speech.speak("Weather mainframe offline.", self.display_text)

    def start_countdown(self, duration_seconds):
        time.sleep(duration_seconds)
        self.input_frame.configure(border_color="#8B0000")
        self.header_frame.configure(border_color="#8B0000")
        self.ai_speech.speak("Sir, your allocated time block has expired.", self.display_text)
        self.after(4000, lambda: self.input_frame.configure(border_color="#2e4057"))
        self.after(4000, lambda: self.header_frame.configure(border_color="#3a7ca5"))

    def handle_notes(self, cmd, query):
        if cmd.startswith("remember ") or cmd.startswith("note "):
            note_content = query[9:] if cmd.startswith("remember ") else query[5:]
            if note_content.strip():
                try:
                    with open("jarvis_notes.txt", "a", encoding="utf-8") as file:
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
                        file.write(f"[{timestamp}] {note_content}\n")
                    self.ai_speech.speak("Noted data securely.", self.display_text)
                except Exception:
                    self.ai_speech.speak("System file error encountered. Unable to save note.", self.display_text)
            else:
                self.ai_speech.speak("Sir, you did not provide any content to note.", self.display_text)

        elif cmd in ["read notes", "show notes", "display notes", "view notes"]:
            try:
                with open("jarvis_notes.txt", "r", encoding="utf-8") as file:
                    all_notes = file.read().strip()
                if all_notes:
                    self.display_text(f"--- LOGGED JARVIS MEMORIES --- \n{all_notes}\n\n")
                    self.ai_speech.speak("Displaying all logged notes, Sir.", lambda x: None)
                else:
                    self.ai_speech.speak("No notes have been logged yet, Sir.", self.display_text)
            except FileNotFoundError:
                self.ai_speech.speak("No notes have been logged yet, Sir.", self.display_text)

        elif cmd in ["wipe notes", "delete notes", "clear notes"]:
            try:
                if os.path.exists("jarvis_notes.txt"):
                    os.remove("jarvis_notes.txt")
                    self.ai_speech.speak("All logged notes have been cleared, Sir.", self.display_text)
                else:
                    self.ai_speech.speak("No notes to clear, Sir.", self.display_text)
            except Exception:
                self.ai_speech.speak("System file error encountered. Unable to clear notes.", self.display_text)

    def handle_todo(self, cmd, query):
        todo_file = "jarvis_todos.txt"

        if cmd.startswith("todo add ") or cmd.startswith("add todo "):
            task = query.replace("todo add ", "").replace("add todo ", "").strip()
            if task:
                try:
                    with open(todo_file, "a", encoding="utf-8") as file:
                        file.write(f"{task}\n")
                    self.ai_speech.speak(f"Task added to your agenda: {task}", self.display_text)
                except Exception:
                    self.ai_speech.speak("Error writing to the agenda database.", self.display_text)
            else:
                self.ai_speech.speak("Sir, you did not specify a task to add.", self.display_text)

        elif cmd in ["todos", "show todos", "todo list", "read todos", "list todos"]:
            if os.path.exists(todo_file):
                with open(todo_file, "r", encoding="utf-8") as file:
                    tasks = file.readlines()
                
                if tasks:
                    output = "--- TACTICAL TO-DO AGENDA ---\n"
                    for i, task in enumerate(tasks, 1):
                        output += f"[{i}] {task.strip()}\n"
                    output += "-----------------------------\n\n"
                    self.display_text(output)
                    self.ai_speech.speak(f"You have {len(tasks)} pending tasks on your agenda, Sir.", lambda x: None)
                else:
                    self.ai_speech.speak("Your agenda is currently clear, Sir.", self.display_text)
            else:
                self.ai_speech.speak("Your agenda is currently clear, Sir.", self.display_text)

        elif cmd.startswith("todo done ") or cmd.startswith("todo remove ") or cmd.startswith("complete todo "):
            words = cmd.split()
            task_num = None
            
            for word in words:
                if word.isdigit():
                    task_num = int(word)
                    break
            
            if task_num is not None:
                if os.path.exists(todo_file):
                    with open(todo_file, "r", encoding="utf-8") as file:
                        tasks = file.readlines()
                    
                    if 1 <= task_num <= len(tasks):
                        completed_task = tasks.pop(task_num - 1).strip()
                        with open(todo_file, "w", encoding="utf-8") as file:
                            file.writelines(tasks)
                        self.ai_speech.speak(f"Task {task_num} marked as complete: {completed_task}", self.display_text)
                    else:
                        self.ai_speech.speak(f"Sir, task number {task_num} does not exist on your agenda.", self.display_text)
                else:
                    self.ai_speech.speak("Your agenda is already empty, Sir.", self.display_text)
            else:
                self.ai_speech.speak("Please specify the task number to complete, Sir.", self.display_text)

        elif cmd in ["todo clear", "clear todos", "wipe todos"]:
            try:
                if os.path.exists(todo_file):
                    os.remove(todo_file)
                    self.ai_speech.speak("Your entire agenda has been wiped clean, Sir.", self.display_text)
                else:
                    self.ai_speech.speak("Your agenda is already clear, Sir.", self.display_text)
            except Exception:
                self.ai_speech.speak("Failed to wipe the agenda database.", self.display_text)

    def handle_open_app(self, cmd):
        app_name = cmd.replace("open ", "").replace("launch ", "").strip().lower()

        app_paths = {
            "notepad": "start notepad",
            "calculator": "calc",
            "paint": "mspaint",
            "chrome": "start chrome",
            "vs code": "code",
            "code": "code",

            #Open Custom Applications
            "my calculator": r"D:\MY APPS\Calculator.exe",
            "dataset visualizer": r"D:\MY APPS\Dataset_Visualizer.exe",
            "footprint scanner": r"D:\MY APPS\Developer_Footprint_Scanner.exe",
            "hangman": r"D:\MY APPS\Hangman_Game.exe",
            "local drop": r"D:\MY APPS\LocalDrop_Pro.exe",
            "morse code": r"D:\MY APPS\MorseCode.exe",
            "youtube downloader": r"D:\MY APPS\YT_Downloader.exe",
            "yt downloader": r"D:\MY APPS\YT_Downloader.exe",

            "camera": "microsoft.windows.camera:",
            "whatsapp": "whatsapp:",
            "settings": "ms-settings:",

            #Open Directories
            "movies": r"E:\Movies",
            "movies folder": r"E:\Movies",
            "college": r"D:\IIT BHU",
            "college stuff": r"D:\IIT BHU",
            "my apps": r"D:\MY APPS",
            "jee": r"D:\JEE",
            "jee stuff": r"D:\JEE",
            "downloads": r"C:\Users\Public\Downloads"
        }

        if app_name in app_paths:
            try:
                target_path = app_paths[app_name]
                if ":" in target_path or "\\" in target_path:
                    os.startfile(target_path)
                else:
                    subprocess.Popen(target_path, shell=True)
                self.ai_speech.speak(f"Launching {app_name} for you, Sir.", self.display_text)
            except Exception as e:
                print(f"Error launching {app_name}: {e}")
                self.ai_speech.speak(f"Sir, I encountered a system error attempting to open {app_name}.", self.display_text)
        else:
            self.ai_speech.speak(f"Sir, I do not have a mapped application for '{app_name}'.", self.display_text)

    def fetch_news(self, category="global"):
        try:
            base_url = "https://news.google.com/rss/headlines/section/topic/"
            loc = "?gl=IN&hl=en-IN&ceid=IN:en"
            
            category_map = {
                "national": (base_url + "NATION" + loc, "Indian National"),
                "world": (base_url + "WORLD" + loc, "World"),
                "business": (base_url + "BUSINESS" + loc, "Business & Market"),
                "technology": (base_url + "TECHNOLOGY" + loc, "Technology"),
                "entertainment": (base_url + "ENTERTAINMENT" + loc, "Entertainment"),
                "sports": (base_url + "SPORTS" + loc, "Sports"),
                "science": (base_url + "SCIENCE" + loc, "Science"),
                "health": (base_url + "HEALTH" + loc, "Health"),
                "global": ("https://news.google.com/rss" + loc, "Top Global")
            }
            
            url, topic_name = category_map.get(category, category_map["global"])

            response = requests.get(url, timeout=5)
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:5] 
            
            news_text = f"--- LATEST {topic_name.upper()} HEADLINES ---\n"
            for i, item in enumerate(items, 1):
                title = item.find('title').text
                news_text += f"[{i}] {title}\n"
            news_text += "-------------------------------\n\n"
            
            self.display_text(news_text)
            
            if len(items) >= 2:
                speech_payload = (
                    f"I have printed the top {topic_name.lower()} headlines, Sir. "
                    f"Headline 1: {items[0].find('title').text}. "
                    f"Headline 2: {items[1].find('title').text}."
                )
            elif len(items) == 1:
                speech_payload = f"I found one {topic_name.lower()} headline, Sir: {items[0].find('title').text}."
            else:
                speech_payload = f"Sir, I could not find any active {topic_name.lower()} headlines right now."
            
            self.ai_speech.speak(speech_payload, lambda x: None)
                
        except Exception as e:
            print(f"News RSS Error: {e}")
            self.ai_speech.speak("Unable to reach the news network, Sir.", self.display_text)
            
    def process_command(self, event):
        query = self.user_input.get().strip()
        if not query:
            return
        
        self.user_input.delete(0, "end")
        
        if query.lower() not in ["clear", "cls", "clear screen"]:
            self.display_text(f"USER: {query}\n")
            
        cmd = query.lower()

        if cmd in ["clear", "cls", "clear screen"]:
            self.console.configure(state="normal")
            self.console.delete("1.0", "end")
            self.console.configure(state="disabled")
            self.ai_speech.speak("Terminal interface cleared, Sir.", lambda x: None)
            
        elif cmd.strip() in ["exit", "quit", "shutdown"]:
            self.ai_speech.speak("Shutting down system. Goodbye, Sir.", self.display_text)
            self.after(3500, self.destroy)

        elif cmd in ["help", "commands"]:
            help_manifest = (
                "❖ J.A.R.V.I.S. SYSTEM COMMANDS ❖\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🧠 CORE MEMORY & AGENDA\n"
                "  > todo add <task> | todo list | todo done <num> | clear todos\n"
                "  > remember <data> | show notes  | clear notes\n\n"
                "🛠️ DEVELOPMENT & WORKFLOW\n"
                "  > launch <app> (vs code, footprint scanner, dataset visualizer, local drop)\n"
                "  > open <dir> (college, ep notes, movies, downloads)\n\n"
                "🌍 GLOBAL INTELLIGENCE\n"
                "  > news (national, business, tech, science, sports, world)\n"
                "  > weather <city>  | wiki <term> | search <query>\n\n"
                "⚙️ SYSTEM UTILITIES\n"
                "  > time | date | my ip | calculate <math> | timer <num> min\n"
                "  > change voice | clear | exit\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )
            self.display_text(help_manifest)
            self.ai_speech.speak("Accessing help directory. Here is what I can do for you, Sir.", lambda x: None)

        elif "change voice" in cmd or "toggle voice" in cmd:
            if self.ai_speech.voice_gender == "male":
                self.ai_speech.voice_gender = "female"
                self.ai_speech.speak("Voice profile configuration updated. Female vocal modules initialized.", self.display_text)
            else:
                self.ai_speech.voice_gender = "male"
                self.ai_speech.speak("Voice profile configuration restored to default male settings.", self.display_text)
                
        elif cmd in ["hello", "hi", "hey"]:
            self.ai_speech.speak("Hello Sir. I am your personal assistant always ready to serve you. How can I help you today?", self.display_text)

        elif cmd.startswith("google ") or cmd.startswith("search "):
            search_query = query[7:]
            if search_query.strip():
                self.ai_speech.speak(f"Accessing web protocols. Searching global database for {search_query}", self.display_text)
                url = f"https://www.google.com/search?q={search_query}"
                webbrowser.open(url)
            else:
                self.ai_speech.speak("Sir, you did not provide an active search query parameter.", self.display_text)

        elif cmd.startswith("calculate ") or cmd.startswith("math "):
            expression = cmd.replace("calculate ", "").replace("math ", "").strip()
            
            allowed_chars = "0123456789+-*/(). "
            is_safe = all(char in allowed_chars for char in expression)
            
            if is_safe and expression:
                try:
                    result = simple_eval(expression)
                    self.ai_speech.speak(f"The computed solution yields: {result}", self.display_text)
                except ZeroDivisionError:
                    self.ai_speech.speak("Error. Mathematical bounds breached by division by zero.", self.display_text)
                except Exception:
                    self.ai_speech.speak("Calculation aborted. Invalid symbolic math format.", self.display_text)
            else:
                self.ai_speech.speak("Sir, processing that expression could compromise terminal security layers.", self.display_text)

        elif cmd.startswith("weather"):
            city_target = query[7:].strip()
            self.display_text("SYSTEM: Querying satellite telemetry network...\n")
            threading.Thread(target=self.fetch_weather, args=(city_target,), daemon=True).start()

        elif cmd.startswith("timer ") or cmd.startswith("alarm "):
            words = cmd.split()
            duration = None
            
            for word in words:
                if word.isdigit():
                    duration = int(word)
                    break
            
            if duration is not None:
                multiplier = 60  
                unit_label = "minutes"
                
                if "second" in cmd:
                    multiplier = 1
                    unit_label = "seconds"
                elif "hour" in cmd:
                    multiplier = 3600
                    unit_label = "hours"
                
                total_seconds = duration * multiplier
                self.ai_speech.speak(f"Mainframe countdown timer established for {duration} {unit_label}.", self.display_text)
                threading.Thread(target=self.start_countdown, args=(total_seconds,), daemon=True).start()
            else:
                self.ai_speech.speak("Sir, please specify a numerical duration context.", self.display_text)

        elif cmd.startswith("open ") or cmd.startswith("launch "):
            self.handle_open_app(cmd)

        elif any(keyword in cmd for keyword in ["news", "headlines"]):
            cmd_words = cmd.split()
            category = "global" 
            
            if "national" in cmd_words or "india" in cmd_words or "indian" in cmd_words:
                category = "national"
            elif "business" in cmd_words or "finance" in cmd_words or "market" in cmd_words or "markets" in cmd_words:
                category = "business"
            elif "tech" in cmd_words or "technology" in cmd_words:
                category = "technology"
            elif "entertainment" in cmd_words or "bollywood" in cmd_words or "movies" in cmd_words:
                category = "entertainment"
            elif "science" in cmd_words:
                category = "science"
            elif "health" in cmd_words or "medical" in cmd_words:
                category = "health"
            elif "sport" in cmd_words or "sports" in cmd_words:
                category = "sports"
            elif "world" in cmd_words or "international" in cmd_words:
                category = "world"
                
            threading.Thread(target=self.fetch_news, args=(category,), daemon=True).start()

        elif any(keyword in cmd for keyword in ["todo", "todos"]):
            self.handle_todo(cmd, query)

        elif cmd.startswith("wiki ") or cmd.startswith("wikipedia "):
            search_term = query[5:].strip() if cmd.startswith("wiki ") else query[10:].strip()
            try:
                def fetch_wiki(term):
                    try:
                        summary = wikipedia.summary(term, sentences=2)
                        self.ai_speech.speak(f"According to Wikipedia: {summary}", self.display_text)
                    except wikipedia.exceptions.DisambiguationError:
                        self.ai_speech.speak(f"Multiple results found. Please be more specific, Sir.", self.display_text)
                    except wikipedia.exceptions.PageError:
                        self.ai_speech.speak(f"Sorry, no Wikipedia page found for '{term}'.", self.display_text)
                    except Exception:
                        self.ai_speech.speak("Connection to Wikipedia databanks failed.", self.display_text)
                        
                threading.Thread(target=fetch_wiki, args=(search_term,), daemon=True).start()
            except Exception:
                pass

        elif cmd in ["my ip", "what's my ip", "whats my ip"]:
            try:
                response = requests.get('https://api.ipify.org?format=json', timeout=5)
                ip = response.json()['ip']
                self.ai_speech.speak(f"Your public IP address is {ip}", self.display_text)
            except Exception:
                self.ai_speech.speak("Unable to ping external network nodes, Sir.", self.display_text)

        elif cmd in ["tell me a joke", "joke"]:
            try:
                response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    joke = f"{data['setup']} ... {data['punchline']}"
                    self.ai_speech.speak(joke, self.display_text)
                else:
                    self.ai_speech.speak("The humor databank is currently unresponsive, Sir.", self.display_text)
                    
            except Exception as e:
                print(f"Joke API Error: {e}")
                self.ai_speech.speak("The humor subsystem is currently offline, Sir.", self.display_text)

        elif cmd in ["give me a quote", "inspire me", "quote", "motivate me"]:
            try:
                response = requests.get("https://zenquotes.io/api/random", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    quote_text = data[0]['q']
                    quote_author = data[0]['a']
                    self.ai_speech.speak(f"{quote_text} — {quote_author}", self.display_text)
                else:
                    self.ai_speech.speak("The quote databank is currently inaccessible, Sir.", self.display_text)
                    
            except Exception as e:
                print(f"Quote API Error: {e}")
                self.ai_speech.speak("Unable to fetch a quote at this time, Sir.", self.display_text)

        elif cmd in ["roll a die", "roll a dice"]:
            die_result = random.randint(1, 6)
            self.ai_speech.speak(f"Sir, you rolled a {die_result}.", self.display_text)

        elif "random between" in cmd or "random number between" in cmd:
            numbers = [int(s) for s in cmd.split() if s.isdigit()]
            if len(numbers) >= 2:
                low, high = min(numbers[:2]), max(numbers[:2])
                random_num = random.randint(low, high)
                self.ai_speech.speak(f"Sir, your random number between {low} and {high} is {random_num}.", self.display_text)
            else:
                self.ai_speech.speak("Sir, please specify two numerical bounds for the random number generation.", self.display_text)

        elif "time" in cmd:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.ai_speech.speak(f"Sir, the current time is {current_time}", self.display_text)
            
        elif "date" in cmd:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.ai_speech.speak(f"Sir, today is {current_date}", self.display_text)
            
        else:
            self.ai_speech.speak("I'm sorry Sir, I don't recognize that command.", self.display_text)


if __name__ == "__main__":
    app = JarvisApp()
    app.mainloop()
