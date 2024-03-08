"""
Постановка задачи:
-Отрисовать игровое поле. Прямогуольник 10х20. Расчертить на клетки.+
-Создать фигуры. (Упростить? 3-4 фигуры?).+
    -Фигуры должны поворачиваться на 90 градусов по команде игрока.
    Влево и вправо. Так же необходимо иметь возможность ускоренно
    перемещать их вниз.
-Рандомная фигура появляется в верхней позиции, после чего начинает
движение вниз до тех пор, пока под каждым блоком снизу есть свободное место.
-При касании фигуры нижнего ряда или другой фигуры её позиция сохраняется,
фигура останавливается.
-При заполнении ряда удалять все сегменты в ряду, увеличивать счёт.
-Опционально: увеличивать скорость за каждые несколько заполненных рядов.
"""
import cv2
import random
import numpy as np

"""
TODO:
-Реализовать сдвиг сегмента влево-вправо;+
-Реализовать "падение" сегментов;+
-Реализовать ичезновение при сборе ряда;
-Реализовать вращение фигур;

Фичи:
-Настройка сложности?
-Ускорение игры со временем?
-Запоминание рекорда?
"""

IN_GAME = True #Продолжается ли игра
SEG_SIZE = 25 #Размер одного сегмента

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


def is_new_position_correct(coords):
    """Проверяет, возможно ли положение фигуры после
    поворота или перемещения."""
    global active_shape
    global active_shape_coords
    global min_line
    global shapes_positions
    
    max_x = 0
    for yx in coords:
        y, x = yx[0], yx[1]
        if x > max_x:
            max_x = x
    #print(max_x)

    if max_x > min_line:
        #print(active_shape_coords)
        update_shapes_positions(active_shape_coords)
        active_shape = False
        active_shape_coords = []
        return False
    #print("***", x, y)
    return True



def move_shape(vector):
    """Перемещает активную фигуру вправо, влево или вниз."""
    global active_shape_coords
    new_active_shape_coords = []

    for coords in active_shape_coords:
        new_coords_x,new_coords_y = coords[0]+vector[0], coords[1]+vector[1]
        new_active_shape_coords.append((new_coords_x,new_coords_y))


    if is_new_position_correct(new_active_shape_coords):
        #Стирание фигуры
        create_shape(active_shape_coords[-1][0],active_shape_coords[-1][1],
                 type_acive_shape,False)

                 #Получение координат после смещения
        active_shape_coords = new_active_shape_coords

        #Отображение фигуры на новом месте
        create_shape(active_shape_coords[-1][0],active_shape_coords[-1][1],
                 type_acive_shape)



def rotate_shape():
    """Поворачивает активную фигуру на 90 градусов
    влево или вправо. Не должна позволять фигуре выходить за границы."""
    pass


def update_shapes_positions(coords):
    """Обновляет массив shapes_positions, заполняя '1' клетки,
    занятые фигурами."""
    global shapes_positions
    print(coords)
    print(min_line)
    for xy in coords:
        x, y = xy[0], xy[1]
        x = x - 1
        if min_line == 20:
            y = y - 1
        shapes_positions[y][x] = 1
    print(shapes_positions)



def update_field():
    """Вызывается при обнаружении полной строки из '1' в
    массиве shapes_positions, очищает строку, увеличивает счёт,
    опускает все закрашенные клетки ВЫШЕ строки на 1 клетку."""
    pass


#-------------------------------------------------------------------------------
#Захват клавиш



#Создание поля для игры
field = np.zeros((SEG_SIZE*20+1, SEG_SIZE*10+1, 3), dtype = 'uint8')
#Разметка игрового поля на сегменты
for x in range(10):
    for y in range(20):
        create_segment(x*SEG_SIZE,y*SEG_SIZE)


i = 0
while IN_GAME:
    if not active_shape:
        #Создание фигуры
        type_acive_shape = random.randint(0,6)
        if type_acive_shape in [0, 1, 6]:
            #Корректировка для некоторых фигур ввиду их особенностей
            min_line = 19
        else:
            min_line = 20
        type_acive_shape = SHAPES[type_acive_shape]
        create_shape(5,-4,type_acive_shape)
        active_shape = True

    #Падение фигуры вниз
    move_shape((0,1))

    #print(active_shape_coords[-1])
    #print(type_acive_shape)

    cv2.imshow('Tetris v0.0.1', field)
    key = cv2.waitKey(1000)
    #print(key)
    i += 1

    #Перемещение фигуры вправо и влево
    if key == 226 or key == 100:
        move_shape((1,0))
    elif key == 244 or key == 97:
        move_shape((-1,0))

    #Вращение фигуры
    #q-key
    elif key == 113 or key == 233:
        rotate_shape()
    #e-key
    elif key == 101 or key == 243:
        rotate_shape()

    elif key == 98 or key == 232:
        break

    #Тестирование новых фигур на доске
    #if i == 20:
        #i = 0
        #active_shape = False


#cv2.destroyAllWindows()
