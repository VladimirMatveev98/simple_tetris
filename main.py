"""
Здесь будет описание модуля.
"""
import cv2
import random
import numpy as np

"""
TODO:
-Реализовать вращение фигур;
-Проверить коллизию фигур после поворота:
    -С границами поля;
    -С другими фигурами.
-Устранить баги;
-Вписать документацию модуля и указать типы данных в функциях;
-Реализовать вывод счёта текстом из openCV на игровое поле.
Не удалять поле по завершению игры до нажатия любой клавиши;
-Записать файл зависимостей для pip;

Фичи:
-Настройка сложности?
-Ускорение игры со временем?
-Запоминание рекорда? Формат CSV - имя пользователя:рекорд?
-Отображать подсказку с управлением для новых пользователей?

BUGS:
-Фигуры могут "залезать" друг в друга с боковых сторон.
-Вылет игры при преждевременном нажатии клавишь управления(до появления фигуры
на поле). Решение: блоировать нажатие клавишь при x<0?
"""

IN_GAME = True #Продолжается ли игра
SEG_SIZE = 25 #Размер одного сегмента

#Игровой счёт
score = 0

#Набор используемых фигур
SHAPES = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
         [(0, -1), (-1, -1), (-1, 0), (0, 0)],
         [(-1, 0), (-1, 1), (0, 0), (0, -1)],
         [(0, 0), (-1, 0), (0, 1), (-1, -1)],
         [(0, 0), (0, -1), (0, 1), (-1, -1)],
         [(0, 0), (0, -1), (0, 1), (1, -1)],
         [(0, 0), (0, -1), (0, 1), (-1, 0)]]

#Позиции уже упавших фигур. 0 - свободная клетка, 1 - заполненная
shapes_positions = np.zeros((20,10))

#Координаты активной фигуры
active_shape_coords = []

#Флаг на наличие активной фигуры
active_shape = False


def create_segment(x,y,color = (0, 255, 0), thick = 1):
    """Создаёт квадрат размером в 1 сегмент
    в указанных координатах. Координаты указывать в пикселях."""
    cv2.rectangle(field, (x, y), (x+SEG_SIZE, y+SEG_SIZE),
    color, thickness=thick)


def create_shape(x, y, type, flag = True):
    """Создаёт серию квадратов по указанным координатам.
    Использовать в сочетании с SHAPES[N]."""
    color_1 = (255,255,255)
    color_2 = (0,0,0)

    if not flag:
        color_1 = (0,0,0)
        color_2 = (0,255,0)

    for segment in type:
        #Отрисовка самой фигуры
        create_segment(x*SEG_SIZE+segment[0]*SEG_SIZE,
                       y*SEG_SIZE+segment[1]*SEG_SIZE,
                       color_1, -1)
        if not active_shape:
            active_shape_coords.append(((x*SEG_SIZE+segment[0]*SEG_SIZE)//25,
                                    (y*SEG_SIZE+segment[1]*SEG_SIZE)//25,))
        #Отрисовка контуров клеток
        create_segment(x*SEG_SIZE+segment[0]*SEG_SIZE,
                       y*SEG_SIZE+segment[1]*SEG_SIZE,
                       color_2, 1)


def is_new_position_correct(coords, JustCheck=False):
    """Проверяет, возможно ли положение фигуры после
    поворота или перемещения."""
    global active_shape
    global active_shape_coords
    global min_line
    global shapes_positions

    max_x = 0
    #Неверное обозначение осей движения. Исправить.
    for yx in coords:
        y, x = yx[0], yx[1]
        if x > max_x:
            max_x = x

    #Некорректные значения?
    min_y = 0
    max_y = 9

    if num_type_acive_shape == 0:
        min_y += 1
    elif num_type_acive_shape in [1,2,3,4,6]:
        max_y += 1
    elif num_type_acive_shape == 5:
        min_y -= 1

    if y <= min_y or y >= max_y:
        return False

    if max_x > min_line:
        if not JustCheck:
            #Начало новой итерации
            update_shapes_positions(active_shape_coords)
            active_shape = False
            active_shape_coords = []
        return False

    #print(shapes_positions)
    #print(active_shape_coords)

    #Проверка, нет ли под фигурой другой фигуры
    #Теория. Координата 18 - нижняя точка. Координата х должна быть +1?
    #print(shapes_positions)
    for xy in active_shape_coords:
        x, y = xy[0], xy[1]
        #x = x + 2 #Смотри строку 151.
        #Блок смещений из функции записи в массив
        if num_type_acive_shape == 0:
            y = y + 1
            x = x + 1
        elif num_type_acive_shape == 1:
            y = y + 1
        elif num_type_acive_shape == 3:
            x = x - 1
        elif num_type_acive_shape == 4:
            x = x - 1
        elif num_type_acive_shape == 5:
            x = x + 1
        elif num_type_acive_shape == 6:
            y = y + 1
            x = x - 1
        #Непонятно, из-за чего возникает тип float. Пофиксить.
        x, y = int(x), int(y)
        #x = x - 2 #Смотри строку 133.
        #print(x,y)
        if y > 0:
            if shapes_positions[y][x] == 1:
                if not JustCheck:
                    print("Фигура обнаружена!")
                    #Начало новой итерации
                    update_shapes_positions(active_shape_coords)
                    active_shape = False
                    active_shape_coords = []
                return False
    return True


def move_shape(vector):
    """Перемещает активную фигуру вправо, влево или вниз."""
    global active_shape_coords
    new_active_shape_coords = []

    for coords in active_shape_coords:
        new_coords_x,new_coords_y = coords[0]+vector[0], coords[1]+vector[1]
        new_active_shape_coords.append((new_coords_x,new_coords_y))

    #Проверка на то, что новая позиция находится на игровом поле:
    if is_new_position_correct(new_active_shape_coords):
        #Стирание фигуры
        create_shape(active_shape_coords[-1][0],active_shape_coords[-1][1],
                 type_acive_shape,False)

                 #Получение координат после смещения
        active_shape_coords = new_active_shape_coords

        #Отображение фигуры на новом месте
        create_shape(active_shape_coords[-1][0],active_shape_coords[-1][1],
                 type_acive_shape)


def rotate_shape(rotation):
    """Поворачивает активную фигуру на 90 градусов
    влево или вправо. Не должна позволять фигуре выходить за границы."""
    global active_shape_coords
    global type_acive_shape
    new_coords = []

    #Этот блок кода используется три раза. Переделать в функцию.
    #Вид функции-get_x_y(coords,i). Возвращает координаты i-того сегмента.
    """
    for xy in active_shape_coords:
        x, y = xy[0], xy[1]

        #Блок смещений из функции записи в массив
        if num_type_acive_shape == 0:
            y = y + 1
            x = x + 1
        elif num_type_acive_shape == 1:
            y = y + 1
        elif num_type_acive_shape == 3:
            x = x - 1
        elif num_type_acive_shape == 4:
            x = x - 1
        elif num_type_acive_shape == 5:
            x = x + 1
        elif num_type_acive_shape == 6:
            y = y + 1
            x = x - 1"""

    #Рассчитать новый набор координат для каждого сегмента
    coords = active_shape_coords
    #new_coords = []

    shape = [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [0, 0, 0, 0]]

    #Заведомо нереалистичные значения
    min_x = 100
    min_y = 100

    for xy in coords:
        x, y = xy[0], xy[1]
        if x < min_x:
            min_x = x
        if y < min_y:
            min_y = y

    for xy in coords:
        x, y = xy[0], xy[1]
        new_x = x - min_x
        new_y = y - min_y
        new_coords.append((new_x, new_y))


    #print(new_coords)

    for xy in new_coords:
        x, y = xy[0], xy[1]
        shape[x][y] = 1

    ## WARNING:
    #type_acive_shape = shape

    my_shape = np.array(shape)
    my_shape = np.rot90(my_shape,k=1)
    new_coords = []

    for i in range(len(my_shape)):
        x = my_shape[i]
        for j in range(len(my_shape)):
            position = x[j]
            if position == 1:
                new_coords.append((i+min_x,j+min_y))



    print(active_shape_coords)
    print(new_coords)

    """Проверить, корректны ли новые координаты (Не залезают на другие фигуры
    и находятся в рамках игрового поля)
    """
    if is_new_position_correct(new_coords,JustCheck=True):
        #Если да, отрисовать фигуру по новым координатам и стереть по старым
        print("Поворот возможен!")
        #Стирание фигуры
        for xy in active_shape_coords:
            create_segment((xy[0]-1)*SEG_SIZE, xy[1]*SEG_SIZE,
            color=(0,0,0),thick=-1)
            create_segment((xy[0]-1)*SEG_SIZE, xy[1]*SEG_SIZE,
            color=(0,255,0),thick=1)

        #Получение координат после смещения
        active_shape_coords = new_coords
        #Отображение фигуры на новом месте
        print(new_coords)
        for xy in new_coords:
            create_segment(xy[0]*SEG_SIZE, xy[1]*SEG_SIZE,
            color=(255,255,255),thick=-1)
            create_segment(xy[0]*SEG_SIZE, xy[1]*SEG_SIZE,
            color=(0,0,0),thick=1)
    #В противном случае можно не делать ничего?

def update_shapes_positions(coords):
    """Обновляет массив shapes_positions, заполняя '1' клетки,
    занятые фигурами."""
    global shapes_positions
    global IN_GAME

    for xy in coords:
        x, y = xy[0], xy[1]
        y = y - 1
        if num_type_acive_shape == 0:
            y = y + 1
            x = x + 1
        elif num_type_acive_shape == 1:
            y = y + 1
        elif num_type_acive_shape == 3:
            x = x - 1
        elif num_type_acive_shape == 4:
            x = x - 1
        elif num_type_acive_shape == 5:
            x = x + 1
        elif num_type_acive_shape == 6:
            y = y + 1
            x = x - 1

        shapes_positions[y][x] = 1

    #print(num_type_acive_shape)
    #print(shapes_positions)

    if 1 in shapes_positions[0]:
        IN_GAME = False
        print(f"Игра окончена. Ваш счёт: {score}")

    for string in shapes_positions:
        if 0 not in string:
            update_field()


def update_field():
    """Вызывается при обнаружении полной строки из '1' в
    массиве shapes_positions, очищает строку, увеличивает счёт,
    опускает все закрашенные клетки ВЫШЕ строки на 1 клетку."""
    global score
    global shapes_positions
    score = score + 1
    #Удалить строку, полностью заполненную 1, добавить в начало пустую строку
    empty_arr = [0,0,0,0,0,0,0,0,0,0]
    for i in range(0, len(shapes_positions)):
        if 0 not in shapes_positions[i]:
            shapes_positions = np.delete(shapes_positions, i, axis = 0)
            shapes_positions = np.vstack([empty_arr, shapes_positions])

    #Отрисовать новое игровое поле в соответствии с 0 и 1 в shapes_positions
    for x in range(0, 10):
        for y in range(0, 20):
            if shapes_positions[y][x] == 1:
                create_segment(x*SEG_SIZE,
                               y*SEG_SIZE,
                               (255,255,255), -1)
                create_segment(x*SEG_SIZE,
                               y*SEG_SIZE,
                               (0,0,0), 1)
            else:
                create_segment(x*SEG_SIZE,
                               y*SEG_SIZE,
                               (0,0,0), -1)
                create_segment(x*SEG_SIZE,
                               y*SEG_SIZE,
                               (0,255,0), 1)

#-------------------------------------------------------------------------------
field = np.zeros((SEG_SIZE*20+1, SEG_SIZE*10+1, 3), dtype = 'uint8')
#Разметка игрового поля на сегменты
for x in range(10):
    for y in range(20):
        create_segment(x*SEG_SIZE,y*SEG_SIZE)


while IN_GAME:
    if not active_shape:
        #Создание фигуры
        num_type_acive_shape = random.randint(0,6)
        #num_type_acive_shape = 3

        #Корректировка нижней границы для некоторых фигур
        if num_type_acive_shape in [0, 1, 6]:
            min_line = 19
        else:
            min_line = 20

        type_acive_shape = SHAPES[num_type_acive_shape]
        create_shape(5,-2,type_acive_shape)
        active_shape = True

    #Падение фигуры вниз
    move_shape((0,1))

    #Отображение окна. Переместить вниз?
    cv2.imshow('Tetris v0.1.7', field)

    key = cv2.waitKey(750)

    #Перемещение фигуры вправо и влево
    if key == 226 or key == 100:
        move_shape((1,0))
    elif key == 244 or key == 97:
        move_shape((-1,0))

    #Вращение фигуры
    #q-key
    elif key == 113 or key == 233:
        rotate_shape(1)
    #e-key
    elif key == 101 or key == 243:
        rotate_shape(-1)

    #b-key
    elif key == 98 or key == 232:
        break


#cv2.destroyAllWindows()
