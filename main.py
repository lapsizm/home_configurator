import tkinter as tk
from tkinter import messagebox
from collections import Counter
from configurator import House




class ModularFrame:
    """Класс для представления модульной рамы."""
    def __init__(self, x, y, width=60.55, height=24.35):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.id = None  # ID элемента на канвасе

class Wall:
    def __init__(self):
        self.left_out = 0
        self.consists_from_short = 0
        self.num_of_frames = 0
        self.right_out = 0
    def init(self, left_out, consists_from_short, num_of_frames, right_out):
        self.left_out = left_out
        self.consists_from_short = consists_from_short
        self.num_of_frames = num_of_frames
        self.right_out = right_out


class ModularHomeBuilder(tk.Tk):
    def __init__(self):
        self.frame_number = 1

        self.nodes_dic = {
            "одиночные соединения": 4,
            "двойные соединения": 0,
            "тройные соединения": 0,
            "четверные соединения": 0
        }

        self.connections_dic = {
            "длинные соединения": 0,
            "короткие соединения": 0
        }

        self.walls_list_list = [((0, 0), [
            (True, True, 1, True),
            (True, False, 1, True),
            (True, True, 1, True),
            (True, False, 1, True),
        ])]

        self.basement_hight = 0

        self.need_down_frames = False

        self.house = House(self.frame_number, self.nodes_dic, self.connections_dic, self.basement_hight,
                      self.need_down_frames)

        self.house.add_wall_list_list(self.walls_list_list)

        super().__init__()
        self.title("Modular Home Builder")
        self.geometry("1200x800")

        self.canvas = tk.Canvas(self, bg='white', width=800, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click_handler)
        self.canvas.bind("<Button-3>", self.canvas_right_click_handler)  # Правый клик для удаления
        self.canvas.bind("<Double-1>", self.canvas_double_click_handler)  # Двойной клик для добавления нового стартового модуля
        self.start_flag = True
        self.frames = []
        self.selected_frame_index = None
        self.temp_tochki = []
        self.temp_sides = []
        self.free_sides = []
        self.ring_sides = []

        self.short_soed = 0
        self.long_soed = 0

        self.width = 60.55
        self.height = 24.35

        self.result_label = tk.Label(self, text="")
        self.result_label.pack(side=tk.TOP, pady=10)

        self.button_download = tk.Button(self, text="Выгрузить спецификацию", command=self.download)
        self.button_download.pack(side=tk.BOTTOM)

        self.button_cokol = tk.Button(self, text="Добавить цоколь", command=self.add_cokol)
        self.button_cokol.pack(side=tk.BOTTOM)

        self.cokol = tk.Entry(self, text="hello")
        self.cokol.pack(side=tk.BOTTOM)

        self.cokol_text =  tk.Label(self, text="")
        self.cokol_text.pack(side=tk.BOTTOM)

        self.var = tk.IntVar()


        self.yes_radio = tk.Radiobutton(self, text="Рамно-свайный фундамент", variable=self.var, value=1, command=self.show_choice)
        self.yes_radio.pack(side = tk.BOTTOM,anchor=tk.W)

        self.no_radio = tk.Radiobutton(self, text="Бетонный фундамент", variable=self.var, value=2, command=self.show_choice)
        self.no_radio.pack(side = tk.BOTTOM,anchor=tk.W)

        self.label_radio = tk.Label(self, text="")
        self.label_radio.pack(side=tk.BOTTOM)

        self.repetition_counts = {}
        self.walls = []
        self.walls_start = 0
        self.ring_walls = []
        self.ring_walls_start = []

        self.height_cok = 0
        self.cokol_text.config(text="Высота цоколя: " + str(self.height_cok), fg="blue")

        self.flag_rams = False
        self.label_radio.config(text="Выбрано: бетонный фундамент", fg="blue")
        self.var.set(2)

        self.flag_ring = False


        # self.calculate_button = tk.Button(self, text="Рассчитать", command=self.calculate_and_display_results,
        #                                   bg="blue", fg="white", relief=tk.GROOVE, font=("Helvetica", 12, "bold"),
        #                                   width=20)
        # self.calculate_button.pack(side=tk.BOTTOM, pady=30, padx=10)

    def download(self):
        if len(self.temp_tochki) == 0:
            self.result_label.config(text="Добавьте хотя бы один \n модуль левой кнопкой мыши!",
                                     font=("Helvetica", 18, "bold"), fg="blue")
        else:
            self.house.create_excel_specification_file()


    def show_choice(self):
        choice = self.var.get()
        if choice == 1:
            self.label_radio.config(text="Выбрано: рамно-свайный фундамент", fg="blue")
            self.flag_rams = True
        elif choice == 2:
            self.label_radio.config(text="Выбрано: бетонный фундамент", fg="blue")
            self.flag_rams = False

        s = self.calculate_and_display_results()
        self.need_down_frames = self.flag_rams

        self.house = House(self.frame_number, self.nodes_dic, self.connections_dic,
                           self.basement_hight, self.need_down_frames)

        self.house.add_wall_list_list(self.walls_list_list)

        self.house.count_specification()
        self.house.count_price_and_weight()

        s += ("Вес дома: " + str(
            self.house.financial_characteristics["Форматированный вес всех комплектов"]) +
              "кг." + "\n")
        s += ("Цена дома: " + str(
            self.house.financial_characteristics["Форматированная розничная цена (с НДС)"]) +
              "р." + "\n")
        s += "Площадь дома: " + str(
            self.house.financial_characteristics["Форматированная площадь дома"]) + " кв. м." + "\n"
        self.result_label.config(text=s, font=("Helvetica", 18, "bold"), fg="blue")


    def add_cokol(self):
        text = "Высота цоколя: "

        try:
            cok = int(self.cokol.get())
            if type(cok) == int:
                if cok >= 0:
                    text += str(cok)
                    self.height_cok = cok
                    s = self.calculate_and_display_results()

                    self.basement_hight = self.height_cok

                    self.house = House(self.frame_number, self.nodes_dic, self.connections_dic,
                                       self.basement_hight, self.need_down_frames)

                    self.house.add_wall_list_list(self.walls_list_list)

                    self.house.count_specification()
                    self.house.count_price_and_weight()

                    s += ("Вес дома: " + str(
                        self.house.financial_characteristics["Форматированный вес всех комплектов"]) +
                          "кг." + "\n")
                    s += ("Цена дома: " + str(
                        self.house.financial_characteristics["Форматированная розничная цена (с НДС)"]) +
                          "р." + "\n")
                    s += "Площадь дома: " + str(
                        self.house.financial_characteristics["Форматированная площадь дома"]) + " кв. м." + "\n"
                    self.result_label.config(text=s, font=("Helvetica", 18, "bold"), fg="blue")
                else:
                    text += "Цоколь должен быть \nбольше или равна 0!"
        except ValueError:
            text += "Цоколь должен быть \nчислом!"

        self.cokol_text.config(text=text, fg="blue")

    def calculate_and_display_results(self):
        # Реализация расчетов и вывода результатов
        counter = Counter(self.temp_tochki)

        self.repetitions_count = {4: 0, 3: 0, 2: 0, 1: 0}
        for k, v in counter.items():
            if v == 2:
                left_s = ((round(k[0] - self.width, 3), k[1]), k)
                right_s = (k, (round(k[0] + self.width, 3), k[1]))
                up_s = (k, (k[0], round(k[1] - self.height, 3)))
                down_s = ((k[0], round(k[1] + self.height, 3)), k)
                if left_s in self.free_sides and right_s in self.free_sides and up_s in self.free_sides and down_s in self.free_sides:
                    self.repetitions_count[1] += 2
                    continue
            self.repetitions_count[v] += 1

        s = f'Узлы: {self.repetitions_count}\nКороткие соединения: {self.short_soed}\nДлинные соединения: {self.long_soed}\nКол-во блоков: {int(len(self.temp_tochki)/4)}\n'
        s += self.calculate_external_sides()
        return s

    def is_vertical(self, side):
        if side[0][0] == side[1][0]:
            return True
        return False
    def is_horizontal(self, side):
        if side[0][1] == side[1][1]:
            return True
        return False

    def there_is_ring(self):
        temp_right_sides = []
        for el in self.free_sides:
            if self.is_vertical(el):
                if self.is_right_side(el):
                    temp_right_sides.append(el)

        self.ring_sides = []
        for el in temp_right_sides:
            temp_lower = el[0]
            temp_upper = el[1]
            const_lower = temp_lower
            const_upper = temp_upper
            my_side = (temp_lower, temp_upper)
            direction_x = 1
            direction_y = 0
            arr_of_sides = []
            start = True
            while True:
                if direction_y != 0 or start:
                    arr_of_sides.append((temp_lower,temp_upper))
                    start = False

                if direction_x == 1:
                    temp_x = round(temp_lower[0] + self.width,3)
                    temp_y = temp_lower[1]
                    if (temp_lower, (temp_x, temp_y)) in self.free_sides:
                        temp_upper = (temp_x, temp_y)
                        direction_y = 1
                    elif ((round(temp_lower[0] - self.width,3), temp_y), temp_lower) in self.free_sides:
                        temp_upper = temp_lower
                        temp_lower = (round(temp_lower[0] - self.width,3), temp_y)
                        direction_y = -1
                    elif ((temp_lower[0], round(temp_lower[1] + self.height,3)), temp_lower) in self.free_sides:
                        temp_upper = temp_lower
                        temp_lower = (temp_lower[0], round(temp_lower[1] + self.height,3))
                        direction_y = 0

                elif direction_x == -1:
                    temp_x = round(temp_upper[0] - self.width,3)
                    temp_y = temp_upper[1]
                    if ((temp_x, temp_y), temp_upper) in self.free_sides:
                        direction_y = -1
                        temp_lower = (temp_x, temp_y)
                    elif (temp_upper, (round(temp_upper[0] + self.width,3), temp_upper[1])) in self.free_sides:
                        direction_y = 1
                        temp_lower = temp_upper
                        temp_upper = (round(temp_upper[0] + self.width,3), temp_upper[1])
                    elif (temp_upper, (temp_upper[0], round(temp_upper[1] - self.height,3))) in self.free_sides:
                        direction_y = 0
                        temp_lower = temp_upper
                        temp_upper = (temp_upper[0], round(temp_upper[1] - self.height,3))

                total_elements = sum(len(sub_array) for sub_array in self.ring_sides)
                if len(arr_of_sides) == len(self.free_sides) - total_elements - 1 or len(arr_of_sides) > len(self.free_sides) // 2:
                    break
                elif temp_lower == const_upper and (direction_x == -1 and direction_y == -1 or direction_x == 0 and direction_y == -1):
                    arr_of_sides.append((temp_lower, temp_upper))
                    #print(arr_of_sides)
                    #self.ring_sides = arr_of_sides
                    self.ring_sides.append(arr_of_sides)
                    break
                elif temp_upper == const_upper or (temp_lower, temp_upper) == (const_lower, const_upper):
                    #print("fuck")
                    break

                if direction_x != 0:
                    arr_of_sides.append((temp_lower,temp_upper))
                if direction_y == 1:
                    temp_x = temp_upper[0]
                    temp_y = round(temp_upper[1] + self.height,3)
                    if (temp_upper, (temp_upper[0],  round(temp_upper[1] - self.height,3))) in self.free_sides:
                        direction_x = -1
                        temp_lower = temp_upper
                        temp_upper = (temp_upper[0],  round(temp_upper[1] - self.height,3))
                    elif ((temp_x, temp_y), temp_upper) in self.free_sides:
                        direction_x = 1
                        temp_lower = (temp_x, temp_y)
                        temp_upper = temp_upper
                    elif (temp_upper, (round(temp_upper[0] + self.width,3),  temp_upper[1])) in self.free_sides:
                        direction_x = 0
                        temp_lower = temp_upper
                        temp_upper = (round(temp_upper[0] + self.width,3),  temp_upper[1])
                elif direction_y == -1:
                    if (temp_lower, (temp_lower[0], round(temp_lower[1] - self.height,3))) in self.free_sides:
                        direction_x = -1
                        temp_lower = temp_lower
                        temp_upper = (temp_lower[0], round(temp_lower[1] - self.height,3))
                    elif ((temp_lower[0], round(temp_lower[1] + self.height,3)), temp_lower) in self.free_sides:
                        direction_x = 1
                        temp_upper = temp_lower
                        temp_lower = (temp_lower[0], round(temp_lower[1] + self.height,3))
                    elif ((round(temp_lower[0] - self.width,3), temp_lower[1]), temp_lower) in self.free_sides:
                        direction_x = 0
                        temp_upper = temp_lower
                        temp_lower = (round(temp_lower[0] - self.width,3), temp_lower[1])

                total_elements = sum(len(sub_array) for sub_array in self.ring_sides)
                if len(arr_of_sides) == len(self.free_sides) - total_elements - 1:
                    break
                elif temp_lower == const_upper and (direction_x == -1 and direction_y == -1 or direction_x == 0 and direction_y == -1):
                    arr_of_sides.append((temp_lower, temp_upper))
                    #print(arr_of_sides)
                    #self.ring_sides = arr_of_sides
                    self.ring_sides.append(arr_of_sides)
                    break
                elif temp_upper == const_upper or (temp_lower, temp_upper) == (const_lower, const_upper):
                    #print("fuck")
                    break


        if len(self.ring_sides) != 0:
            print("THEREISRING: " , self.ring_sides)
            self.flag_ring = True
            return True
        self.flag_ring = False
        return False




    def is_left_side(self, side):
        lower_tochka = side[0]
        upper_tochka = side[1]
        flag_lower = False
        flag_upper = False
        for i in range(0, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == lower_tochka:
                flag_lower = True
                break
        for i in range(1, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == upper_tochka:
                flag_upper = True
                break

        if flag_lower and flag_upper:
            return True
        else:
            return False

    def is_right_side(self, side):
        lower_tochka = side[0]
        upper_tochka = side[1]
        flag_lower = False
        flag_upper = False
        for i in range(3, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == lower_tochka:
                flag_lower = True
                break
        for i in range(2, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == upper_tochka:
                flag_upper = True
                break

        if flag_lower and flag_upper:
            return True
        else:
            return False

    def is_upper_side(self, side):
        left_tochka = side[0]
        right_tochka = side[1]
        flag_left = False
        flag_right = False
        for i in range(1, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == left_tochka:
                flag_left = True
                break
        for i in range(2, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == right_tochka:
                flag_right = True
                break

        if flag_left and flag_right:
            return True
        else:
            return False

    def is_lower_side(self, side):
        left_tochka = side[0]
        right_tochka = side[1]
        flag_left = False
        flag_right = False
        for i in range(0, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == left_tochka:
                flag_left = True
                break
        for i in range(3, len(self.temp_tochki), 4):
            if self.temp_tochki[i] == right_tochka:
                flag_right = True
                break

        if flag_left and flag_right:
            return True
        else:
            return False



    def calculate_free_sides(self):
        self.free_sides = []
        for el in self.temp_sides:
            if self.temp_sides.count(el) == 1:
                self.free_sides.append(el)


    def calculate_rings_sides(self):
        self.ring_walls = []
        self.ring_walls_start = []
        d_x = dict()
        d_y = dict()
        s = f'\n'

        for el in self.ring_sides:
            temp_ring_sides = []
            for i in range(len(el)):
                if el[i][0][0] == el[i][1][0] and (el[i][0][0] not in d_x.keys()):
                    d_x[el[i][0][0]] = [el[i]]
                    for j in range(i + 1, len(el)):
                        if el[j][0][0] == el[j][1][0] == el[i][0][0]:
                            d_x[el[i][0][0]].append(el[j])

            for i in range(len(el)):
                if el[i][0][1] == el[i][1][1] and (el[i][0][1] not in d_y.keys()):
                    d_y[el[i][0][1]] = [el[i]]
                    for j in range(i + 1, len(el)):
                        if el[j][0][1] == el[j][1][1] == el[i][0][1]:
                            # TODO: добавить проверку на огромный разрыв и соответствие
                            d_y[el[i][0][1]].append(el[j])

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
                temp = [[], [], [], [], [], [], [], [], []]
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


            min_x = min(d_x.keys())
            min_y = min(d_y.keys())

            direction_x = 1
            direction_y = 1
            start_flag = True

            while d_x or d_y:
                if d_x:
                    if start_flag:
                        first_side = d_x[min_x][0]
                        start_flag = False
                        #s += str(first_side[0][1]) + "\n"
                        self.ring_walls_start.append(first_side[0][1])
                    elif direction_x == -1:
                        if direction_y == -1:
                            first_side = d_x[min_x][0]
                        else:
                            first_side = d_x[min_x][-1]
                    elif direction_x == 1:
                        if direction_y == -1:
                            first_side = d_x[min_x][0]
                        elif direction_y == 1:
                            first_side = d_x[min_x][-1]

                    wall = Wall()
                    left_p = first_side[0][1]  # up
                    right_p = first_side[-1][0]  # down
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
                    temp_ring_sides.append(wall)
                    s += f'{(wall.left_out, wall.consists_from_short, wall.num_of_frames, wall.right_out)}\n'

                    if direction_x == 1:
                        min_y = first_side[-1][0][1]
                        temp_x = first_side[-1][0][0]
                    elif direction_x == -1:
                        min_y = first_side[0][1][1]
                        temp_x = first_side[0][1][0]

                    if min_y not in d_y:
                        min_y = first_side[0][1][1]
                        temp_x = first_side[0][1][0]

                    d_x[min_x].remove(first_side)

                    if ((round(temp_x - self.width, 3), min_y), (temp_x, min_y)) not in el:
                        direction_y = 1
                    else:
                        direction_y = -1

                    if d_x[min_x] is None or len(d_x[min_x]) == 0:
                        del d_x[min_x]

                if d_y:
                    if direction_y == -1:
                        if direction_x == 1:
                            second_side = d_y[min_y][0]
                        else:
                            second_side = d_y[min_y][-1]
                    else:
                        if direction_x == -1:
                            second_side = d_y[min_y][-1]
                        else:
                            second_side = d_y[min_y][0]

                    wall = Wall()
                    left_p = second_side[0][0]  # left
                    right_p = second_side[-1][1]  # right
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
                    temp_ring_sides.append(wall)

                    if direction_y == 1:
                        min_x = second_side[-1][1][0]
                        temp_y = second_side[-1][1][1]
                    elif direction_y == -1:
                        min_x = second_side[0][0][0]
                        temp_y = second_side[0][0][1]

                    if min_x not in d_x:
                        min_x = second_side[0][0][0]
                        temp_y = second_side[0][0][1]
                    d_y[min_y].remove(second_side)

                    if ((min_x, round(temp_y + self.height, 3)), (min_x, temp_y)) not in el:
                        direction_x = -1
                    else:
                        direction_x = 1

                    if d_y[min_y] is None or len(d_y[min_y]) == 0:
                        del d_y[min_y]
            self.ring_walls.append(temp_ring_sides)
            s += "\n"
        return s

    def calculate_external_sides(self):
        self.walls = []
        self.ring_walls = []

        if len(self.temp_tochki) == 0:
            return ""
        if self.there_is_ring():
            for el in self.ring_sides:
                for temp_el in el:
                    self.free_sides.remove(temp_el)
        else:
            self.ring_sides = []

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

        s = f''

        min_x = min(self.temp_tochki, key=lambda p: p[0])[0]
        min_y = min(self.temp_tochki, key=lambda p: p[1])[1]

        direction_x = 1
        direction_y = 1
        start_flag = True

        while d_x or d_y:
            if d_x:
                if start_flag:
                    first_side = d_x[min_x][0]
                    start_flag = False
                    #s += str(first_side[0][1]) + "\n"
                    self.walls_start = first_side[0][1]
                elif direction_x == -1:
                    if direction_y == -1:
                        first_side = d_x[min_x][0]
                        if first_side[-1][0][1] != temp_y:
                            first_side = d_x[min_x][-1]
                    else:
                        first_side = d_x[min_x][-1]
                        if first_side[-1][0][1] != temp_y:
                            first_side = d_x[min_x][0]
                elif direction_x == 1:
                    if direction_y == -1:
                        first_side = d_x[min_x][0]
                        if first_side[-1][0][1] != temp_y:
                            first_side = d_x[min_x][-1]
                    elif direction_y == 1:
                        first_side = d_x[min_x][-1]
                        if [((min_x, round(temp_y + self.height, 3)), (min_x, temp_y))] in d_x[min_x]:
                            first_side = [((min_x, round(temp_y + self.height, 3)), (min_x, temp_y))]

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
                self.walls.append(wall)

                if direction_x == 1:
                    min_y = first_side[-1][0][1]
                    temp_x = first_side[-1][0][0]
                elif direction_x == -1:
                    min_y = first_side[0][1][1]
                    temp_x = first_side[0][1][0]

                if min_y not in d_y:
                    min_y = first_side[0][1][1]
                    temp_x = first_side[0][1][0]

                d_x[min_x].remove(first_side)

                if ((round(temp_x - self.width,3), min_y), (temp_x, min_y)) not in self.free_sides:
                    direction_y = 1
                else:
                    direction_y = -1

                if d_x[min_x] is None or len(d_x[min_x]) == 0:
                    del d_x[min_x]


            if d_y:
                if direction_y == -1:
                    if direction_x == 1:
                        second_side = d_y[min_y][0]
                    else:

                        second_side = d_y[min_y][-1]
                else:
                    if direction_x == -1:
                        second_side = d_y[min_y][-1]
                    else:
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
                self.walls.append(wall)



                if direction_y == 1:
                    min_x = second_side[-1][1][0]
                    temp_y = second_side[-1][1][1]
                elif direction_y == -1:
                    min_x = second_side[0][0][0]
                    temp_y = second_side[0][0][1]

                if min_x not in d_x:
                    min_x = second_side[0][0][0]
                    temp_y = second_side[0][0][1]
                d_y[min_y].remove(second_side)

                if ((min_x, round(temp_y + self.height, 3)), (min_x, temp_y)) not in self.free_sides:
                    direction_x = -1
                else:
                    direction_x = 1

                if d_y[min_y] is None or len(d_y[min_y]) == 0:
                    del d_y[min_y]

        if len(self.ring_sides) > 0:
            s += self.calculate_rings_sides()
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
        if self.start_flag or len(self.temp_tochki) == 0:
            self.add_starting_frame(event.x, event.y)
            self.start_flag = False

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

    # def is_important(self, my_frame):
    #     temp_frames = self.frames.copy()
    #     temp_frames.pop(self.frames.index(my_frame))
    #     list_frames = []
    #     for index, frame in enumerate(temp_frames):
    #         list_frames.append((round(frame.x, 3), round(frame.y, 3)))
    #
    #     if len(list_frames) == 0:
    #         return False
    #     length_frames = len(list_frames)
    #     already_checked = []
    #     el = list_frames[0]
    #     while True:
    #         flag_found = False
    #         if (el[0] + self.width, el[1]) in list_frames and (el[0] + self.width, el[1]) not in already_checked:
    #             already_checked.append(el)
    #             el = (el[0] + self.width, el[1])
    #             flag_found = True
    #         elif (el[0] - self.width, el[1]) in list_frames and (el[0] - self.width, el[1]) not in already_checked:
    #             already_checked.append(el)
    #             el = (el[0] - self.width, el[1])
    #             flag_found = True
    #         elif (el[0], el[1] + self.height) in list_frames and (el[0], el[1] + self.height) not in already_checked:
    #             already_checked.append(el)
    #             el = (el[0], el[1] + self.height)
    #             flag_found = True
    #         elif (el[0], el[1] - self.height) in list_frames and (el[0], el[1] - self.height) not in already_checked:
    #             already_checked.append(el)
    #             el = (el[0], el[1] - self.height)
    #             flag_found = True
    #
    #         if flag_found == False and len(already_checked) == length_frames - 1:
    #             return False
    #         if flag_found == False and len(already_checked) < length_frames - 1:
    #             return True





    def delete_frame(self, clicked_item):
        for index, frame in enumerate(self.frames):
            if frame.id == clicked_item:

                l_d = (round(frame.x - frame.width / 2, 3), round(frame.y + frame.height / 2, 3))
                l_u = (round(frame.x - frame.width / 2, 3), round(frame.y - frame.height / 2, 3))
                r_u = (round(frame.x + frame.width / 2, 3), round(frame.y - frame.height / 2, 3))
                r_d = (round(frame.x + frame.width / 2, 3), round(frame.y + frame.height / 2, 3))

                # if self.temp_tochki.count(l_d) > 1 and self.temp_tochki.count(l_u) > 1 or self.temp_tochki.count(r_u) > 1 and self.temp_tochki.count(r_d) > 1:
                #     if self.short_soed > 0:
                #         self.short_soed -= 1
                # if self.temp_tochki.count(l_d) > 1 and self.temp_tochki.count(r_d) > 1 or self.temp_tochki.count(l_u) > 1 and self.temp_tochki.count(r_u) > 1:
                #     if self.long_soed > 0:
                #         self.long_soed -= 1

                # if self.is_important(frame):
                #     print("IMPORTANT")
                #     return

                for i in range(0, len(self.temp_sides), 4):
                    if self.temp_sides[i] == (l_d, l_u) and self.temp_sides[i + 1] == (l_u, r_u) and self.temp_sides[i + 2] == (r_d, r_u) and self.temp_sides[i + 3] == (l_d, r_d):
                        self.temp_sides.pop(i)
                        self.temp_sides.pop(i)
                        self.temp_sides.pop(i)
                        self.temp_sides.pop(i)
                        break

                for i in range(0, len(self.temp_tochki), 4):
                    if self.temp_tochki[i] == l_d and self.temp_tochki[i + 1] == l_u and self.temp_tochki[i + 2] == r_u and self.temp_tochki[i + 3] == r_d:
                        self.temp_tochki.pop(i)
                        self.temp_tochki.pop(i)
                        self.temp_tochki.pop(i)
                        self.temp_tochki.pop(i)
                        break

                self.frames.pop(index)
                self.canvas.delete(clicked_item)
                self.selected_frame_index = None
                # Удаляем кнопки направления, если они есть
                self.canvas.delete("direction_button")


                self.calculate_free_sides()

                self.calculate_internal_sides()
                s = self.calculate_and_display_results()
                print(s)

                temp_list_walls = [(self.walls_start,
                                    [(el.left_out, el.consists_from_short, el.num_of_frames, el.right_out) for el in
                                     self.walls])]
                if len(self.ring_walls) != 0:
                    for i in range(len(self.ring_walls)):
                        temp_list_walls.append((self.ring_walls_start[i],
                                                [(el.left_out, el.consists_from_short, el.num_of_frames, el.right_out) for
                                                 el in self.ring_walls[i]]))
                print("LIST OF WALLS: ", temp_list_walls)
                print("LEN: ", len(temp_list_walls))

                self.frame_number = int(len(self.temp_tochki) / 4)

                self.nodes_dic = {
                    "одиночные соединения": self.repetitions_count[1],
                    "двойные соединения": self.repetitions_count[2],
                    "тройные соединения": self.repetitions_count[3],
                    "четверные соединения": self.repetitions_count[4]
                }

                self.connections_dic = {
                    "длинные соединения": self.long_soed,
                    "короткие соединения": self.short_soed
                }

                self.walls_list_list = temp_list_walls

                self.basement_hight = self.height_cok

                self.need_down_frames = self.flag_rams

                self.house = House(self.frame_number, self.nodes_dic, self.connections_dic, self.basement_hight,
                                   self.need_down_frames)

                self.house.add_wall_list_list(self.walls_list_list)

                self.house.count_specification()
                self.house.count_price_and_weight()
                print(self.house.walls_list_list)

                s += "Вес дома: " + str(
                    self.house.financial_characteristics["Форматированный вес всех комплектов"]) + "кг." + "\n"
                s += "Цена дома: " + str(
                    self.house.financial_characteristics["Форматированная розничная цена (с НДС)"]) + "р." + "\n"
                s += "Площадь дома: " + str(
                    self.house.financial_characteristics["Форматированная площадь дома"]) + " кв. м." + "\n"
                self.result_label.config(text=s, font=("Helvetica", 18, "bold"), fg="blue")

                print("TEMP_TOCHKI: ", self.temp_tochki)
                print("TEMP_SIDES: ", self.temp_sides)
                print("TEMP_FRAMES: ", self.frames)

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

    def calculate_internal_sides(self):
        self.short_soed = 0
        self.long_soed = 0
        already = []
        for i in range(0, len(self.temp_tochki), 4):
            l_d = self.temp_tochki[0 + i]
            l_u = self.temp_tochki[1 + i]
            r_u = self.temp_tochki[2 + i]
            r_d = self.temp_tochki[3 + i]
            if self.temp_sides.count((l_d, l_u)) == 2 and ((l_d, l_u) not in already):
                self.short_soed += 1
                already.append((l_d, l_u))
            if self.temp_sides.count((r_d, r_u)) == 2 and ((r_d, r_u) not in already):
                self.short_soed += 1
                already.append((r_d, r_u))
            if self.temp_sides.count((l_d, r_d)) == 2 and ((l_d, r_d) not in already):
                self.long_soed += 1
                already.append((l_d, r_d))
            if self.temp_sides.count((l_u, r_u)) == 2 and ((l_u, r_u) not in already):
                self.long_soed += 1
                already.append((l_u, r_u))

        #print("HELLO", self.short_soed, self.long_soed)


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

        self.temp_tochki.append(l_d)
        self.temp_tochki.append(l_u)
        self.temp_tochki.append(r_u)
        self.temp_tochki.append(r_d)

        self.temp_sides.append((l_d, l_u))
        self.temp_sides.append((l_u, r_u))
        self.temp_sides.append((r_d, r_u))
        self.temp_sides.append((l_d, r_d))

        print("temp.temp_tochki = ", self.temp_tochki)
        print("temp.temp_sides = ", self.temp_sides)

        self.calculate_free_sides()
        print("Free sides: ", self.free_sides)
        self.calculate_internal_sides()
        s = self.calculate_and_display_results()
        print(s)
        #   self.repetitions_count - словарь узлов
        #   self.walls - список стен
        #   self.walls - список в кольце

        #   int(len(self.temp_tochki)/4) -кол-во блоков

        print(self.repetitions_count)
        print(self.walls)
        print(self.ring_walls)
        print(int(len(self.temp_tochki)/4))
        print(self.short_soed)
        print(self.long_soed)
        print(self.height_cok) # высота цоколя
        print(self.flag_rams) # True/false

        temp_list_walls = [(self.walls_start , [(el.left_out, el.consists_from_short, el.num_of_frames, el.right_out) for el in self.walls])]

        if len(self.ring_walls) != 0:
            for i in range(len(self.ring_walls)):
                temp_list_walls.append((self.ring_walls_start[i],
                                        [(el.left_out, el.consists_from_short, el.num_of_frames, el.right_out) for
                                         el in self.ring_walls[i]]))


        print("LIST OF WALLS: ", temp_list_walls)
        print("LEN: ", len(temp_list_walls))

        self.frame_number = int(len(self.temp_tochki)/4)

        self.nodes_dic = {
            "одиночные соединения": self.repetitions_count[1],
            "двойные соединения": self.repetitions_count[2],
            "тройные соединения": self.repetitions_count[3],
            "четверные соединения": self.repetitions_count[4]
        }

        self.connections_dic = {
            "длинные соединения": self.long_soed,
            "короткие соединения": self.short_soed
        }

        self.walls_list_list = temp_list_walls

        self.basement_hight = self.height_cok

        self.need_down_frames = self.flag_rams

        self.house = House(self.frame_number, self.nodes_dic, self.connections_dic, self.basement_hight,
                      self.need_down_frames)

        self.house.add_wall_list_list(self.walls_list_list)

        self.house.count_specification()
        self.house.count_price_and_weight()
        print(self.house.walls_list_list)

        s += "Вес дома: " + str(self.house.financial_characteristics["Форматированный вес всех комплектов"]) + "кг." + "\n"
        s += "Цена дома: " + str(self.house.financial_characteristics["Форматированная розничная цена (с НДС)"]) + "р." + "\n"
        s += "Площадь дома: " + str(
            self.house.financial_characteristics["Форматированная площадь дома"]) + " кв. м." + "\n"
        self.result_label.config(text=s, font=("Helvetica", 18, "bold"), fg="blue")



if __name__ == "__main__":
    app = ModularHomeBuilder()
    app.mainloop()