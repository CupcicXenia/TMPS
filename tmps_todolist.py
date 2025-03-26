from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox, simpledialog
import copy

# 1. Singleton — AppSettings
class AppSettings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppSettings, cls).__new__(cls)
            cls._instance.save_path = "./tasks"
        return cls._instance

    def set_save_path(self, path):
        self.save_path = path

    def get_save_path(self):
        return self.save_path


# 2. Factory Method — TaskFactory
class Task(ABC):
    @abstractmethod
    def display(self):
        pass

class SimpleTask(Task):
    def __init__(self, description):
        self.description = description

    def display(self):
        return f"Simple Task: {self.description}"

class UrgentTask(Task):
    def __init__(self, description):
        self.description = description

    def display(self):
        return f"Urgent Task: {self.description}"

class RecurringTask(Task):
    def __init__(self, description):
        self.description = description

    def display(self):
        return f"Recurring Task: {self.description}"

class TaskFactory:
    def create_task(self, task_type, description):
        if task_type == "simple":
            return SimpleTask(description)
        elif task_type == "urgent":
            return UrgentTask(description)
        elif task_type == "recurring":
            return RecurringTask(description)
        else:
            raise ValueError("Unknown task type")


# 3. Abstract Factory — ProjectFactory
class ProjectTask(ABC):
    @abstractmethod
    def display(self):
        pass

class WorkTask(ProjectTask):
    def __init__(self, description):
        self.description = description

    def display(self):
        return f"Work Task: {self.description}"

class HomeTask(ProjectTask):
    def __init__(self, description):
        self.description = description

    def display(self):
        return f"Home Task: {self.description}"

class HobbyTask(ProjectTask):
    def __init__(self, description):
        self.description = description

    def display(self):
        return f"Hobby Task: {self.description}"

class ProjectFactory:
    def create_task(self, project_type, description):
        if project_type == "work":
            return WorkTask(description)
        elif project_type == "home":
            return HomeTask(description)
        elif project_type == "hobby":
            return HobbyTask(description)
        else:
            raise ValueError("Unknown project type")


# 4. Builder — TaskBuilder
class TaskBuilder:
    def __init__(self):
        self.task = {}

    def set_description(self, description):
        self.task['description'] = description
        return self

    def set_deadline(self, deadline):
        self.task['deadline'] = deadline
        return self

    def set_tags(self, tags):
        self.task['tags'] = tags
        return self

    def build(self):
        return self.task


# 5. Prototype — TaskPrototype
class TaskPrototype:
    def __init__(self, task):
        self.task = task

    def clone(self):
        return copy.deepcopy(self.task)


# Графический интерфейс
class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager")
        self.root.geometry("500x400")

        # Singleton
        self.settings = AppSettings()

        # GUI Elements
        self.label = tk.Label(root, text="To-Do List Manager")
        self.label.pack(pady=10)

        self.task_listbox = tk.Listbox(root)
        self.task_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки
        self.add_button = tk.Button(root, text="Add Task", command=self.add_task)
        self.add_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.clone_button = tk.Button(root, text="Clone Task", command=self.clone_task)
        self.clone_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.view_button = tk.Button(root, text="View Task", command=self.view_task)
        self.view_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.delete_button = tk.Button(root, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.tasks = []

    def add_task(self):
        description = simpledialog.askstring("Add Task", "Enter task description:")
        if description:
            task_type = simpledialog.askstring("Add Task", "Enter task type (simple/urgent/recurring):")
            project_type = simpledialog.askstring("Add Task", "Enter project type (work/home/hobby):")

            # Factory Method
            task_factory = TaskFactory()
            task = task_factory.create_task(task_type, description)

            # Abstract Factory
            project_factory = ProjectFactory()
            project_task = project_factory.create_task(project_type, description)

            # Builder
            task_builder = TaskBuilder()
            task_data = task_builder.set_description(description).build()

            self.tasks.append((task, project_task, task_data))
            self.task_listbox.insert(tk.END, description)

    def clone_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            selected_task = self.tasks[selected_index[0]]
            cloned_task = TaskPrototype(selected_task).clone()
            self.tasks.append(cloned_task)
            self.task_listbox.insert(tk.END, cloned_task[0].display())

    def view_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            selected_task = self.tasks[selected_index[0]]
            task_info = (
                f"Task: {selected_task[0].display()}\n"
                f"Project: {selected_task[1].display()}\n"
                f"Details: {selected_task[2]}"
            )
            messagebox.showinfo("Task Details", task_info)

    def delete_task(self):
        selected_index = self.task_listbox.curselection()
        if selected_index:
            self.task_listbox.delete(selected_index)
            self.tasks.pop(selected_index[0])


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()