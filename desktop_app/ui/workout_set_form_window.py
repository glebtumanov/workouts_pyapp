import customtkinter as ctk
from core.models import WorkoutSet
import uuid
from datetime import datetime

class WorkoutSetFormWindow(ctk.CTkToplevel):
    def __init__(self, master, existing_workout_set: WorkoutSet = None, save_callback=None):
        super().__init__(master)
        self.transient(master) # Keep window on top of master
        self.grab_set()      # Modal behavior
        self.protocol("WM_DELETE_WINDOW", self._cancel) # Handle window close button

        self.existing_workout_set = existing_workout_set
        self.save_callback = save_callback

        if self.existing_workout_set:
            self.title("Редактировать комплекс")
        else:
            self.title("Создать новый комплекс")

        self.geometry("500x350")
        self.resizable(False, False)

        # Name
        self.name_label = ctk.CTkLabel(self, text="Название комплекса:")
        self.name_label.pack(pady=(20, 5), padx=20, anchor="w")
        self.name_entry = ctk.CTkEntry(self, width=460)
        self.name_entry.pack(pady=5, padx=20, fill="x")

        # Description
        self.description_label = ctk.CTkLabel(self, text="Описание (опционально):")
        self.description_label.pack(pady=(10, 5), padx=20, anchor="w")
        self.description_textbox = ctk.CTkTextbox(self, height=100, width=460)
        self.description_textbox.pack(pady=5, padx=20, fill="x")

        # Buttons Frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.pack(pady=20, padx=20, fill="x", side="bottom")

        self.save_button = ctk.CTkButton(self.buttons_frame, text="Сохранить", command=self._save)
        self.save_button.pack(side="right", padx=(10, 0))

        self.cancel_button = ctk.CTkButton(self.buttons_frame, text="Отмена", command=self._cancel, fg_color="gray50", hover_color="gray40")
        self.cancel_button.pack(side="right")

        if self.existing_workout_set:
            self.name_entry.insert(0, self.existing_workout_set.name)
            if self.existing_workout_set.description:
                self.description_textbox.insert("1.0", self.existing_workout_set.description)

        self.name_entry.focus()

    def _save(self):
        name = self.name_entry.get().strip()
        description = self.description_textbox.get("1.0", "end-1c").strip() # Get all text except trailing newline

        if not name:
            from tkinter import messagebox
            messagebox.showerror("Ошибка", "Название комплекса не может быть пустым.", parent=self)
            return

        if self.save_callback:
            if self.existing_workout_set:
                # Update existing
                self.existing_workout_set.name = name
                self.existing_workout_set.description = description if description else None
                self.existing_workout_set.updated_at = datetime.now()
                self.save_callback(self.existing_workout_set, is_new=False)
            else:
                # Create new
                new_set = WorkoutSet(
                    name=name,
                    description=description if description else None,
                    # code, created_at, updated_at will be set by default_factory
                )
                self.save_callback(new_set, is_new=True)
        self.destroy()

    def _cancel(self):
        self.destroy()