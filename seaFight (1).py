import pygame as pg
import random
import copy


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_BLUE = (0, 153, 153)
LIGHT_GRAY = (192, 192, 192)
RED = (255, 0, 0)

block_size = 30
left_margin = 5 * block_size
upper_margin = 2 * block_size

size = (left_margin + 30 * block_size, upper_margin + 20 * block_size)

LETTERS = "АБВГДЕЖЗИК"

pg.init()

screen = pg.display.set_mode(size)
pg.display.set_caption("МОРСКОЙ БОЙ")

font_size = int(block_size / 1.5)
font = pg.font.SysFont('Gabriola', font_size)
game_over_font_size = 3 * block_size
game_over_font = pg.font.SysFont('Gabriola', game_over_font_size)

# КОМПЬЮТЕРНЫЕ ДАННЫЕ
computer_available_to_fire_set = {(x, y) for x in range(16, 26) for y in range(1, 11)}
around_last_computer_hit_set = set()
dotted_set_for_computer_not_to_shoot = set()
hit_blocks_for_computer_not_to_shoot = set()
last_hits_list = []
###################

hit_blocks = set()
dotted_set = set()
destroyed_computer_ships = []


class Grid:
    """
    Класс для рисования сеток и добавления к ним заголовков, цифр и букв
    ----------
    Атрибуты:
        title (str): имя игрока, которое будет отображаться в верхней части его сетки.
        offset (int): Где начинается сетка (в количестве блоков)
                (обычно 0 для компьютера и 15 для человека)
    ----------
    Методы:
        __draw_grid(): Рисует две сетки для обоих игроков
    __add_nums_letters_to_grid(): Рисует числа 1-10 по вертикали и добавляет буквы ниже по горизонтали
    линии для обеих сеток
    __sign_grid(): Помещает имена игроков (названия) в центр над сетками
    """

    def __init__(self, title, offset):
        """
        title (str): имя игрока, которое будет отображаться в верхней части его сетки.
        offset (int): Где начинается сетка (в количестве блоков)
        (0 для компьютера и 15 для человека)
        """
        self.title = title
        self.offset = offset
        self.__draw_grid()
        self.__add_nums_letters_to_grid()
        self.__sign_grid()

    def __draw_grid(self):
        """
        Рисует две сетки для обоих игроков
        """
        for i in range(11):
            # Горизонтальные линии
            pg.draw.line(screen, BLACK, (left_margin + self.offset * block_size, upper_margin + i * block_size),
                             (left_margin + (10 + self.offset) * block_size, upper_margin + i * block_size), 1)
            # Вертикальные линии
            pg.draw.line(screen, BLACK, (left_margin + (i + self.offset) * block_size, upper_margin),
                             (left_margin + (i + self.offset) * block_size, upper_margin + 10 * block_size), 1)

    def __add_nums_letters_to_grid(self):
        """
        Рисует цифры 1-10 по вертикали и добавляет буквы ниже по горизонтали
        линии для обеих сеток
        """
        for i in range(10):
            num_ver = font.render(str(i + 1), True, BLACK)
            letters_hor = font.render(LETTERS[i], True, BLACK)
            num_ver_width = num_ver.get_width()
            num_ver_height = num_ver.get_height()
            letters_hor_width = letters_hor.get_width()

            # Числа (по вертикали)
            screen.blit(num_ver, (left_margin - (block_size // 2 + num_ver_width // 2) + self.offset * block_size,
                                  upper_margin + i * block_size + (block_size // 2 - num_ver_height // 2)))
            # Буквы (горизонтальные)
            screen.blit(letters_hor, (left_margin + i * block_size + (block_size // 2 - letters_hor_width // 2) +
                                      self.offset * block_size, upper_margin + 10 * block_size))

    def __sign_grid(self):
        """
        Помещает имена (titles) игроков в центр над сетками
        """
        player = font.render(self.title, True, BLACK)
        sign_width = player.get_width()
        screen.blit(player, (left_margin + 5 * block_size - sign_width // 2 +
                             self.offset * block_size, upper_margin - block_size // 2 - font_size))


class Button:
    """
    Создает кнопки и печатает пояснительное сообщение для них
    ----------
    Атрибуты:
        __title (str): Название кнопки (title)
        __message (str): пояснительное сообщение для печати на экране
        __x_start (int): горизонтальное смещение, с чего начать рисование кнопки
        __y_start (int): смещение по вертикали, с чего начать рисование кнопки
        rect_for_draw (tuple of four ints): прямоугольник кнопки, который нужно нарисовать
        rect (pg Rect): pg Rect object
        __rect_for_button_title (tuple of two ints): прямоугольник для печати текста в прямоугольнике
        __color (tuple): цвет кнопки (по умолчанию ЧЕРНЫЙ, при наведении - GREEN_BLUE, отключен - СВЕТЛО-СЕРЫЙ)
    ----------
    Методы:
    draw_button(): Рисует кнопку в виде цветного прямоугольника (по умолчанию ЧЕРНЫЙ)
    change_color_on_hover(): Рисует кнопку в виде прямоугольника цвета GREEN_BLUE
    print_message_for_button(): Печатает пояснительное сообщение рядом с кнопкой
    """

    def __init__(self, x_offset, button_title, message_to_show):
        self.__title = button_title
        self.__title_width, self.__title_height = font.size(self.__title)
        self.__message = message_to_show
        self.__button_width = self.__title_width + block_size
        self.__button_height = self.__title_height + block_size
        self.__x_start = x_offset
        self.__y_start = upper_margin + 10 * block_size + self.__button_height
        self.rect_for_draw = self.__x_start, self.__y_start, self.__button_width, self.__button_height
        self.rect = pg.Rect(self.rect_for_draw)
        self.__rect_for_button_title = self.__x_start + self.__button_width / 2 - \
            self.__title_width / 2, self.__y_start + \
            self.__button_height / 2 - self.__title_height / 2
        self.__color = BLACK

    def draw_button(self, color=None):
        """
        Рисует кнопку в виде цветного прямоугольника (по умолчанию ЧЕРНЫЙ)
        Аргументы:
            цвет (tuple, optional): Цвет кнопки. По умолчанию значение "Нет" (ЧЕРНЫЙ).
        """
        if not color:
            color = self.__color
        pg.draw.rect(screen, color, self.rect_for_draw)
        text_to_blit = font.render(self.__title, True, WHITE)
        screen.blit(text_to_blit, self.__rect_for_button_title)

    def change_color_on_hover(self):
        """
        Рисует кнопку в виде прямоугольника цвета GREEN_BLUE
        """
        mouse = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.draw_button(GREEN_BLUE)

    def print_message_for_button(self):
        """
        Печатает пояснительное сообщение рядом с кнопкой
        """
        message_width, message_height = font.size(self.__message)
        rect_for_message = self.__x_start / 2 - message_width / \
            2, self.__y_start + self.__button_height / 2 - message_height / 2
        text = font.render(self.__message, True, BLACK)
        screen.blit(text, rect_for_message)


class AutoShips:
    """
    Случайным образом создаёт все корабли игрока в сетке
    ----------
    Атрибуты:
        offset (int): Где начинается сетка (в количестве блоков)
                    (0 для компьютера и 15 для человека)
        available_blocks (set of tuples): координаты всех блоков
                    которые доступны для создания кораблей (обновляются каждый раз при создании корабля)
        ships_set (set of tuples): все блоки, занятые кораблями
        ships (list of lists): список всех отдельных судов (в виде списков)
    ----------
    Методы:
        __create_start_block(available_blocks):
            Случайным образом выбирает блок, с которого можно начать создание корабля.
            Случайным образом выбирает горизонтальный или вертикальный тип корабля
            Случайным образом выбирает направление (от начального блока) - прямое или обратное
            Возвращает три случайно выбранных значения
        __create_ship(number_of_blocks, available_blocks):
            Создает корабль заданной длины (number_of_blocks), начиная с начального блока,
                возвращенного предыдущим методом, используя тип корабля и направление (изменяя его
                если выход за пределы сетки), возвращенный предыдущим методом.
                Проверяет, является ли судно действительным (не рядом с другими судами и в пределах сетки)
                и добавляет его в список кораблей.
            Возвращает список кортежей с координатами нового корабля
        __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
            Проверяет, находятся ли новые отдельные блоки, добавляемые к кораблю в предыдущем методе
                в сетке, в противном случае изменяет направление.
            Возвращается:
                направление (int): прямое или обратное
                увеличенная/уменьшенная координата последнего/первого блока строящегося судна
        __is_ship_valid(new_ship):
            Проверяет, все ли координаты корабля находятся в пределах набора доступных блоков.
            Возвращает истину или ложь
        __add_new_ship_to_set(new_ship):
            Добавляет все блоки в списке кораблей в набор кораблей
        __update_available_blocks_for_creating_ships(new_ship):
            Удаляет все блоки, занятые кораблем и вокруг него, из набора доступных блоков
        __populate_grid():
            Создает необходимое количество кораблей каждого типа, вызывая метод create_ship.
                Добавляет каждый корабль в список кораблей, ships_set и обновляет доступные блоки.
            Возвращает список всех судов
    """

    def __init__(self, offset):
        """
        Параметры:
        offset (int): Где начинается сетка (в количестве блоков)
                (0 для компьютера и 15 для человека)
        available_blocks (set of tuples): координаты всех блоков,
                которые доступны для создания кораблей (обновляются каждый раз при создании корабля)
        ships_set (set of tuples): все блоки, занятые кораблями
        ships (list of lists): список всех отдельных судов (в виде списков)
        """

        self.offset = offset
        self.available_blocks = {(x, y) for x in range(1 + self.offset, 11 + self.offset) for y in range(1, 11)}
        self.ships_set = set()
        self.ships = self.__populate_grid()
        self.orientation = None
        self.direction = None

    def __create_start_block(self, available_blocks):
        """
        Случайным образом выбирает блок, с которого можно начать создание корабля.
        Случайным образом выбирает горизонтальный или вертикальный тип корабля
        Случайным образом выбирает направление (от начального блока) - прямое или обратное
        Аргументы:
            available_blocks (set of tuples): координаты всех блоков,
                    которые доступны для создания кораблей (обновляются каждый раз при создании корабля)
        Возвращает:
            int: x координата случайного блока
            int: y координата случайного блока
            int: 0=horizontal (изменение x), 1=vertical (изменение y)
            int: 1=straight, -1=reverse
        """
        self.orientation = random.randint(0, 1)
        # -1 - влево или вниз, 1 - вправо или вверх
        self.direction = random.choice((-1, 1))
        x, y = random.choice(tuple(available_blocks))
        return x, y, self.orientation, self.direction

    def __create_ship(self, number_of_blocks, available_blocks):
        """
        Создает корабль заданной длины (number_of_blocks), начиная с начального блока,
            возвращенного предыдущим методом, используя тип корабля и направление (изменяя его
            если выход за пределы сетки), возвращенный предыдущим методом.
            Проверяет, является ли судно действительным (не рядом с другими судами и в пределах сетки)
            и добавляет его в список кораблей.
        Аргументы:
            number_of_blocks (int): длина необходимого судна
            available_blocks (set): бесплатные блоки для создания кораблей
        Возвращает:
            list: список кортежей с координатами нового судна
        """
        ship_coordinates = []
        x, y, self.orientation, self.direction = self.__create_start_block(available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not self.orientation:
                self.direction, x = self.__get_new_block_for_ship(x, self.direction, self.orientation, ship_coordinates)
            else:
                self.direction, y = self.__get_new_block_for_ship(y, self.direction, self.orientation, ship_coordinates)
        if self.__is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.__create_ship(number_of_blocks, available_blocks)

    def __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
        """
        Проверяет, находятся ли новые отдельные блоки, добавляемые к кораблю в предыдущем методе
            в сетке, в противном случае изменяет направление.
        Аргументы:
            coor (int): координата x или y для увеличения/ уменьшения
            direction (int): 1 или -1
            orientation (int): 0 или 1
            ship_coordinates (list): координаты недостроенного корабля
        Возвращает:
            direction (int): straight или reverse
                увеличенная/уменьшенная координата последнего/первого блока строящегося судна (int)
        """
        self.direction = direction
        self.orientation = orientation
        if (coor <= 1 - self.offset * (self.orientation - 1) and self.direction == -1) or (
                coor >= 10 - self.offset * (self.orientation - 1) and self.direction == 1):
            self.direction *= -1
            return self.direction, ship_coordinates[0][self.orientation] + self.direction
        else:
            return self.direction, ship_coordinates[-1][self.orientation] + self.direction

    def __is_ship_valid(self, new_ship):
        """
        Проверьте, все ли координаты корабля находятся в пределах набора доступных блоков.
        Аргументы:
            new_ship (list): список кортежей с координатами вновь созданного судна
        Возвращает:
            bool: True или False
        """
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def __add_new_ship_to_set(self, new_ship):
        """
        Добавляет все блоки в списке кораблей в ships_set
        Аргументы:
            new_ship (list): список кортежей с координатами вновь созданного судна
        """
        self.ships_set.update(new_ship)

    def __update_available_blocks_for_creating_ships(self, new_ship):
        """
        Удаляет все блоки, занятые кораблем и вокруг него, из набора доступных блоков
        Аргументы:
            new_ship ([type]): список кортежей с координатами вновь созданного судна
        """
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if self.offset < (elem[0] + k) < 11 + self.offset and 0 < (elem[1] + m) < 11:
                        self.available_blocks.discard((elem[0] + k, elem[1] + m))

    def __populate_grid(self):
        """
        Создает необходимое количество кораблей каждого типа, вызывая метод create_ship.
            Добавляет каждый корабль в список кораблей, ships_set и обновляет доступные блоки.
        Возвращает:
            list: 2d-список всех кораблей
        """
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5 - number_of_blocks):
                new_ship = self.__create_ship(number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.__add_new_ship_to_set(new_ship)
                self.__update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list

# ===========Секция стрельбы==============


def computer_shoots(set_to_shoot_from):
    """
    Случайным образом выбирает блок из доступных для выстрела набора клеток.
    """
    pg.time.delay(600)
    computer_fired_block = random.choice(tuple(set_to_shoot_from))
    computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def check_hit_or_miss(fired_block, opponents_ships_list, computer_turn, opponents_ships_list_original_copy,
                      opponents_ships_set):
    """
    Проверяет, является ли блок, в который выстрелил компьютер или человек, попаданием или промахом.
    Наборы обновлений с точками (в пропущенных блоках или в диагональных блоках вокруг блока попадания) и "X".
    (в блоках попадания).
    Удаляет уничтоженные корабли из списка кораблей.
    """
    for elem in opponents_ships_list:
        diagonal_only = True
        if fired_block in elem:
            # Это делается для того, чтобы расставить точки до и после уничтоженного корабля
            # и нарисовать уничтоженные корабли компьютера (которые скрыты до тех пор, пока не будут уничтожены)
            ind = opponents_ships_list.index(elem)
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only)
            elem.remove(fired_block)
            # Это делается для того, чтобы проверить, кто проиграет - если ships_set пуст
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                last_hits_list.append(fired_block)
                update_around_last_computer_hit(fired_block, True)
            # Если корабль будет уничтожен
            if not elem:
                update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy)
                if computer_turn:
                    last_hits_list.clear()
                    around_last_computer_hit_set.clear()
                else:
                    # Добавьте уничтоженный корабль компьютера
                    # в список, чтобы нарисовать его (компьютерные корабли скрыты)
                    destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(fired_block)
    if computer_turn:
        update_around_last_computer_hit(fired_block, False)
    return False


def update_destroyed_ships(ind, computer_turn, opponents_ships_list_original_copy):
    """
    Добавляет блоки до и после корабля в dotted_set, чтобы нарисовать на них точки.
    Добавляет все блоки на корабле в набор hit_blocks для рисования крестиков внутри разрушенного корабля.
    """
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(ship[i], computer_turn, False)


def update_around_last_computer_hit(fired_block, computer_hits):
    """
    Обновляет around_last_computer_hit_set (который используется для выбора компьютера для стрельбы), если он
    попал в корабль, но не уничтожил его). Добавляет к этому набору вертикальные или горизонтальные блоки вокруг
    блока, который был поражен последним. Затем удаляет те блоки из этого набора, в которые стреляли, но промахнулись.
    around_last_computer_hit_set заставляет компьютер выбирать правильные блоки, чтобы быстро уничтожить корабль,
    вместо того, чтобы просто случайным образом стрелять по совершенно случайным блокам.
    """
    global around_last_computer_hit_set, computer_available_to_fire_set
    if computer_hits and fired_block in around_last_computer_hit_set:
        around_last_computer_hit_set = computer_hits_twice()
    elif computer_hits and fired_block not in around_last_computer_hit_set:
        computer_first_hit(fired_block)
    elif not computer_hits:
        around_last_computer_hit_set.discard(fired_block)

    around_last_computer_hit_set -= dotted_set_for_computer_not_to_shoot
    around_last_computer_hit_set -= hit_blocks_for_computer_not_to_shoot
    computer_available_to_fire_set -= around_last_computer_hit_set
    computer_available_to_fire_set -= dotted_set_for_computer_not_to_shoot


def computer_first_hit(fired_block):
    """
    Добавляет блоки выше, ниже, справа и слева от блока,
        пораженного компьютером, во временный набор, из которого компьютер может выбрать свой следующий снимок.
    Аргументы:
        fired_block (tuple): координаты блока, пораженного компьютером
    """
    x_hit, y_hit = fired_block
    if x_hit > 16:
        around_last_computer_hit_set.add((x_hit - 1, y_hit))
    if x_hit < 25:
        around_last_computer_hit_set.add((x_hit + 1, y_hit))
    if y_hit > 1:
        around_last_computer_hit_set.add((x_hit, y_hit - 1))
    if y_hit < 10:
        around_last_computer_hit_set.add((x_hit, y_hit + 1))


def computer_hits_twice():
    """
    Добавляет блоки до и после двух или более блоков корабля во временный список
        для компьютера, чтобы быстрее закончить корабль.
    Возвращает:
        set: временный набор блоков, где потенциально должен находиться человеческий корабль,
        с которого компьютер может стрелять
    """
    last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(last_hits_list) - 1):
        x1 = last_hits_list[i][0]
        x2 = last_hits_list[i + 1][0]
        y1 = last_hits_list[i][1]
        y2 = last_hits_list[i + 1][1]
        if x1 == x2:
            if y1 > 1:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < 10:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > 16:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < 25:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(fired_block, computer_turn, diagonal_only=True):
    """
    Помещает точки в центр диагонали или вокруг блока, который был поражен (человеком или
    с помощью компьютера). Добавляет все диагональные блоки или круговой выбранный блок в отдельный набор
    block: block попадания (tuple)
    """
    global dotted_set
    x, y = fired_block
    a = 15 * computer_turn
    b = 11 + 15 * computer_turn
    # Добавляет блок, пораженный компьютером, в набор его попаданий, чтобы позже удалить
    # их из набора блоков, доступных для него, чтобы стрелять из
    hit_blocks_for_computer_not_to_shoot.add(fired_block)
    # Добавляет блоки попадания либо в сетку 1 (x:1-10), либо в сетку 2 (x:16-25).
    hit_blocks.add(fired_block)
    # Добавляет блоки по диагонали или по всему блоку в соответствующие наборы
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (not diagonal_only or i != 0 and j != 0) and a < x + i < b and 0 < y + j < 11:
                add_missed_block_to_dotted_set((x + i, y + j))
    dotted_set -= hit_blocks


def add_missed_block_to_dotted_set(fired_block):
    """
    Добавляет fired_block к набору пропущенных
    выстрелов (если fired_block - это промах), чтобы затем нарисовать на них точки.
    Также необходимо, чтобы компьютер удалил эти пунктирные блоки из набора доступных
    блоков, из которых он может стрелять.
    """
    dotted_set.add(fired_block)
    dotted_set_for_computer_not_to_shoot.add(fired_block)


# ===========РАЗДЕЛ ЧЕРТЕЖА==============

def draw_ships(ships_coordinates_list):
    """
    Рисует прямоугольники вокруг блоков, занятых кораблем
    Аргументы:
        ships_coordinates_list (list of tuples): список координат корабля
    """
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Горизонтальные и 1 блочные корабли
        ship_width = block_size * len(ship)
        ship_height = block_size
        # Вертикальные корабли
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width, ship_height = ship_height, ship_width
        x = block_size * (x_start - 1) + left_margin
        y = block_size * (y_start - 1) + upper_margin
        pg.draw.rect(screen, BLACK, ((x, y), (ship_width, ship_height)), width=block_size // 10)


def draw_from_dotted_set(dotted_set_to_draw_from):
    """
    Рисует точки в центре всех блоков в наборе точек
    """
    for elem in dotted_set_to_draw_from:
        pg.draw.circle(screen, BLACK, (block_size * (
            elem[0] - 0.5) + left_margin, block_size * (elem[1] - 0.5) + upper_margin), block_size // 6)


def draw_hit_blocks(hit_blocks_to_draw_from):
    """
    Рисует "X" в блоках, которые были успешно поражены компьютером или человеком
    """
    for block in hit_blocks_to_draw_from:
        x1 = block_size * (block[0] - 1) + left_margin
        y1 = block_size * (block[1] - 1) + upper_margin
        pg.draw.line(screen, BLACK, (x1, y1), (x1 + block_size, y1 + block_size), block_size // 6)
        pg.draw.line(screen, BLACK, (x1, y1 + block_size), (x1 + block_size, y1), block_size // 6)


def show_message_at_rect_center(message, rect, which_font=font, color=RED):
    """
    Выводит сообщение на экран в центре заданного прямоугольника.
    Аргументы:
        message (str): Сообщение для печати
        rect (tuple): прямоугольник в формате (x_start, y_start, width, height)
        which_font (pg font object, optional): Какой шрифт использовать для печати сообщения.
        По умолчанию используется шрифт.
        color (tuple, optional): Цвет сообщения. По умолчанию используется КРАСНЫЙ цвет.
    """
    message_width, message_height = which_font.size(message)
    message_rect = pg.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pg.Rect(x_start - block_size / 2, y_start, message_width + block_size, message_height)
    message_to_blit = which_font.render(message, True, color)
    screen.fill(WHITE, background_rect)
    screen.blit(message_to_blit, (x_start, y_start))


def ship_is_valid(ship_set, blocks_for_manual_drawing):
    """
    Проверяет, не касается ли корабль других судов
    Аргументы:
        ship_set (set): Набор с кортежами координат новых кораблей
        blocks_for_manual_drawing (set): Набор со всеми используемыми блоками для других кораблей, включая все
        блоки вокруг кораблей.
    Возвращает:
        Bool: True, если корабли не соприкасаются, в противном случае False.
    """
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def check_ships_numbers(ship, num_ships_list):
    """
    Проверяет, не превышает ли судно определенной длины (1-4) необходимое количество (4-1).
    Аргументы:
        ship (list): Список с координатами новых судов
        num_ships_list (list): Список с номерами конкретных судов в соответствующих индексах.
    Возвращает:
        Bool: True, если количество судов определенной длины не превышает необходимого,
            False, если таких судов достаточно.
    """
    return (5 - len(ship)) > num_ships_list[len(ship)-1]


def update_used_blocks(ship, method):
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                method((block[0]+i, block[1]+j))


computer = AutoShips(0)
computer_ships_working = copy.deepcopy(computer.ships)

auto_button_place = left_margin + 17 * block_size
manual_button_place = left_margin + 20 * block_size
how_to_create_ships_message = "Как вы хотите создать корабли? Нажмите кнопку"
auto_button = Button(auto_button_place, "АВТО", how_to_create_ships_message)
manual_button = Button(manual_button_place, "ВРУЧНУЮ", how_to_create_ships_message)
undo_message = "Для отмены последнего корабля нажмите кнопку"
undo_button_place = left_margin + 12 * block_size
undo_button = Button(undo_button_place, "ОТМЕНА", undo_message)


def main():
    game_not_start = True
    music = True
    button_size_w, button_size_h, big_button_size_w, big_button_size_h = 350, 85, 360, 101
    small_button_size_w, small_button_size_h = 344, 79
    menu_image = pg.image.load("menu_without_buttons.png")
    menu_img = pg.transform.scale(menu_image, size)
    play_image = pg.image.load("buttons/button_play.png")
    play_img = pg.transform.scale(play_image, (button_size_w, button_size_h))
    quit_image = pg.image.load("buttons/button_quit.png")
    quit_img = pg.transform.scale(quit_image, (button_size_w, button_size_h))
    pg.mixer.music.load('background_soundtrack.mp3')
    pg.mixer.music.set_volume(0.05)
    pg.mixer.music.play(-1)
    play_collide = False
    quit_collide = False
    while game_not_start:
        mouse = pg.mouse.get_pos()
        screen.blit(menu_img, (0, 0))
        play_x, play_y = size[0] // 2 - 190, size[1] // 2 - 50
        quit_x, quit_y = size[0] // 2 - 190, size[1] // 2 + 50
        big_play_x, big_play_y = size[0] // 2 - 195, size[1] // 2 - 58
        small_quit_x, small_quit_y = size[0] // 2 - 187, size[1] // 2 + 53
        if play_collide:
            screen.blit(play_img, (big_play_x, big_play_y))
        else:
            screen.blit(play_img, (play_x, play_y))
        if quit_collide:
            screen.blit(quit_img, (small_quit_x, small_quit_y))
        else:
            screen.blit(quit_img, (quit_x, quit_y))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                mouse = pg.mouse.get_pos()
                if play_x < mouse[0] < play_x + button_size_w and play_y < mouse[1] < play_y + button_size_h:
                    game_not_start = False
                elif quit_x < mouse[0] < quit_x + button_size_w and quit_y < mouse[1] < quit_y + button_size_h:
                    quit_not_decided = True
                    quit_menu_image = pg.image.load("buttons/quit_menu.png")
                    quit_menu_img = pg.transform.scale(quit_menu_image, (450, 300))
                    while quit_not_decided:
                        screen.blit(quit_menu_img, (size[0] // 2 - 225, size[1] // 2 - 167))
                        yes_x0, yes_x1, yes_y0, yes_y1 = 376, 461, 343, 427
                        no_x0, no_x1, no_y0, no_y1 = 590, 673, 343, 427
                        pg.display.update()
                        for quit_event in pg.event.get():
                            if quit_event.type == pg.QUIT:
                                pg.quit()
                            if quit_event.type == pg.MOUSEBUTTONDOWN:
                                quit_mouse = pg.mouse.get_pos()
                                if yes_x0 < quit_mouse[0] < yes_x1 and yes_y0 < quit_mouse[1] < yes_y1:
                                    quit_not_decided = False
                                    game_not_start = False
                                    pg.quit()
                                elif no_x0 < quit_mouse[0] < no_x1 and no_y0 < quit_mouse[1] < no_y1:
                                    quit_not_decided = False
            elif not play_collide:
                if play_x < mouse[0] < play_x + button_size_w and play_y < mouse[1] < play_y + button_size_h:
                    play_img = pg.transform.scale(play_image, (big_button_size_w, big_button_size_h))
                    play_collide = True
            elif play_collide:
                if not (big_play_x < mouse[0] < big_play_x + big_button_size_w and big_play_y < mouse[1] < big_play_y \
                        + big_button_size_h):
                    play_img = pg.transform.scale(play_image, (button_size_w, button_size_h))
                    play_collide = False
            if not quit_collide:
                if quit_x < mouse[0] < quit_x + button_size_w and quit_y < mouse[1] < quit_y + button_size_h:
                    quit_img = pg.transform.scale(quit_image, (small_button_size_w, small_button_size_h))
                    quit_collide = True
            elif quit_collide:
                if not (small_quit_x < mouse[0] < small_quit_x + small_button_size_w and small_quit_y < mouse[1] <
                        small_quit_y + small_button_size_h):
                    quit_img = pg.transform.scale(quit_image, (button_size_w, button_size_h))
                    quit_collide = False

        pg.display.update()
    note_image = pg.image.load("buttons/note.png")
    note_img = pg.transform.scale(note_image, (60, 65))
    not_note_image = pg.image.load("buttons/not_note.png")
    not_note_img = pg.transform.scale(not_note_image, (60, 65))

    ships_creation_not_decided = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False
    start = (0, 0)
    ship_size = (0, 0)

    rect_for_grids = (0, 0, size[0], upper_margin + 12 * block_size)
    rect_for_messages_and_buttons = (0, upper_margin + 11 * block_size, size[0], 5 * block_size)
    message_rect_for_drawing_ships = (undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2],
                                      upper_margin + 11 * block_size, size[0] -
                                      (undo_button.rect_for_draw[0] + undo_button.rect_for_draw[2]), 4 * block_size)
    message_rect_computer = (left_margin - 2 * block_size, upper_margin +
                             11 * block_size, 14 * block_size, 4 * block_size)
    message_rect_human = (left_margin + 15 * block_size, upper_margin +
                          11 * block_size, 10 * block_size, 4 * block_size)

    human_ships_to_draw = []
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    num_ships_list = [0, 0, 0, 0]

    screen.fill(WHITE)
    screen.blit(note_img, [10, 10])
    computer_grid = Grid("КОМПЬЮТЕР", 0)
    human_grid = Grid("ЧЕЛОВЕК", 15)

    while ships_creation_not_decided:
        auto_button.draw_button()
        manual_button.draw_button()
        auto_button.change_color_on_hover()
        manual_button.change_color_on_hover()
        auto_button.print_message_for_button()

        mouse = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game_over = True
                ships_creation_not_decided = False
                ships_not_created = False
            # Если нажата кнопка АВТО - автоматически создавать человеческие корабли
            elif event.type == pg.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                human = AutoShips(15)
                human_ships_to_draw = human.ships
                human_ships_working = copy.deepcopy(human.ships)
                human_ships_set = human.ships_set
                ships_creation_not_decided = False
                ships_not_created = False
            elif event.type == pg.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                ships_creation_not_decided = False
            elif event.type == pg.MOUSEBUTTONDOWN and 10 < mouse[0] < 70 and 10 < mouse[1] < 75:
                if music:
                    screen.fill(WHITE, (0, 0, 80, 80))
                    screen.blit(not_note_img, [10, 10])
                    music = False
                    pg.mixer.music.pause()
                else:
                    screen.fill(WHITE, (0, 0, 80, 80))
                    screen.blit(note_img, [10, 10])
                    music = True
                    pg.mixer.music.unpause()

        pg.display.update()
        screen.fill(WHITE, rect_for_messages_and_buttons)
        if music:
            screen.blit(note_img, [10, 10])
        else:
            screen.blit(not_note_img, [10, 10])

    while ships_not_created:
        screen.fill(WHITE, rect_for_grids)
        if music:
            screen.blit(note_img, [10, 10])
        else:
            screen.blit(not_note_img, [10, 10])
        computer_grid = Grid("КОМПЬЮТЕР", 0)
        human_grid = Grid("ЧЕЛОВЕК", 15)
        undo_button.draw_button()
        undo_button.print_message_for_button()
        undo_button.change_color_on_hover()
        mouse = pg.mouse.get_pos()
        if not human_ships_to_draw:
            undo_button.draw_button(LIGHT_GRAY)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                ships_not_created = False
                game_over = True
            elif undo_button.rect.collidepoint(mouse) and event.type == pg.MOUSEBUTTONDOWN:
                if human_ships_to_draw:
                    screen.fill(WHITE, message_rect_for_drawing_ships)
                    deleted_ship = human_ships_to_draw.pop()
                    num_ships_list[len(deleted_ship) - 1] -= 1
                    update_used_blocks(deleted_ship, used_blocks_for_manual_drawing.discard)
            elif event.type == pg.MOUSEBUTTONDOWN:  # start_here
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = (0, 0)
            elif drawing and event.type == pg.MOUSEMOTION:
                x_end, y_end = event.pos
                ship_size = x_end - x_start, y_end - y_start
            elif drawing and event.type == pg.MOUSEBUTTONUP:
                x_end, y_end = event.pos
                drawing = False
                ship_size = (0, 0)
                start_block = ((x_start - left_margin) // block_size + 1, (y_start - upper_margin) // block_size + 1)
                end_block = ((x_end - left_margin) // block_size + 1, (y_end - upper_margin) // block_size + 1)
                if start_block > end_block:
                    start_block, end_block = end_block, start_block
                temp_ship = []
                if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and \
                   15 < end_block[0] < 26 and 0 < end_block[1] < 11:
                    screen.fill(WHITE, message_rect_for_drawing_ships)
                    if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
                        for block in range(start_block[1], end_block[1]+1):
                            temp_ship.append((start_block[0], block))
                    elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
                        for block in range(start_block[0], end_block[0]+1):
                            temp_ship.append((block, start_block[1]))
                    else:
                        show_message_at_rect_center("КОРАБЛЬ СЛИШКОМ БОЛЬШОЙ!", message_rect_for_drawing_ships)
                else:
                    show_message_at_rect_center("КОРАБЛЬ ЗА ПРЕДЕЛАМИ СЕТКИ!", message_rect_for_drawing_ships)
                if temp_ship:
                    temp_ship_set = set(temp_ship)
                    if ship_is_valid(temp_ship_set, used_blocks_for_manual_drawing):
                        if check_ships_numbers(temp_ship, num_ships_list):
                            num_ships_list[len(temp_ship) - 1] += 1
                            human_ships_to_draw.append(temp_ship)
                            human_ships_set |= temp_ship_set
                            update_used_blocks(temp_ship, used_blocks_for_manual_drawing.add)
                        else:
                            show_message_at_rect_center(
                                f"УЖЕ ДОСТАТОЧНО {len(temp_ship)}-ПАЛУБНЫХ КОРАБЛЕЙ", message_rect_for_drawing_ships)
                    else:
                        show_message_at_rect_center("КОРАБЛИ ПРИКАСАЮТСЯ!", message_rect_for_drawing_ships)
            if event.type == pg.MOUSEBUTTONDOWN and 10 < mouse[0] < 70 and 10 < mouse[1] < 75:
                if music:
                    screen.fill(WHITE, (0, 0, 80, 80))
                    # screen.blit(not_note_img, [10, 10])
                    music = False
                    pg.mixer.music.pause()
                else:
                    screen.fill(WHITE, (0, 0, 80, 80))
                    # screen.blit(note_img, [10, 10])
                    music = True
                    pg.mixer.music.unpause()
            if len(human_ships_to_draw) == 10:
                ships_not_created = False
                human_ships_working = copy.deepcopy(human_ships_to_draw)
                screen.fill(WHITE, rect_for_messages_and_buttons)

        pg.draw.rect(screen, BLACK, (start, ship_size), 3)
        draw_ships(human_ships_to_draw)
        pg.display.update()

    while not game_over:
        draw_ships(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)
        if not (dotted_set | hit_blocks):
            show_message_at_rect_center("ИГРА НАЧАЛАСЬ! ВАШ ХОД!", message_rect_computer)
        for event in pg.event.get():
            mouse = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                game_over = True
            if event.type == pg.MOUSEBUTTONDOWN and 10 < mouse[0] < 70 and 10 < mouse[1] < 75:
                if music:
                    screen.fill(WHITE, (0, 0, 80, 80))
                    screen.blit(not_note_img, [10, 10])
                    music = False
                    pg.mixer.music.pause()
                else:
                    screen.fill(WHITE, (0, 0, 80, 80))
                    screen.blit(note_img, [10, 10])
                    music = True
                    pg.mixer.music.unpause()
            elif not computer_turn and event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (left_margin < x < left_margin + 10 * block_size) and (
                        upper_margin < y < upper_margin + 10 * block_size):
                    fired_block = ((x - left_margin) // block_size + 1, (y - upper_margin) // block_size + 1)
                    computer_turn = not check_hit_or_miss(fired_block, computer_ships_working, False, computer.ships,
                                                          computer.ships_set)
                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill(WHITE, message_rect_computer)
                    show_message_at_rect_center(
                        f"ВАШ ПОСЛЕДНИЙ ХОД: "
                        f"{LETTERS[fired_block[0]-1] + str(fired_block[1])}", message_rect_computer, color=BLACK)
                else:
                    show_message_at_rect_center("ВЫСТРЕЛ ЗА ПРЕДЕЛЫ СЕТКИ!", message_rect_computer)
        pg.display.update()
        if computer_turn:
            set_to_shoot_from = computer_available_to_fire_set
            if around_last_computer_hit_set:
                set_to_shoot_from = around_last_computer_hit_set
            fired_block = computer_shoots(set_to_shoot_from)
            computer_turn = check_hit_or_miss(
                fired_block, human_ships_working, True, human_ships_to_draw, human_ships_set)
            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            screen.fill(WHITE, message_rect_human)
            show_message_at_rect_center(
                f"ПОСЛЕДНИЙ ХОД КОМПЬЮТЕРА: "
                f"{LETTERS[fired_block[0] - 16] + str(fired_block[1])}", message_rect_human, color=BLACK)
        pg.display.update()
        if not computer.ships_set:
            show_message_at_rect_center("ВЫ ВЫИГРАЛИ!", (0, 0, size[0], size[1]), game_over_font)
            game_over = True
        if not human_ships_set:
            show_message_at_rect_center("ВЫ ПРОИГРАЛИ!", (0, 0, size[0], size[1]), game_over_font)
            game_over = True

        pg.display.update()
    pg.time.delay(2500)
    pg.quit()


if __name__ == '__main__':
    main()
