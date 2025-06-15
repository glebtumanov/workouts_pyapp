import customtkinter as ctk
from ui.screens.main_screen import MainScreen # Импортируем главный экран

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Домашние тренировки")
        self.geometry("800x600")

        # Настройка темы (опционально)
        # ctk.set_appearance_mode("System")  # System, Light, Dark
        # ctk.set_default_color_theme("blue")  # Themes: blue (default), green, dark-blue

        # self.label = ctk.CTkLabel(self, text="Главное окно приложения")
        # self.label.pack(pady=20)

        # Отображаем главный экран
        self.main_screen = MainScreen(master=self)
        self.main_screen.pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()