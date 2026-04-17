#!/usr/bin/env python3
"""
Голосовой ассистент для Arch Linux с локальным ИИ
Распознает голосовые команды, отвечает через ИИ и озвучивает ответы
"""

import speech_recognition as sr
import subprocess
import os
import sys
import json
import urllib.request
import urllib.error

# Попытка импорта pyttsx3 для офлайн TTS
try:
    import pyttsx3
    TTS_ENGINE = "pyttsx3"
except ImportError:
    TTS_ENGINE = None

class VoiceAssistant:
    def __init__(self, use_ai=True, ai_model="llama3.2"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.use_ai = use_ai
        self.ai_model = ai_model
        self.ollama_url = "http://localhost:11434/api/generate"
        
        # Инициализация TTS
        self.tts_engine = None
        if TTS_ENGINE == "pyttsx3":
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.9)
                # Попытка установить русский голос
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if 'ru' in voice.languages or 'russian' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                print(f"TTS движок: pyttsx3 (офлайн)")
            except Exception as e:
                print(f"Ошибка инициализации pyttsx3: {e}")
                self.tts_engine = None
        
        # Команды, которые может выполнять ассистент
        self.commands = {
            "открой браузер": self.open_browser,
            "открой терминал": self.open_terminal,
            "открой файловый менеджер": self.open_file_manager,
            "обновить систему": self.update_system,
            "покажи дату": self.show_date,
            "покажи время": self.show_time,
            "выключи компьютер": self.shutdown,
            "перезагрузи компьютер": self.reboot,
            "сделай скриншот": self.take_screenshot,
            "блокируй экран": self.lock_screen,
            "открой калькулятор": self.open_calculator,
            "открой настройки": self.open_settings,
            "помощь": self.show_help,
            "стоп": self.stop,
            "выход": self.stop,
        }
        
        self.running = True
        
    def speak(self, text):
        """Озвучивает текст через TTS"""
        if not text:
            return
        
        print(f"Ответ: {text}")
        
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"Ошибка TTS: {e}")
        else:
            # Fallback: используем системный tts если доступен
            try:
                subprocess.run(["espeak", "-v", "ru", text], check=False)
            except FileNotFoundError:
                pass  # espeak не установлен
    
    def query_ai(self, user_input):
        """Отправляет запрос к локальной ИИ модели через Ollama"""
        if not self.use_ai:
            return None
        
        prompt = f"""Ты голосовой помощник для Linux. Отвечай кратко и по делу на русском языке.
Пользователь сказал: {user_input}
Если это команда для системы (открыть приложение, показать время и т.д.), ответь что выполняю.
Если это вопрос или беседа - дай полезный краткий ответ."""

        data = {
            "model": self.ai_model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                self.ollama_url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '').strip()
                
        except urllib.error.URLError as e:
            print(f"Ошибка подключения к Ollama: {e}")
            print("Убедитесь, что Ollama запущен: ollama serve")
            return f"Извините, ИИ недоступен. Проверьте, запущен ли Ollama с моделью {self.ai_model}"
        except Exception as e:
            print(f"Ошибка запроса к ИИ: {e}")
            return None
    
    def listen(self):
        """Слушает микрофон и распознает речь"""
        with self.microphone as source:
            print("Настройте уровень шума...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Слушаю...")
            
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=30)
                print("Распознаю речь...")
                
                # Пытаемся распознать речь используя встроенный распознаватель
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                print(f"Вы сказали: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                print("Время ожидания истекло")
                return None
            except sr.UnknownValueError:
                print("Не удалось распознать речь")
                return None
            except sr.RequestError as e:
                print(f"Ошибка сервиса распознавания: {e}")
                return None
    
    def open_browser(self):
        """Открывает браузер по умолчанию"""
        browsers = ["google-chrome", "firefox", "chromium", "brave"]
        for browser in browsers:
            if self.command_exists(browser):
                subprocess.Popen([browser])
                print(f"Открыт {browser}")
                return
        print("Браузер не найден")
    
    def open_terminal(self):
        """Открывает терминал"""
        terminals = ["gnome-terminal", "konsole", "xfce4-terminal", "alacritty", "kitty", "xterm"]
        for terminal in terminals:
            if self.command_exists(terminal):
                subprocess.Popen([terminal])
                print(f"Открыт {terminal}")
                return
        print("Терминал не найден")
    
    def open_file_manager(self):
        """Открывает файловый менеджер"""
        file_managers = ["nautilus", "dolphin", "thunar", "pcmanfm", "nemo"]
        for fm in file_managers:
            if self.command_exists(fm):
                subprocess.Popen([fm])
                print(f"Открыт {fm}")
                return
        print("Файловый менеджер не найден")
    
    def update_system(self):
        """Обновляет систему (требуется подтверждение)"""
        print("Запуск обновления системы...")
        try:
            subprocess.run(["sudo", "pacman", "-Syu"], check=True)
            print("Система обновлена")
        except subprocess.CalledProcessError:
            print("Ошибка при обновлении системы")
        except FileNotFoundError:
            print("pacman не найден (не Arch Linux?)")
    
    def show_date(self):
        """Показывает текущую дату"""
        result = subprocess.run(["date", "+%d.%m.%Y"], capture_output=True, text=True)
        print(f"Дата: {result.stdout.strip()}")
    
    def show_time(self):
        """Показывает текущее время"""
        result = subprocess.run(["date", "+%H:%M:%S"], capture_output=True, text=True)
        print(f"Время: {result.stdout.strip()}")
    
    def shutdown(self):
        """Выключает компьютер"""
        print("Выключение компьютера через 10 секунд...")
        subprocess.run(["shutdown", "-h", "+1"])
    
    def reboot(self):
        """Перезагружает компьютер"""
        print("Перезагрузка компьютера через 10 секунд...")
        subprocess.run(["shutdown", "-r", "+1"])
    
    def take_screenshot(self):
        """Делает скриншот"""
        screenshot_tools = ["gnome-screenshot", "flameshot", "scrot", "maim"]
        for tool in screenshot_tools:
            if self.command_exists(tool):
                filename = f"screenshot_{subprocess.run(['date', '+%Y%m%d_%H%M%S'], capture_output=True, text=True).stdout.strip()}.png"
                subprocess.run([tool, filename])
                print(f"Скриншот сохранен как {filename}")
                return
        print("Инструмент для скриншотов не найден")
    
    def lock_screen(self):
        """Блокирует экран"""
        lock_commands = [
            ["gnome-screensaver-command", "-l"],
            ["dm-tool", "lock"],
            ["xscreensaver-command", "-lock"],
            ["i3lock"],
        ]
        for cmd in lock_commands:
            if self.command_exists(cmd[0]):
                subprocess.run(cmd)
                print("Экран заблокирован")
                return
        print("Инструмент блокировки экрана не найден")
    
    def open_calculator(self):
        """Открывает калькулятор"""
        calculators = ["gnome-calculator", "qalculate-gtk", "kcalc"]
        for calc in calculators:
            if self.command_exists(calc):
                subprocess.Popen([calc])
                print(f"Открыт {calc}")
                return
        print("Калькулятор не найден")
    
    def open_settings(self):
        """Открывает настройки системы"""
        settings_apps = ["gnome-control-center", "systemsettings", "xfce4-settings-manager"]
        for app in settings_apps:
            if self.command_exists(app):
                subprocess.Popen([app])
                print(f"Открыты настройки: {app}")
                return
        print("Приложение настроек не найдено")
    
    def show_help(self):
        """Показывает список доступных команд"""
        print("\n=== Доступные команды ===")
        command_list = list(self.commands.keys())
        for i, cmd in enumerate(command_list, 1):
            print(f"{i}. {cmd}")
        print("========================\n")
    
    def stop(self):
        """Останавливает ассистента"""
        print("До свидания!")
        self.running = False
    
    def command_exists(self, cmd):
        """Проверяет, существует ли команда в системе"""
        return subprocess.run(["which", cmd], capture_output=True).returncode == 0
    
    def execute_command(self, text):
        """Выполняет команду по распознанному тексту с ответом от ИИ"""
        if not text:
            return
        
        # Сначала проверяем специальные команды
        for command_phrase, command_func in self.commands.items():
            if command_phrase in text:
                print(f"\nВыполняю команду: {command_phrase}")
                
                # Для команд остановки не вызываем ИИ
                if command_func in [self.stop]:
                    command_func()
                    return
                
                # Выполняем команду
                command_func()
                
                # Получаем ответ от ИИ и озвучиваем
                if self.use_ai:
                    ai_response = self.query_ai(f"Я выполнил команду: {command_phrase}. Подтверди выполнение кратко.")
                    if ai_response:
                        self.speak(ai_response)
                return
        
        # Если это не команда системы, отправляем запрос к ИИ
        if self.use_ai:
            print("\nЗапрос к ИИ...")
            ai_response = self.query_ai(text)
            if ai_response:
                self.speak(ai_response)
            else:
                self.speak("Извините, я не понял команду и не смог получить ответ от ИИ.")
        else:
            print("Команда не распознана. Скажите 'помощь' для списка команд.")
            self.speak("Команда не распознана")
    
    def run(self):
        """Основной цикл работы ассистента"""
        print("=" * 50)
        print("Голосовой ассистент запущен!")
        if self.use_ai:
            print(f"ИИ включен (модель: {self.ai_model})")
            print("Убедитесь, что Ollama запущен: ollama serve")
        else:
            print("ИИ отключен, только системные команды")
        print("Скажите 'помощь' для списка команд")
        print("Скажите 'стоп' или 'выход' для завершения")
        print("=" * 50)
        
        # Приветственное сообщение от ИИ
        if self.use_ai and self.tts_engine:
            self.speak("Голосовой помощник готов к работе")
        
        while self.running:
            try:
                text = self.listen()
                if text:
                    self.execute_command(text)
            except KeyboardInterrupt:
                print("\nПрервано пользователем")
                break
            except Exception as e:
                print(f"Ошибка: {e}")
        
        print("Ассистент остановлен")


def check_dependencies():
    """Проверяет наличие необходимых зависимостей"""
    missing = []
    
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")
    
    try:
        import pyaudio
    except ImportError:
        missing.append("PyAudio")
    
    try:
        import pyttsx3
    except ImportError:
        print("pyttsx3 не найден - будет использоваться espeak для TTS (опционально)")
    
    if missing:
        print("Отсутствуют необходимые зависимости:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nУстановите их командой:")
        print("  sudo pacman -S python-pip python-pyaudio")
        print("  pip install SpeechRecognition")
        print("\nДля офлайн TTS (рекомендуется):")
        print("  pip install pyttsx3")
        print("  sudo pacman -S espeak-ng")
        return False
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Голосовой ассистент с локальным ИИ")
    parser.add_argument("--no-ai", action="store_true", help="Отключить ИИ, только системные команды")
    parser.add_argument("--model", type=str, default="llama3.2", help="Модель Ollama (по умолчанию: llama3.2)")
    args = parser.parse_args()
    
    if not check_dependencies():
        sys.exit(1)
    
    assistant = VoiceAssistant(use_ai=not args.no_ai, ai_model=args.model)
    assistant.run()
