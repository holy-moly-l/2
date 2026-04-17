#!/usr/bin/env python3
"""
Голосовой ассистент для Arch Linux
Распознает голосовые команды и выполняет их
"""

import speech_recognition as sr
import subprocess
import os
import sys

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
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
        
    def listen(self):
        """Слушает микрофон и распознает речь"""
        with self.microphone as source:
            print("Настройте уровень шума...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Слушаю...")
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
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
        """Выполняет команду по распознанному тексту"""
        if not text:
            return
        
        # Ищем совпадения в командах
        for command_phrase, command_func in self.commands.items():
            if command_phrase in text:
                print(f"\nВыполняю команду: {command_phrase}")
                command_func()
                return
        
        print("Команда не распознана. Скажите 'помощь' для списка команд.")
    
    def run(self):
        """Основной цикл работы ассистента"""
        print("=" * 50)
        print("Голосовой ассистент запущен!")
        print("Скажите 'помощь' для списка команд")
        print("Скажите 'стоп' или 'выход' для завершения")
        print("=" * 50)
        
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
    
    if missing:
        print("Отсутствуют необходимые зависимости:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nУстановите их командой:")
        print("  sudo pacman -S python-pip python-pyaudio")
        print("  pip install SpeechRecognition")
        return False
    
    return True


if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    assistant = VoiceAssistant()
    assistant.run()
