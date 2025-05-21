import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime, timedelta
import random

class RecommendationSystem:
    """Система рекомендаций (Мост)"""
    def __init__(self, implementation):
        self.impl = implementation
    
    def get_recommendations(self, destination, days):
        return self.impl.generate_recommendations(destination, days)

class BasicRecommendation:
    """Базовая реализация рекомендаций"""
    def generate_recommendations(self, destination, days):
        base_recs = [
            "Обзорная экскурсия по городу (10:00-13:00, €25)",
            "Посещение главного музея (14:00-17:00, €15)",
            "Ужин в традиционном ресторане (19:00-21:00, €40)"
        ]
        return [f"{rec} (День {i+1})" for i in range(days) for rec in base_recs]

class MLRecommendation:
    """Улучшенные рекомендации с ИИ"""
    def generate_recommendations(self, destination, days):
        city_data = {
            "Париж": [
                "Экскурсия в Лувр с гидом (09:00-12:00, €25)",
                "Обед в ресторане Le Procope (13:00-15:00, €50)",
                "Вечерний круиз по Сене (19:30-22:00, €85)",
                "Прогулка по Монмартру (10:00-13:00, бесплатно)",
                "Посещение музея Орсе (14:00-17:00, €14)"
            ],
            "Рим": [
                "Тур по Колизею и Форуму (10:00-13:00, €35)",
                "Дегустация джелато в Giolitti (14:00-15:00, €10)",
                "Экскурсия по Ватикану (16:00-18:00, €45)",
                "Прогулка по Трастевере (19:00-21:00, бесплатно)"
            ]
        }
        
        recommendations = city_data.get(destination, [
            "Пешеходная экскурсия по центру (10:00-13:00, €20)",
            "Посещение местного рынка (14:00-16:00, бесплатно)",
            "Ужин с местной кухней (19:00-21:00, €30-50)"
        ])
        
        # Выбираем случайные рекомендации для каждого дня
        result = []
        for day in range(1, days+1):
            daily_recs = random.sample(recommendations, min(3, len(recommendations)))
            result.extend([f"{rec} (День {day})" for rec in daily_recs])
        
        return result

class RestaurantRecommendation:
    """Рекомендации ресторанов"""
    def get_restaurants(self, destination):
        restaurants = {
            "Париж": [
                {"name": "Le Jules Verne", "type": "Французская", "price": "€120-250", "rating": "4.8"},
                {"name": "Bistrot Paul Bert", "type": "Бистро", "price": "€30-60", "rating": "4.6"},
                {"name": "L'Ambroisie", "type": "Мишлен", "price": "€300+", "rating": "4.9"}
            ],
            "Рим": [
                {"name": "Roscioli", "type": "Итальянская", "price": "€40-80", "rating": "4.7"},
                {"name": "La Pergola", "type": "Мишлен", "price": "€200+", "rating": "4.9"}
            ]
        }
        return restaurants.get(destination, [
            {"name": "Местный ресторан", "type": "Региональная", "price": "€20-50", "rating": "4.0+"}
        ])

class TravelComponent:
    """Базовый компонент (Компоновщик)"""
    def __init__(self, name):
        self.name = name
    
    def display(self, tree, parent=""):
        pass
    
    def get_cost(self):
        return 0
    
    def to_dict(self):
        return {"name": self.name}

class Activity(TravelComponent):
    """Активность"""
    def __init__(self, name, cost=0, time="", notes=""):
        super().__init__(name)
        self.cost = cost
        self.time = time
        self.notes = notes
    
    def display(self, tree, parent=""):
        tree.insert(parent, "end", text=f"⏰ {self.name}", 
                   values=(f"€{self.cost}", f"{self.time} | {self.notes}"))
    
    def get_cost(self):
        return self.cost
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "type": "activity",
            "cost": self.cost,
            "time": self.time,
            "notes": self.notes
        })
        return data

class DayPlan(TravelComponent):
    """План на день"""
    def __init__(self, name, date):
        super().__init__(name)
        self.date = date
        self.activities = []
    
    def add(self, component):
        self.activities.append(component)
    
    def display(self, tree, parent=""):
        day_node = tree.insert(parent, "end", text=f"📅 {self.name} ({self.date})", 
                             values=("", ""), open=True)
        total = 0
        for activity in self.activities:
            activity.display(tree, day_node)
            total += activity.get_cost()
        tree.item(day_node, values=(f"€{total}", ""))
    
    def get_cost(self):
        return sum(activity.get_cost() for activity in self.activities)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "type": "day",
            "date": self.date,
            "activities": [act.to_dict() for act in self.activities]
        })
        return data

class TripPlan(TravelComponent):
    """План поездки"""
    def __init__(self, destination):
        super().__init__(destination)
        self.days = []
        self.hotel = None
        self.flight = None
    
    def add_day(self, day):
        self.days.append(day)
    
    def set_hotel(self, hotel):
        self.hotel = hotel
    
    def set_flight(self, flight):
        self.flight = flight
    
    def display(self, tree):
        tree.delete(*tree.get_children())
        trip_node = tree.insert("", "end", text=f"✈️ Поездка в {self.name}", 
                              values=("", ""), open=True)
        
        if self.flight:
            flight_text = f"{self.flight['airline']} ({self.flight['time']})"
            tree.insert(trip_node, "end", text=f"✈️ Перелет: {flight_text}",
                        values=(f"€{self.flight['price']}", ""))
        
        if self.hotel:
            hotel_text = f"{self.hotel['name']} ★{self.hotel['rating']}"
            tree.insert(trip_node, "end", text=f"🏨 Отель: {hotel_text}",
                        values=(f"€{self.hotel['price']}", self.hotel['address']))
        
        total = (self.flight['price'] if self.flight else 0) + \
               (self.hotel['price'] if self.hotel else 0)
        
        for day in self.days:
            day.display(tree, trip_node)
            total += day.get_cost()
        
        tree.insert(trip_node, "end", text="💰 Итого:", 
                   values=(f"€{total}", ""), tags=("total",))
        tree.tag_configure("total", background="#f0f0f0", font=("Arial", 9, "bold"))
    
    def get_cost(self):
        return sum(day.get_cost() for day in self.days) + \
              (self.flight['price'] if self.flight else 0) + \
              (self.hotel['price'] if self.hotel else 0)
    
    def to_dict(self):
        return {
            "destination": self.name,
            "flight": self.flight,
            "hotel": self.hotel,
            "days": [day.to_dict() for day in self.days],
            "total_cost": self.get_cost()
        }

class TravelPlannerFacade:
    """Фасад для планирования поездки"""
    def __init__(self):
        self.booking_adapter = BookingAdapter()
        self.flight_adapter = FlightAdapter()
        self.recommendation_system = RecommendationSystem(MLRecommendation())
        self.restaurant_recommendation = RestaurantRecommendation()
    
    def plan_trip(self, destination, start_date, days, origin_city="Москва"):
        # Получаем данные от внешних сервисов
        dates = [start_date + timedelta(days=i) for i in range(days)]
        hotels = self.booking_adapter.search_hotels(destination, dates)
        flights = self.flight_adapter.search_flights(origin_city, destination, start_date)
        attractions = self.recommendation_system.get_recommendations(destination, days)
        restaurants = self.restaurant_recommendation.get_restaurants(destination)
        
        # Создаем базовый план
        trip = TripPlan(destination)
        trip.set_flight(flights[0])
        trip.set_hotel(hotels[1])
        
        # Создаем план для каждого дня
        for i in range(days):
            day = DayPlan(f"День {i+1}", dates[i].strftime("%d.%m.%Y"))
            
            # Добавляем активности
            if i*3 < len(attractions):
                act = self._parse_activity(attractions[i*3])
                if act: day.add(act)
            
            # Добавляем обед
            if restaurants and i < len(restaurants):
                rest = restaurants[i]
                day.add(Activity(
                    f"Обед в {rest['name']} ({rest['type']})",
                    self._parse_price(rest['price']),
                    "13:00-15:00",
                    f"Рейтинг: {rest['rating']}"
                ))
            
            # Добавляем ужин
            if i*3+2 < len(attractions):
                act = self._parse_activity(attractions[i*3+2])
                if act: day.add(act)
            
            trip.add_day(day)
        
        return trip
    
    def _parse_activity(self, activity_str):
        """Парсит строку активности в объект Activity"""
        try:
            parts = activity_str.split("(")
            name = parts[0].strip()
            details = parts[1].split(")")[0]
            
            time, *cost_parts = details.split(",")
            time = time.strip()
            cost = 0
            
            if cost_parts:
                cost_str = cost_parts[0].strip()
                if "€" in cost_str:
                    cost = int(cost_str.replace("€", "").strip())
            
            return Activity(name, cost, time)
        except:
            return None
    
    def _parse_price(self, price_str):
        """Парсит строку цены в число"""
        try:
            return int(price_str.replace("€", "").replace("+", "").strip())
        except:
            return 0

class BookingAdapter:
    """Адаптер для Booking.com"""
    def search_hotels(self, destination, dates):
        hotels = [
            {
                "name": "Budget Hotel",
                "price": 50,
                "rating": 3.5,
                "address": "Near city center"
            },
            {
                "name": "Comfort Hotel",
                "price": 120,
                "rating": 4.2,
                "address": "City center"
            },
            {
                "name": "Luxury Resort",
                "price": 300,
                "rating": 4.8,
                "address": "Waterfront"
            }
        ]
        return hotels

class FlightAdapter:
    """Адаптер для поиска авиабилетов"""
    def search_flights(self, origin, destination, date):
        flights = [
            {
                "airline": "AirFrance",
                "price": 250,
                "time": "10:00-12:30",
                "class": "Economy"
            },
            {
                "airline": "Lufthansa",
                "price": 400,
                "time": "15:00-17:45",
                "class": "Premium"
            },
            {
                "airline": "Emirates",
                "price": 800,
                "time": "08:00-10:15",
                "class": "Business"
            }
        ]
        return flights

class TravelPlannerApp(tk.Tk):
    """Графический интерфейс приложения"""
    def __init__(self):
        super().__init__()
        self.title("Умный планировщик путешествий")
        self.geometry("1000x750")
        
        # Инициализация фасада
        self.planner = TravelPlannerFacade()
        self.current_trip = None
        
        # Создание виджетов
        self.create_widgets()
    
    def create_widgets(self):
        # Стиль
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", background="#f5f5f5")
        style.configure("TButton", padding=5)
        
        # Основной контейнер
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Город назначения:").grid(row=0, column=0, sticky=tk.W)
        self.destination_entry = ttk.Entry(control_frame, width=20)
        self.destination_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Дата начала:").grid(row=0, column=2, sticky=tk.W)
        self.start_date_entry = ttk.Entry(control_frame, width=10)
        self.start_date_entry.grid(row=0, column=3, padx=5)
        self.start_date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        ttk.Label(control_frame, text="Дней:").grid(row=0, column=4, sticky=tk.W)
        self.days_spinbox = ttk.Spinbox(control_frame, from_=1, to=30, width=5)
        self.days_spinbox.grid(row=0, column=5, padx=5)
        self.days_spinbox.set(3)
        
        ttk.Button(control_frame, text="Создать план", 
                  command=self.create_plan).grid(row=0, column=6, padx=10)
        
        # Дерево маршрута
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=("cost", "details"), 
                                displaycolumns=("cost", "details"))
        self.tree.heading("#0", text="Маршрут")
        self.tree.heading("cost", text="Стоимость")
        self.tree.heading("details", text="Детали")
        self.tree.column("cost", width=100, anchor=tk.E)
        self.tree.column("details", width=300)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Детали поездки
        details_frame = ttk.LabelFrame(main_frame, text="Детали поездки")
        details_frame.pack(fill=tk.BOTH, pady=(10, 0))
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=10, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопки экспорта
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Сохранить в JSON", 
                  command=self.save_to_json).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Показать детали", 
                  command=self.show_trip_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Советы по поездке", 
                  command=self.show_travel_tips).pack(side=tk.LEFT, padx=5)
    
    def create_plan(self):
        try:
            destination = self.destination_entry.get()
            if not destination:
                messagebox.showerror("Ошибка", "Введите город назначения")
                return
            
            start_date = datetime.strptime(self.start_date_entry.get(), "%d.%m.%Y")
            days = int(self.days_spinbox.get())
            
            # Создаем план через фасад
            self.current_trip = self.planner.plan_trip(destination, start_date, days)
            
            # Отображаем план
            self.display_trip()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные данные: {str(e)}")
    
    def display_trip(self):
        """Отображает план поездки в интерфейсе"""
        if not self.current_trip:
            return
        
        self.tree.delete(*self.tree.get_children())
        self.current_trip.display(self.tree)
        
        # Обновляем детали
        self.update_trip_details()
    
    def update_trip_details(self):
        """Обновляет текстовое описание поездки"""
        if not self.current_trip:
            return
        
        details = f"✈️ Поездка в {self.current_trip.name}\n\n"
        
        if self.current_trip.flight:
            details += f"Перелет: {self.current_trip.flight['airline']} ({self.current_trip.flight['time']})\n"
            details += f"Стоимость: €{self.current_trip.flight['price']}\n\n"
        
        if self.current_trip.hotel:
            details += f"Отель: {self.current_trip.hotel['name']}\n"
            details += f"Рейтинг: ★{self.current_trip.hotel['rating']}\n"
            details += f"Адрес: {self.current_trip.hotel['address']}\n"
            details += f"Стоимость: €{self.current_trip.hotel['price']}\n\n"
        
        details += "Маршрут:\n"
        for day in self.current_trip.days:
            details += f"\n{day.name} ({day.date}):\n"
            for activity in day.activities:
                details += f"- {activity.name} ({activity.time}), стоимость: €{activity.cost}\n"
        
        details += f"\n💰 Общая стоимость поездки: €{self.current_trip.get_cost()}"
        
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)
    
    def save_to_json(self):
        """Сохраняет план поездки в JSON-файл"""
        if not self.current_trip:
            messagebox.showerror("Ошибка", "Сначала создайте план поездки")
            return
        
        trip_data = self.current_trip.to_dict()
        filename = f"trip_to_{trip_data['destination']}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(trip_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", f"План поездки сохранен в файл {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def show_trip_details(self):
        """Показывает детали поездки в отдельном окне"""
        if not self.current_trip:
            messagebox.showerror("Ошибка", "Сначала создайте план поездки")
            return
        
        details = self.details_text.get(1.0, tk.END)
        messagebox.showinfo("Детали поездки", details)
    
    def show_travel_tips(self):
        """Показывает советы для выбранного направления"""
        destination = self.destination_entry.get()
        if not destination:
            messagebox.showerror("Ошибка", "Введите город назначения")
            return
        
        tips = {
            "Париж": [
                "Купите музейную карту Paris Museum Pass для экономии на входных билетах",
                "Используйте метро - самый удобный транспорт в городе",
                "Попробуйте круассаны в местных пекарнях (буланжери)"
            ],
            "Рим": [
                "Бронируйте билеты в Колизей заранее, чтобы избежать очередей",
                "Пейте воду из городских фонтанов - она чистая и бесплатная",
                "Избегайте ресторанов рядом с главными достопримечательностями - они дорогие и неаутентичные"
            ]
        }.get(destination, [
            "Изучите местные обычаи перед поездкой",
            "Скачайте офлайн-карты города",
            "Имейте при себе наличные - не везде принимают карты"
        ])
        
        message = f"Советы для поездки в {destination}:\n\n" + "\n• ".join(tips)
        messagebox.showinfo("Советы по поездке", message)

if __name__ == "__main__":
    app = TravelPlannerApp()
    app.mainloop()