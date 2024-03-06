"""
Постановка задачи:
-Отрисовать игровое поле. Прямогуольник 10х20. Расчертить на клетки.
-Создать фигуры. (Упростить? 3-4 фигуры?).
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
-Реализовать сдвиг сегмента влево-вправо;
-Реализовать "падение" сегментов;
-Реализовать ичезновение при сборе ряда(по цвету пикселей??);
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


def is_new_position_correct():
    """Проверяет, возможно ли положение фигуры после
    поворота или перемещения."""


def move_shape(vector):
    """Перемещает активную фигуру вправо, влево или вниз."""
    global active_shape_coords
    new_active_shape_coords = []

    for coords in active_shape_coords:
        new_coords_x,new_coords_y = coords[0]+vector[0], coords[1]+vector[1]
        new_active_shape_coords.append((new_coords_x,new_coords_y))

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


#-------------------------------------------------------------------------------
#Захват клавиш



#Создание поля для игры
field = np.zeros((SEG_SIZE*20+1, SEG_SIZE*10+1, 3), dtype = 'uint8')
#Разметка игрового поля на сегменты
for x in range(10):
    for y in range(20):
        create_segment(x*SEG_SIZE,y*SEG_SIZE)


i = 0
while True:
    if not active_shape:
        #Создание фигуры
        type_acive_shape = SHAPES[random.randint(0,6)]
        create_shape(5,0,type_acive_shape)
        active_shape = True

    #Падение фигуры вниз
    move_shape((0,1))

    print(active_shape_coords[-1])
    print(type_acive_shape)

    cv2.imshow('Tetris v0.0.1', field)
    cv2.waitKey(1000)
    i += 1
    if i == 10:
        break

cv2.destroyAllWindows()
