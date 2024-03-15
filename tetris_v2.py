"""
Клавиши управления:
D - сдвинуть фигуру вправо;
A - сдвинуть фигуру влево;
E - Повернуть фигуру вправо;
Q - повернуть фигуру влево;
B - прервать игровой процесс, выход из игры.
"""

import cv2
import random
import numpy as np

"""
TODO:
-Реализовать проверки для поворота фигур и для смещения влево-вправо
на предмет совпадения новых координат с уже упавшими фигурами;
-Улучшить вращение фигур, удаляя пустые строки и столбцы перед вращением.
"""

IN_GAME = True #Продолжается ли игра
SEG_SIZE = 25 #Размер одного сегмента
score = 0 #Игровой счёт
step_time = 50 #Шаг, на который меняется показатель waiting_time
shape_coords = [] #Координаты всех сегментов активной фигуры
waiting_time = 1000 #Время ожидания перед нажатием клавиши игроком.
active_shape = False #Флаг на наличие фигуры на поле

#Параметры разработчика:
DEBUG = False #Показывает информацию о состоянии игры
DEBUG_TYPING = False #Отображает тайпинги некоторых переменных.

#Пресеты координат для различных фигур
start_shape_coords = [[(1, 4), (0, 4), (2, 4), (3, 4)],
                      [(1, 4), (0, 4), (0, 5), (1, 5)],
                      [(0, 5), (0, 6), (1, 5), (1, 4)],
                      [(1, 5), (0, 5), (1, 6), (0, 4)],
                      [(1, 5), (1, 4), (1, 6), (0, 4)],
                      [(0, 5), (0, 4), (0, 6), (1, 4)],
                      [(1, 5), (1, 4), (1, 6), (0, 5)]]

#Массив для записи координат фигур на поле, активных и упавших
field_back = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


class Segment():
    def __init__(self, x, y, color):
        self.x = x*SEG_SIZE
        self.y = y*SEG_SIZE
        self.color = color

    def change_color(self,new_color):
        self.color = new_color

    def activate(self):
        #Создать цевтной квадрат по координатам сегмента
        cv2.rectangle(field_face, (self.x, self.y),
        (self.x+SEG_SIZE, self.y+SEG_SIZE),
        self.color, thickness=-1)
        #Отрисовать границы
        cv2.rectangle(field_face, (self.x, self.y),
        (self.x+SEG_SIZE, self.y+SEG_SIZE),
        (0, 0, 0), thickness=1)

    def deactivate(self):
        #Создать чёрный квадрат по координатам сегмента
        cv2.rectangle(field_face, (self.x, self.y),
        (self.x+SEG_SIZE, self.y+SEG_SIZE),
        (0, 0, 0), thickness=-1)
        #Отрисовать границы
        cv2.rectangle(field_face, (self.x, self.y),
        (self.x+SEG_SIZE, self.y+SEG_SIZE),
        (0, 255, 0), thickness=1)


def create_flip(size:tuple) -> list:
    x,y = size[0],size[1]
    flip = []
    for i in range(y):
        string = []
        for j in range(x):
            a = Segment(j,i,(255,255,255))
            string.append(a)
        flip.append(string)
    return flip


def pprint(lst:list):
    """Выводит на печать список в удобном для воспрития виде.
    Неободима для отладки и проверки состояния массива field_back."""
    for i in lst:
        print(i)
    print('-' * 30)


def create_shape(shape_coords:list):
    """Вносит в массив field_back начальные координаты при
    появлении на поле новой фигуры. Символ активной фигуры - 2."""
    global field_back
    for xy in shape_coords:
        x,y = xy[0], xy[1]
        field_back[x][y] = 2


def check_left_right(new_coords:list) -> bool:
    global field_back
    #Добавить сюда же проверку на пересечение с уже упавшими фигурами
    for xy in new_coords:
        x,y = xy[0], xy[1]
        #Проверка на границы:
        if y < 0 or y > 9:
            return False
        if field_back[x-1][y] == 1:
            print(new_coords)
            print('Клетка уже занята!')
            return False
    return True

def check_down(new_coords:list) -> bool:
    global active_shape
    global field_back
    for xy in new_coords:
        x,y = xy[0], xy[1]
        #Проверка на нижнюю границу
        if x >= 20 or field_back[x][y] == 1:
            active_shape = False
            for xy in new_coords:
                x,y = xy[0], xy[1]
                field_back[x-1][y] = 1
            return False
    return True

def check_bug_field(field_back:list, shape_coords:list) -> list:
    """Проходит по всему массиву field_back, удаляя
    случайные 2-ки в тех местах, где их не должно быть."""
    for x in range(len(field_back)):
        for y in range(len(field_back[0])):
            if field_back[x][y] == 2 and (x,y) not in shape_coords:
                field_back[x][y] = 0

    return field_back


def move_shape(shape_coords:list, vector:tuple) -> list:
    global field_back
    new_coords = []
    for xy in shape_coords:
        x,y = xy[0], xy[1]
        x += vector[0]
        y += vector[1]
        new_coords.append((x,y))

    if check_left_right(new_coords) and check_down(new_coords):
        #Стирание старой фигуры
        for xy in shape_coords:
            x,y = xy[0], xy[1]
            field_back[x][y] = 0
        #И её отрисовка на новом месте
        for xy in new_coords:
            x,y = xy[0], xy[1]
            field_back[x][y] = 2
        return new_coords
    return shape_coords


def rotate_shape(shape_coords:list, rotate:int) -> list:
    #Теория: удалять пустые строки и столбцы после записи координат.
    #Так можно добиться более интуитивно понятного вращения фигур.
    shape = [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]
    #Заведомо нереалистичные значения
    min_x = 100
    min_y = 100

    for xy in shape_coords:
        x, y = xy[0], xy[1]
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y

    for xy in shape_coords:
        x, y = xy[0], xy[1]
        new_x = x - min_x
        new_y = y - min_y
        shape[new_x][new_y] = 1

    #Удаление пустых строк из списка
    while [0,0,0,0] in shape:
        shape.remove([0,0,0,0])

    my_shape = np.array(shape)
    my_shape = np.rot90(my_shape,k=rotate)
    new_coords = []
    for i in range(len(my_shape)):
        x = my_shape[i]
        for j in range(len(my_shape[0])):
            position = x[j]
            if position == 1:
                new_coords.append((i+min_x,j+min_y))

    if DEBUG:
        print(f"Координаты до вращения: {shape_coords}\n")
        print(f"Координаты после вращения: {new_coords}")

    if check_left_right(new_coords) and check_down(new_coords):
        #Стирание старой фигуры
        for xy in shape_coords:
            x,y = xy[0], xy[1]
            field_back[x][y] = 0
        #И её отрисовка на новом месте
        for xy in new_coords:
            x,y = xy[0], xy[1]
            field_back[x][y] = 2
        return new_coords
    return shape_coords


def update_field_back(score:int, waiting_time:int) -> int:
    global field_back
    global IN_GAME
    empty_string = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #Проверка на заполненную строку
    for i in range(len(field_back)):
        if 0 not in field_back[i] and 2 not in field_back[i]:
            field_back.pop(i)
            field_back.insert(0, empty_string)
            score += 1
            waiting_time -= step_time
    #Проверка на окончание игры
    if 1 in field_back[0]:
        IN_GAME = False
        print_end_game_message(score)
    return score, waiting_time


def draw_face(field_back:list):
    """Принимает на вход массив field_back, отрисовывая на его
    основе графигу в комфортном для пользователя виде.
    Взаимодействует с полем field_face."""
    global field_face
    for x in range(len(field_back)):
        for y in range(len(field_back[0])):
            if field_back[x][y] in [1,2]:
                flip[x][y].activate()
            else:
                flip[x][y].deactivate()


def print_end_game_message(score):
    text=('Игра окончена!', f'Ваш счет: {score}.',
          'Для выхода','нажмите', 'любую', 'клавишу.')
    font = cv2.FONT_HERSHEY_COMPLEX

    i = 1
    for message in text:
        cv2.putText(field_face, message, (SEG_SIZE,SEG_SIZE*i), font,
                      0.8, color = (255,0,255), thickness=1)
        i += 1
    cv2.imshow('Tetris v2.0', field_face)
    cv2.waitKey()

#------------------------------------------------------------------------------

#Создание игрового поля.
field_face = np.zeros((SEG_SIZE*20+1, SEG_SIZE*10+1, 3), dtype = 'uint8')

#Расчерчивает поле на сегменты.
for x in range(10):
    for y in range(20):
        cv2.rectangle(field_face,(x*SEG_SIZE,y*SEG_SIZE),
        ((x*SEG_SIZE)+SEG_SIZE,(y*SEG_SIZE)+SEG_SIZE),
        (0, 255, 0), thickness=1)

#Подготовка массива отрисовки сегментов
flip = create_flip((10,20))

#Перемнные для сброса фигуры
new_time = 10
old_time = waiting_time

while IN_GAME:
    #Окно необходимо для захвата клавиши
    cv2.imshow('Tetris v2.0', field_face)

    if not active_shape:
        num_type_shape = random.randint(0,6)
        #num_type_shape = 1
        shape_coords = start_shape_coords[num_type_shape]
        create_shape(shape_coords)
        active_shape = True
        #Возврат к нормальному течению времени
        waiting_time = old_time - (step_time*score)

    key = cv2.waitKey(waiting_time)

    if key == 226 or key == 100:
        shape_coords = move_shape(shape_coords, (0,1))
    elif key == 244 or key == 97:
        shape_coords = move_shape(shape_coords, (0,-1))
    elif key == 113 or key == 233:
        shape_coords = rotate_shape(shape_coords, 1)
    elif key == 101 or key == 243:
        shape_coords = rotate_shape(shape_coords, -1)

    elif key == 32:
        #"Сброс" фигуры вниз
        waiting_time = new_time

    elif key == 98 or key == 232:
        break

    print(key)

    field_back = check_bug_field(field_back, shape_coords)

    if DEBUG:
        pprint(field_back)
        print(f"key = {key}")
        print(shape_coords)
    if DEBUG_TYPING:
        print(f"Тип shape_coords = {type(shape_coords)}")
        print(f"Тип field_back = {type(shape_coords)}")
        #Для того, что бы вывести на печать тайпинги только один раз
        DEBUG_TYPING = False

    draw_face(field_back)
    score, waiting_time = update_field_back(score, waiting_time)

    shape_coords = move_shape(shape_coords, (1,0))
