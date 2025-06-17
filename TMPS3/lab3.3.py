import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

# Паттерн Mediator: Центральный контроллер для координации устройств
class SmartHomeMediator:
    def __init__(self):
        self.devices = {}
        self.observers = []
        self.command_history = []  # История для отмены команд

    def register_device(self, device_name, device):
        self.devices[device_name] = device

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def execute_command(self, command):
        command.execute()
        self.command_history.append(command)  # Сохраняем команду в историю
        self.notify_observers(f"Команда выполнена: {command.__class__.__name__}")

    def undo_last_command(self):
        if self.command_history:
            command = self.command_history.pop()  # Удаляем последнюю команду
            command.undo()
            self.notify_observers(f"Команда отменена: {command.__class__.__name__}")
        else:
            self.notify_observers("Нет команд для отмены")

# Паттерн Observer: Интерфейс для наблюдения за изменениями
class Observer:
    def update(self, message):
        pass

# Паттерн Command: Абстрактный класс команды
class Command:
    def execute(self):
        pass

    def undo(self):
        pass

# Конкретные команды для устройств
class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light

    def execute(self):
        self.light.turn_on()

    def undo(self):
        self.light.turn_off()

class LightOffCommand(Command):
    def __init__(self, light):
        self.light = light

    def execute(self):
        self.light.turn_off()

    def undo(self):
        self.light.turn_on()

class MusicPlayCommand(Command):
    def __init__(self, music_player):
        self.music_player = music_player

    def execute(self):
        self.music_player.play()

    def undo(self):
        self.music_player.pause()

class MusicPauseCommand(Command):
    def __init__(self, music_player):
        self.music_player = music_player

    def execute(self):
        self.music_player.pause()

    def undo(self):
        self.music_player.play()

# Паттерн Strategy: Стратегии управления температурой
class TemperatureStrategy:
    def adjust_temperature(self, current_temp):
        pass

class EcoTemperatureStrategy(TemperatureStrategy):
    def adjust_temperature(self, current_temp):
        return max(18, current_temp - 1)  # Экономичный режим: минимальная температура 18°C

class ComfortTemperatureStrategy(TemperatureStrategy):
    def adjust_temperature(self, current_temp):
        return 22  # Комфортный режим: всегда 22°C

class NightTemperatureStrategy(TemperatureStrategy):
    def adjust_temperature(self, current_temp):
        return 16  # Ночной режим: температура 16°C для экономии энергии

# Паттерн State: Состояния охранной системы
class SecurityState:
    def handle(self, security_system):
        pass

class ArmedState(SecurityState):
    def handle(self, security_system):
        return "Охранная система включена"

class DisarmedState(SecurityState):
    def handle(self, security_system):
        return "Охранная система выключена"

# Устройства умного дома
class Light:
    def __init__(self, name):
        self.name = name
        self.is_on = False

    def turn_on(self):
        self.is_on = True
        return f"{self.name} включен"

    def turn_off(self):
        self.is_on = False
        return f"{self.name} выключен"

class Thermostat:
    def __init__(self, name):
        self.name = name
        self.temperature = 20
        self.strategy = EcoTemperatureStrategy()

    def set_strategy(self, strategy):
        self.strategy = strategy

    def adjust_temperature(self):
        self.temperature = self.strategy.adjust_temperature(self.temperature)
        return f"{self.name}: Температура установлена на {self.temperature}°C"

class SecuritySystem:
    def __init__(self, name):
        self.name = name
        self.state = DisarmedState()

    def change_state(self, state):
        self.state = state
        return self.state.handle(self)

class MusicPlayer:
    def __init__(self, name):
        self.name = name
        self.is_playing = False

    def play(self):
        self.is_playing = True
        return f"{self.name} воспроизводит музыку"

    def pause(self):
        self.is_playing = False
        return f"{self.name} на паузе"

# Графический интерфейс (PyQt5) и реализация Observer
class SmartHomeUI(QMainWindow, Observer):
    def __init__(self, mediator):
        super().__init__()
        self.mediator = mediator
        self.mediator.add_observer(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Система умного дома")
        self.setGeometry(100, 100, 400, 600)

        # Создаем центральный виджет и компоновку
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Метка для отображения статуса
        self.status_label = QLabel("Статус: Ожидание команд")
        layout.addWidget(self.status_label)

        # Кнопка для отмены последней команды
        undo_btn = QPushButton("Отменить последнюю команду")
        undo_btn.clicked.connect(self.mediator.undo_last_command)
        layout.addWidget(undo_btn)

        # Кнопки для управления светом
        light_on_btn = QPushButton("Включить свет")
        light_off_btn = QPushButton("Выключить свет")
        light_on_btn.clicked.connect(lambda: self.mediator.execute_command(LightOnCommand(self.mediator.devices["light"])))
        light_off_btn.clicked.connect(lambda: self.mediator.execute_command(LightOffCommand(self.mediator.devices["light"])))
        layout.addWidget(light_on_btn)
        layout.addWidget(light_off_btn)

        # Кнопки для управления термостатом
        eco_btn = QPushButton("Экономичный режим термостата")
        comfort_btn = QPushButton("Комфортный режим термостата")
        night_btn = QPushButton("Ночной режим термостата")
        eco_btn.clicked.connect(lambda: self.mediator.devices["thermostat"].set_strategy(EcoTemperatureStrategy()) or self.mediator.notify_observers(self.mediator.devices["thermostat"].adjust_temperature()))
        comfort_btn.clicked.connect(lambda: self.mediator.devices["thermostat"].set_strategy(ComfortTemperatureStrategy()) or self.mediator.notify_observers(self.mediator.devices["thermostat"].adjust_temperature()))
        night_btn.clicked.connect(lambda: self.mediator.devices["thermostat"].set_strategy(NightTemperatureStrategy()) or self.mediator.notify_observers(self.mediator.devices["thermostat"].adjust_temperature()))
        layout.addWidget(eco_btn)
        layout.addWidget(comfort_btn)
        layout.addWidget(night_btn)

        # Кнопки для управления охранной системой
        arm_btn = QPushButton("Включить охрану")
        disarm_btn = QPushButton("Выключить охрану")
        arm_btn.clicked.connect(lambda: self.mediator.notify_observers(self.mediator.devices["security"].change_state(ArmedState())))
        disarm_btn.clicked.connect(lambda: self.mediator.notify_observers(self.mediator.devices["security"].change_state(DisarmedState())))
        layout.addWidget(arm_btn)
        layout.addWidget(disarm_btn)

        # Кнопки для управления музыкой
        play_btn = QPushButton("Включить музыку")
        pause_btn = QPushButton("Пауза музыки")
        play_btn.clicked.connect(lambda: self.mediator.execute_command(MusicPlayCommand(self.mediator.devices["music"])))
        pause_btn.clicked.connect(lambda: self.mediator.execute_command(MusicPauseCommand(self.mediator.devices["music"])))
        layout.addWidget(play_btn)
        layout.addWidget(pause_btn)

    def update(self, message):
        self.status_label.setText(f"Статус: {message}")

# Основная функция для запуска приложения
def main():
    app = QApplication(sys.argv)
    
    # Создаем устройства
    light = Light("Свет в гостиной")
    thermostat = Thermostat("Термостат")
    security = SecuritySystem("Охранная система")
    music_player = MusicPlayer("Музыкальный плеер")

    # Создаем медиатор и регистрируем устройства
    mediator = SmartHomeMediator()
    mediator.register_device("light", light)
    mediator.register_device("thermostat", thermostat)
    mediator.register_device("security", security)
    mediator.register_device("music", music_player)

    # Создаем и показываем интерфейс
    ui = SmartHomeUI(mediator)
    ui.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()