import tkinter as tk
from tkinter import messagebox
from collections import Counter

class ModularFrame:
    """Класс для представления модульной рамы."""
    def __init__(self, x, y, width=60.55, height=24.35):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = None  # ID элемента на канвасе

class ModularHomeBuilder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modular Home Builder")
        self.geometry("1200x800")

        self.canvas = tk.Canvas(self, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click_handler)
        self.canvas.bind("<Button-3>", self.canvas_right_click_handler)  # Правый клик для удаления
        self.canvas.bind("<Double-1>", self.canvas_double_click_handler)  # Двойной клик для добавления нового стартового модуля

        self.frames = []
        self.selected_frame_index = None
        self.temp_tochki = []
        self.short_soed = 0
        self.long_soed = 0

        self.result_label = tk.Label(self, text="")
        self.result_label.pack(side=tk.TOP, pady=10)

        self.calculate_button = tk.Button(self, text="Рассчитать", command=self.calculate_and_display_results,
                                          bg="blue", fg="white", relief=tk.GROOVE, font=("Helvetica", 12, "bold"),
                                          width=20)
        self.calculate_button.pack(side=tk.BOTTOM, pady=30, padx=10)

    def calculate_and_display_results(self):
        # Реализация расчетов и вывода результатов
        counter = Counter(self.temp_tochki)

        repetitions_count = {4: 0, 3: 0, 2: 0, 1: 0}
        for count in counter.values():
            repetitions_count[count] += 1

        s = f'Узлы: {repetitions_count}\nКороткие соединения: {self.short_soed}\nДлинные соединения: {self.long_soed}\nКол-во блоков: {int(len(self.temp_tochki)/4)}'

        self.result_label.config(text=s, font=("Helvetica", 18, "bold"), fg="blue")


    def init_frame(self):
        initial_frame = ModularFrame(400, 300)
        self.add_frame_to_canvas(initial_frame)

    def canvas_click_handler(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        self.select_frame(clicked_item)

    def canvas_right_click_handler(self, event):
        # Обработчик правого клика для удаления рамы
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        self.delete_frame(clicked_item)

    def canvas_double_click_handler(self, event):
        # Обработчик двойного клика для добавления нового стартового модуля
        self.add_starting_frame(event.x, event.y)

    def add_starting_frame(self, x, y):
        # Добавление нового стартового модуля в указанное место
        new_frame = ModularFrame(x, y)
        self.add_frame_to_canvas(new_frame)

    def show_direction_buttons(self, frame):
        self.canvas.delete("direction_button")
        positions = {
            "↑": (frame.x, frame.y - frame.height / 2 - 20),
            "↓": (frame.x, frame.y + frame.height / 2 + 20),
            "←": (frame.x - frame.width / 2 - 20, frame.y),
            "→": (frame.x + frame.width / 2 + 20, frame.y),
        }
        for direction, (x, y) in positions.items():
            btn = tk.Button(self, text=direction, command=lambda d=direction: self.add_frame(d))
            self.canvas.create_window(x, y, window=btn, anchor=tk.CENTER, tags="direction_button")

    def select_frame(self, clicked_item):
        for index, frame in enumerate(self.frames):
            if frame.id == clicked_item:
                self.selected_frame_index = index
                self.canvas.itemconfig(clicked_item, fill="cyan")
                self.show_direction_buttons(frame)
            else:
                self.canvas.itemconfig(frame.id, fill="lightgray")




    def delete_frame(self, clicked_item):
        for index, frame in enumerate(self.frames):
            if frame.id == clicked_item:
                self.frames.pop(index)
                self.canvas.delete(clicked_item)
                self.selected_frame_index = None
                # Удаляем кнопки направления, если они есть
                self.canvas.delete("direction_button")

                l_d = (round(frame.x - frame.width / 2, 3), round(frame.y + frame.height / 2, 3))
                l_u = (round(frame.x - frame.width / 2, 3), round(frame.y - frame.height / 2, 3))
                r_u = (round(frame.x + frame.width / 2, 3), round(frame.y - frame.height / 2, 3))
                r_d = (round(frame.x + frame.width / 2, 3), round(frame.y + frame.height / 2, 3))

                if self.temp_tochki.count(l_d) > 1 and self.temp_tochki.count(l_u) > 1 or self.temp_tochki.count(r_u) > 1 and self.temp_tochki.count(r_d) > 1:
                    self.short_soed -= 1
                if self.temp_tochki.count(l_d) > 1 and self.temp_tochki.count(r_d) > 1 or self.temp_tochki.count(l_u) > 1 and self.temp_tochki.count(r_u) > 1:
                    self.long_soed -= 1

                self.temp_tochki.remove(l_d)
                self.temp_tochki.remove(l_u)
                self.temp_tochki.remove(r_d)
                self.temp_tochki.remove(r_u)
                break

    def show_direction_buttons(self, frame):
        self.canvas.delete("direction_button")
        # Символы стрелок Unicode
        positions = {
            "↑": (frame.x, frame.y - frame.height / 2 - 20),
            "↓": (frame.x, frame.y + frame.height / 2 + 20),
            "←": (frame.x - frame.width / 2 - 20, frame.y),
            "→": (frame.x + frame.width / 2 + 20, frame.y),
        }
        for direction, (x, y) in positions.items():
            btn = tk.Button(self, text=direction, command=lambda d=direction: self.add_frame(d))
            self.canvas.create_window(x, y, window=btn, anchor=tk.CENTER, tags="direction_button")

    def add_frame(self, direction):
        if self.selected_frame_index is None:
            messagebox.showwarning("Warning", "Please select a frame first!")
            return
        selected_frame = self.frames[self.selected_frame_index]
        x, y = selected_frame.x, selected_frame.y
        if direction == "↑":
            y -= selected_frame.height
        elif direction == "↓":
            y += selected_frame.height
        elif direction == "←":
            x -= selected_frame.width
        elif direction == "→":
            x += selected_frame.width
        if not self.is_overlap(x, y, selected_frame.width, selected_frame.height):
            new_frame = ModularFrame(x, y)
            self.add_frame_to_canvas(new_frame)
        else:
            messagebox.showwarning("Warning", "Cannot add a frame over another frame!")

    def is_overlap(self, x, y, width, height):
        print(self.frames)
        for frame in self.frames:
            if (abs(x - frame.x) * 2 + 1 < (width + frame.width)) and (abs(y - frame.y) * 2 + 1 < (height + frame.height)):
                return True
        return False

    def on_enter_side(self, event, frame):
        # Вывод чего-то на экран при наведении на сторону прямоугольника
        self.result_label.config(text=f"Наведено на \n ({frame.x}, {frame.y})")

    def on_leave_side(self):
        # Очистка метки при уходе курсора с прямоугольника
        self.result_label.config(text="")

    def on_click_side(self, event, frame):
        # Вывод информации при нажатии на сторону прямоугольника
        self.result_label.config(text=f"Нажатие на \n({frame.x}, {frame.y})")

    def add_frame_to_canvas(self, frame):
        frame.id = self.canvas.create_rectangle(
            frame.x - frame.width / 2, frame.y - frame.height / 2,
            frame.x + frame.width / 2, frame.y + frame.height / 2,
            outline="black", fill="lightgray"
        )
        self.frames.append(frame)
        self.select_frame(frame.id)  # Автоматически выбираем добавленный модуль

        self.canvas.tag_bind(frame.id, "<Enter>", lambda event, frame=frame: self.on_enter_side(event, frame))
        self.canvas.tag_bind(frame.id, "<Leave>", lambda event: self.on_leave_side())
        self.canvas.tag_bind(frame.id, "<Button-1>", lambda event, frame=frame: self.on_click_side(event, frame))


        l_d = (round(frame.x - frame.width / 2, 3), round(frame.y + frame.height / 2, 3))
        l_u = (round(frame.x - frame.width / 2, 3), round(frame.y - frame.height / 2, 3))
        r_u = (round(frame.x + frame.width / 2, 3), round(frame.y - frame.height / 2, 3))
        r_d = (round(frame.x + frame.width / 2, 3), round(frame.y + frame.height / 2, 3))

        if l_d in self.temp_tochki and l_u in self.temp_tochki or r_u in self.temp_tochki and r_d in self.temp_tochki:
            self.short_soed += 1
        if l_d in self.temp_tochki and r_d in self.temp_tochki or l_u in self.temp_tochki and r_u in self.temp_tochki:
            self.long_soed += 1

        self.temp_tochki.append(l_d)
        self.temp_tochki.append(l_u)
        self.temp_tochki.append(r_u)
        self.temp_tochki.append(r_d)


        print(self.temp_tochki)



    def calculate_elements(self):
        # Расчёт и отображение количества элементов (можно дополнить)
        pass

if __name__ == "__main__":
    app = ModularHomeBuilder()
    app.mainloop()