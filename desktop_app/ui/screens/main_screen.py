import customtkinter as ctk
from tkinter import messagebox
from core.models import WorkoutSet
from ui.workout_set_form_window import WorkoutSetFormWindow # Импортируем окно формы
import uuid
from datetime import datetime

class MainScreen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.top_bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.top_bar_frame.grid_columnconfigure(0, weight=1)

        self.screen_title_label = ctk.CTkLabel(self.top_bar_frame, text="Комплексы упражнений", font=ctk.CTkFont(size=24, weight="bold"))
        self.screen_title_label.grid(row=0, column=0, sticky="w")

        self.create_set_button = ctk.CTkButton(self.top_bar_frame, text="⊕ Создать комплекс", command=self._create_new_workout_set)
        self.create_set_button.grid(row=0, column=1, sticky="e")

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.workout_sets: list[WorkoutSet] = []
        self._initialize_mock_data() # Renamed for clarity
        self._load_workout_sets_display() # Renamed for clarity

    def _initialize_mock_data(self):
        # Mock data for demonstration - only if workout_sets is empty
        if not self.workout_sets:
            self.workout_sets = [
                WorkoutSet(name="Комплекс упражнений для рук с гантелями дома",
                           description="Этот комплекс упражнений поможет эффективно проработать бицепс и трицепс с помощью гантелей без посещения спортзала.",
                           code=uuid.uuid4(), created_at=datetime.now(), updated_at=datetime.now()),
                WorkoutSet(name="Комплекс упражнений для плеч с гантелями дома",
                           description="Этот комплекс разработан для полноценной проработки всех отделов дельтовидных мышц (средней, задней и передней дельты) с использованием гантелей в домашних условиях.",
                           code=uuid.uuid4(), created_at=datetime.now(), updated_at=datetime.now()),
                WorkoutSet(name="Комплекс упражнений для прокачки груди с гантелями дома",
                           description="Этот комплекс направлен на развитие грудных мышц с помощью гантелей в домашних условиях.",
                           code=uuid.uuid4(), created_at=datetime.now(), updated_at=datetime.now()),
            ]

    def _load_workout_sets_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.workout_sets:
            no_sets_label = ctk.CTkLabel(self.scrollable_frame, text="Нет доступных комплексов. Нажмите 'Создать комплекс', чтобы добавить новый.", font=ctk.CTkFont(size=16))
            no_sets_label.pack(pady=50)
            return

        for workout_set in self.workout_sets:
            card = self._create_workout_set_card(self.scrollable_frame, workout_set)
            card.pack(pady=10, padx=10, fill="x")

    def _create_workout_set_card(self, master_frame, workout_set: WorkoutSet):
        card_frame = ctk.CTkFrame(master_frame, border_width=1, border_color="gray50")

        name_label = ctk.CTkLabel(card_frame, text=workout_set.name, font=ctk.CTkFont(size=18, weight="bold"), anchor="w")
        name_label.pack(pady=(10, 5), padx=15, fill="x")

        if workout_set.description:
            desc_label = ctk.CTkLabel(card_frame, text=workout_set.description, wraplength=master_frame.winfo_width() - 60, justify="left", anchor="w", font=ctk.CTkFont(size=12))
            desc_label.pack(pady=5, padx=15, fill="x")

        stats_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        stats_frame.pack(pady=5, padx=15, fill="x")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        exercises_label = ctk.CTkLabel(stats_frame, text=f"Упражнений: {len(getattr(workout_set, 'exercises', [])) or 6}", font=ctk.CTkFont(size=12))
        exercises_label.grid(row=0, column=0, sticky="w")

        last_trained_label = ctk.CTkLabel(stats_frame, text="Когда тренировались: 3 дн. назад", font=ctk.CTkFont(size=12))
        last_trained_label.grid(row=0, column=1, sticky="e")

        buttons_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        buttons_frame.pack(pady=(10, 10), padx=15, fill="x")

        start_button = ctk.CTkButton(buttons_frame, text="Начать тренировку",
                                     command=lambda ws_code=workout_set.code: self._start_training(ws_code),
                                     fg_color="#28a745", hover_color="#218838")
        start_button.pack(side="left", padx=(0,5), expand=True, fill="x")

        edit_button = ctk.CTkButton(buttons_frame, text="✏️", width=40,
                                    command=lambda ws_code=workout_set.code: self._edit_workout_set(ws_code),
                                    fg_color="#007bff", hover_color="#0069d9")
        edit_button.pack(side="left", padx=5)

        delete_button = ctk.CTkButton(buttons_frame, text="🗑️", width=40,
                                      command=lambda ws_code=workout_set.code: self._delete_workout_set(ws_code),
                                      fg_color="#dc3545", hover_color="#c82333")
        delete_button.pack(side="left", padx=(5,0))

        return card_frame

    def _handle_save_workout_set(self, workout_set_data: WorkoutSet, is_new: bool):
        if is_new:
            self.workout_sets.append(workout_set_data)
            print(f"New workout set added: {workout_set_data.name}")
        else:
            # The workout_set_data is the already updated instance from the form
            # We just need to ensure our list has this updated instance if it wasn't directly modified
            # (In this case, it was directly modified if it came from self.workout_sets)
            # So, a refresh of the display is the main thing needed.
            print(f"Workout set updated: {workout_set_data.name}")

        self._load_workout_sets_display() # Refresh the entire display

    def _create_new_workout_set(self):
        print(f"Action: Create new workout set button pressed")
        form_window = WorkoutSetFormWindow(master=self.winfo_toplevel(), save_callback=self._handle_save_workout_set)
        # The form_window will call _handle_save_workout_set upon saving

    def _start_training(self, workout_set_code: uuid.UUID):
        print(f"Action: Start training for {workout_set_code}")
        messagebox.showinfo("Начать тренировку", f"Запуск тренировки для комплекса {workout_set_code} (не реализовано).")

    def _edit_workout_set(self, workout_set_code: uuid.UUID):
        print(f"Action: Edit workout set {workout_set_code}")
        workout_to_edit = next((ws for ws in self.workout_sets if ws.code == workout_set_code), None)
        if workout_to_edit:
            form_window = WorkoutSetFormWindow(master=self.winfo_toplevel(),
                                               existing_workout_set=workout_to_edit,
                                               save_callback=self._handle_save_workout_set)
        else:
            messagebox.showerror("Ошибка", f"Комплекс с кодом {workout_set_code} не найден.")

    def _delete_workout_set(self, workout_set_code: uuid.UUID):
        print(f"Action: Delete workout set {workout_set_code}")
        workout_to_delete = next((ws for ws in self.workout_sets if ws.code == workout_set_code), None)
        if not workout_to_delete:
             messagebox.showerror("Ошибка", f"Комплекс с кодом {workout_set_code} не найден для удаления.")
             return

        confirmed = messagebox.askyesno("Удалить комплекс", f"Вы уверены, что хотите удалить комплекс \"{workout_to_delete.name}\"? Это действие необратимо.", parent=self.winfo_toplevel())
        if confirmed:
            self.workout_sets = [ws for ws in self.workout_sets if ws.code != workout_set_code]
            self._load_workout_sets_display()
            messagebox.showinfo("Удалено", f"Комплекс \"{workout_to_delete.name}\" удален.")
        else:
            print(f"Deletion cancelled for {workout_set_code}")

if __name__ == '__main__':
    class TestApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Test Main Screen")
            self.geometry("900x700")
            main_screen = MainScreen(self)
            main_screen.pack(fill="both", expand=True)
    app = TestApp()
    app.mainloop()