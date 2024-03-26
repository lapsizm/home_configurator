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

class Wall:
    def init(self, left_out, consists_from_short, num_of_frames, right_out):
        self.left_out = left_out
        self.consists_from_short = consists_from_short
        self.num_of_frames = num_of_frames
        self.right_out = right_out


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
        self.temp_sides = []
        self.free_sides = []

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

        s = f'Узлы: {repetitions_count}\nКороткие соединения: {self.short_soed}\nДлинные соединения: {self.long_soed}\nКол-во блоков: {int(len(self.temp_tochki)/4)}\n'
        s += self.calculate_external_sides()
        self.result_label.config(text=s, font=("Helvetica", 18, "bold"), fg="blue")


    def calculate_free_sides(self):
        self.free_sides = []
        for el in self.temp_sides:
            if self.temp_sides.count(el) == 1:
                self.free_sides.append(el)


    def calculate_external_sides(self):
        d_x = dict()
        d_y = dict()
        for i in range(len(self.free_sides)):
            if self.free_sides[i][0][0] == self.free_sides[i][1][0] and (self.free_sides[i][0][0] not in d_x.keys()):
                d_x[self.free_sides[i][0][0]] = [self.free_sides[i]]
                for j in range(i + 1, len(self.free_sides)):
                    if self.free_sides[j][0][0] == self.free_sides[j][1][0] == self.free_sides[i][0][0]:
                        d_x[self.free_sides[i][0][0]].append(self.free_sides[j])

        for i in range(len(self.free_sides)):
            if self.free_sides[i][0][1] == self.free_sides[i][1][1] and (self.free_sides[i][0][1] not in d_y.keys()):
                d_y[self.free_sides[i][0][1]] = [self.free_sides[i]]
                for j in range(i + 1, len(self.free_sides)):
                    if self.free_sides[j][0][1] == self.free_sides[j][1][1] == self.free_sides[i][0][1]:
                        # TODO: добавить проверку на огромный разрыв и соответствие
                        d_y[self.free_sides[i][0][1]].append(self.free_sides[j])

        sorted_dict = dict()
        for key in d_y.keys():
            sorted_dict[key] = sorted(d_y[key], key=lambda x: x[0][0])

        d_y = sorted_dict

        sorted_dict = dict()
        for key in d_x.keys():
            sorted_dict[key] = sorted(d_x[key], key=lambda x: x[0][1])

        d_x = sorted_dict

        count_side = 0
        for k, v in d_y.items():
            temp = [[], [], [], [], [] , [], [], [], []]
            for i in range(len(v) - 1):
                temp[count_side].append(v[i])
                if v[i][1][0] != v[i + 1][0][0]:
                    count_side += 1
            temp[count_side].append(v[-1])
            temp = list(filter(lambda x: x != [], temp))
            d_y[k] = temp

        count_side = 0
        for k, v in d_x.items():
            temp = [[], [], [], [], [], [], [], [], []]
            for i in range(len(v) - 1):
                temp[count_side].append(v[i])
                if v[i][0][1] != v[i + 1][1][1]:
                    count_side += 1
            temp[count_side].append(v[-1])
            temp = list(filter(lambda x: x != [], temp))
            d_x[k] = temp





        arr_short = [None,0,0,0,0,0,0,0]
        s = f''

        print("with static x")
        for el in d_x.values():
            print(el)
            for el_j in el:
                count = len(el_j)
                arr_short[count] += 1

        arr_long = [None, 0, 0, 0, 0, 0, 0, 0]

        print("with static y")
        for el in d_y.values():
            print(el)
            for el_j in el:
                count = len(el_j)
                arr_long[count] += 1


        # for i in range(1, len(arr_short)):
        #     if arr_short[i] > 0:
        #         s += f'{i} внешних коротких - {arr_short[i]} штук\n'
        #
        # for i in range(1, len(arr_long)):
        #     if arr_long[i] > 0:
        #         s += f'{i} внешних длинных - {arr_long[i]} штук\n'

        min_x = min(self.temp_tochki, key=lambda p: p[0])[0]
        min_y = min(self.temp_tochki, key=lambda p: p[1])[1]

        direction_x = 1
        direction_y = 1

        while d_x or d_y:
            if d_x:
                first_side = d_x[min_x][-1]

                wall = Wall()
                left_p = first_side[0][1] # up
                right_p = first_side[-1][0] #down
                if self.temp_tochki.count(left_p) == 1:
                    if direction_x == -1:
                        wall.right_out = True
                    else:
                        wall.left_out = True
                else:
                    if direction_x == -1:
                        wall.right_out = False
                    else:
                        wall.left_out = False

                if self.temp_tochki.count(right_p) == 1:
                    if direction_x == -1:
                        wall.left_out = True
                    else:
                        wall.right_out = True
                else:
                    if direction_x == -1:
                        wall.left_out = False
                    else:
                        wall.right_out = False

                wall.consists_from_short = True
                wall.num_of_frames = len(first_side)
                s += f'{(wall.left_out, wall.consists_from_short, wall.num_of_frames, wall.right_out)}\n'

                min_y = first_side[-1][0][1]
                temp_x = first_side[-1][0][0]

                if min_y not in d_y:
                    min_y = first_side[0][1][1]
                    temp_x = first_side[0][1][0]

                d_x[min_x].remove(first_side)

                if ((round(temp_x - self.frames[0].width,3), min_y), (temp_x, min_y)) not in self.free_sides:
                    direction_y = 1
                else:
                    direction_y = -1

                if d_x[min_x] is None or len(d_x[min_x]) == 0:
                    del d_x[min_x]


            if d_y:
                second_side = d_y[min_y][0]

                wall = Wall()
                left_p = second_side[0][0] # left
                right_p = second_side[-1][1] #right
                if self.temp_tochki.count(left_p) == 1:
                    if direction_y == -1:
                        wall.right_out = True
                    else:
                        wall.left_out = True
                else:
                    if direction_y == -1:
                        wall.right_out = False
                    else:
                        wall.left_out = False

                if self.temp_tochki.count(right_p) == 1:
                    if direction_y == -1:
                        wall.left_out = True
                    else:
                        wall.right_out = True
                else:
                    if direction_y == -1:
                        wall.left_out = False
                    else:
                        wall.right_out = False
                wall.consists_from_short = False
                wall.num_of_frames = len(second_side)
                s += f'{(wall.left_out, wall.consists_from_short, wall.num_of_frames, wall.right_out)}\n'

                min_x = second_side[-1][1][0]
                temp_y = second_side[-1][1][1]
                if min_x not in d_x:
                    min_x = second_side[0][0][0]
                    temp_y = second_side[0][0][1]
                d_y[min_y].remove(second_side)

                if ((min_x, round(temp_y + self.frames[0].height, 3)), (min_x, temp_y)) not in self.free_sides:
                    direction_x = -1
                else:
                    direction_x = 1

                if d_y[min_y] is None or len(d_y[min_y]) == 0:
                    del d_y[min_y]








        return s





    def init_frame(self):
        initial_frame = ModularFrame(400, 300)
        self.add_frame_to_canvas(initial_frame)

    def canvas_click_handler(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y, 5)[0]
        print(event.x, event.y, clicked_item)
        print("CLICKED", clicked_item)
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
                    if self.short_soed > 0:
                        self.short_soed -= 1
                if self.temp_tochki.count(l_d) > 1 and self.temp_tochki.count(r_d) > 1 or self.temp_tochki.count(l_u) > 1 and self.temp_tochki.count(r_u) > 1:
                    if self.long_soed > 0:
                        self.long_soed -= 1

                self.temp_tochki.remove(l_d)
                self.temp_tochki.remove(l_u)
                self.temp_tochki.remove(r_d)
                self.temp_tochki.remove(r_u)

                self.temp_sides.remove((l_d, l_u))
                self.temp_sides.remove((l_u, r_u))
                self.temp_sides.remove((r_d, r_u))
                self.temp_sides.remove((l_d, r_d))
                self.calculate_free_sides()
                self.calculate_and_display_results()

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
        print(f"Наведено на \n ({frame.x}, {frame.y})")
        #self.result_label.config(text=f"Наведено на \n ({frame.x}, {frame.y})")

    def on_leave_side(self):
        # Очистка метки при уходе курсора с прямоугольника
        #self.result_label.config(text="")
        pass

    def on_click_side(self, event, frame):
        # Вывод информации при нажатии на сторону прямоугольника
        #self.result_label.config(text=f"Нажатие на \n({frame.x}, {frame.y})")
        print(f"Нажатие на \n({frame.x}, {frame.y})")

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

        self.temp_sides.append((l_d, l_u))
        self.temp_sides.append((l_u, r_u))
        self.temp_sides.append((r_d, r_u))
        self.temp_sides.append((l_d, r_d))


        self.calculate_free_sides()
        print("Free sides: ", self.free_sides)
        self.calculate_and_display_results()




    def calculate_elements(self):
        # Расчёт и отображение количества элементов (можно дополнить)
        pass

if __name__ == "__main__":
    app = ModularHomeBuilder()
    app.mainloop()