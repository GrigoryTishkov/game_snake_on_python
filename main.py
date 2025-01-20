from tkinter import *
from tkinter import messagebox
from random import *
from enum import *
import platform
import os


class Constant(Enum):
    # Размеры змейки и еды
    ELEMENT_SNAKE = 20
    SIZE_FOOD = 20
    # Размеры окна 
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    CONTENT_WIDTH = 320
    CONTENT_HEIGHT = 320
    # Параметры нужны для того, чтобы разбить поле на квадраты, по которым будет ползать наша змейка
    GRID_WIDTH = WINDOW_WIDTH // ELEMENT_SNAKE  # Ширина квадратика игрового поля
    GRID_HEIGHT = WINDOW_HEIGHT // ELEMENT_SNAKE  # Длина квадратика игрового поля
    # Цвета игры
    BG_COLOR = "#9ACD32"
    FOOD_COLOR = "#FF69B4"
    SNAKE_COLOR = "#2F4F4F"
    GM_NORMAL = "Обычный"
    GM_WITHOUT_WALL = "Без стен"
    TXT = f'''Игра змейка \nПозволяет: \nКлавиши программы: \n
WASD - Управление змейкой\n
Управление скоростью змейки: \n"+" - увеличивает скорость\n"-" - уменьшает скорость\n
Выбор режима игры:\n"N" - Игра со стенами\n"M" - Игра без стен\n
"P" - Пауза
F1 - Вызов справки по программе, \nCtrl + X - Выход из программы.'''


class GameSnake:
    def __init__(self, window):
        self.window = window
        self.window.title("ИГРА ЗМЕЙКА")
        self.window.resizable(False, False)
        self.windows_version = self.get_windows_version()
        self.state_value = 12 if self.windows_version == "Windows 10" else 4
        self.snake = Snake()
        self.food = Food(self)
        self.save_score = self.load_scorefile()
        self.moving_game_id = None
        self.game_mode = None
        self.status = None
        self.canvas = Canvas(window, width=Constant.WINDOW_WIDTH.value, height=Constant.WINDOW_HEIGHT.value,
                             bg=str(Constant.BG_COLOR.value))
        self.canvas.pack()

        self.snake_speed = 10
        self.menu_bar()
        self.status_bar()
        self.show_mode_selection()
        self.window.bind("<KeyPress>", self.bind_buttons)

    def get_windows_version(self):  # Получение версии windows так как на Win 10 кнопка Ctrl соответствует event.state
        # == 12, в то время как на Win 11 соответствует 4
        version = platform.version()
        if version >= '10.0.22000':
            return "Windows 11"
        elif version.startswith('10.'):
            return "Windows 10"

    def show_mode_selection(self):  # Функция показывает кнопки выбора режима перед началом игры
        self.canvas.create_text(Constant.WINDOW_WIDTH.value // 2, Constant.WINDOW_HEIGHT.value // 2 - 20,
                                font="Arial 14", text="Выберите режим игры:", fill="white")

        button_normal = Button(self.window, text="Обычный",
                               command=lambda: self.set_game_mode(Constant.GM_NORMAL.value))
        button_normal_window = self.canvas.create_window(Constant.WINDOW_WIDTH.value // 2,
                                                         Constant.WINDOW_HEIGHT.value // 2 + 20, window=button_normal)

        button_without_wall = Button(self.window, text="Без стен",
                                     command=lambda: self.set_game_mode(Constant.GM_WITHOUT_WALL.value))
        button_without_wall_window = self.canvas.create_window(Constant.WINDOW_WIDTH.value // 2,
                                                               Constant.WINDOW_HEIGHT.value // 2 + 60,
                                                               window=button_without_wall)

    def set_game_mode(self, mode):  # Установка соответствующего режима игры
        self.game_mode = mode
        self.reload_game()

    def start_game(self):  # Функция старта игры, в которой задаются начальные параметры
        if self.game_mode is None:
            return
        self.snake = Snake()
        self.food = Food(self)
        self.snake_speed = 10
        self.snake.score = 0
        self.running = True
        self.save_score = self.load_scorefile()
        # self.window.bind("<KeyPress>", self.bind_buttons)
        self.moving_game()

    def moving_game(self):  # Цикл движения змейки и пересоздания еды
        if self.running:
            if self.game_mode == Constant.GM_NORMAL.value:
                self.snake.move()
            elif self.game_mode == Constant.GM_WITHOUT_WALL.value:
                self.snake.move_without_wall()
            self.update_status_bar()
            if self.snake.check_food_collision(self.food):
                self.snake.add_element()
                self.food.reposition_food()
                if self.snake.score > self.save_score:
                    self.save_score = self.snake.score
                    self.save_scorefile()
                    self.update_status_bar()
            if self.game_mode == Constant.GM_NORMAL.value and self.snake.check_wall_collision() \
                    or self.snake.check_self_collision():
                self.running = False
            elif self.game_mode == Constant.GM_WITHOUT_WALL.value and self.snake.check_self_collision():
                self.running = False
            self.draw()
            self.moving_game_id = self.window.after(1000 // self.snake_speed, self.moving_game)
        else:
            self.game_over()

    def draw_square(self, x, y, width, height, color):
        self.canvas.create_rectangle(
            x * width,
            y * height,
            (x + 1) * width,
            (y + 1) * height,
            fill=color
        )

    def draw(self):
        self.canvas.delete(ALL)
        for element in self.snake.body:
            x, y = element
            self.draw_square(x, y, Constant.ELEMENT_SNAKE.value, Constant.ELEMENT_SNAKE.value,
                             Constant.SNAKE_COLOR.value)
        food_x, food_y = self.food.food_position
        self.draw_square(food_x, food_y, Constant.SIZE_FOOD.value, Constant.SIZE_FOOD.value, Constant.FOOD_COLOR.value)

    def bind_buttons(self, event):
        if event.keysym.lower() == "w" or event.char.lower() == "ц":
            self.snake.change_position(0, -1)
        if event.keysym.lower() == "a" or event.char.lower() == "ф":
            self.snake.change_position(-1, 0)
        if event.keysym.lower() == "s" or event.char.lower() == "ы":
            self.snake.change_position(0, 1)
        if event.keysym.lower() == "d" or event.char.lower() == "в":
            self.snake.change_position(1, 0)
        if event.keycode == 88 and event.state == self.state_value:  # Закрытие игры
            self.close_game()
        if event.keycode == 82 and event.state == self.state_value:  # Перезагрузка игры
            self.reload_game()
        if event.keysym == "F1":
            self.about_program()
        if event.keysym == 'KP_Add' or event.keysym == 'plus':
            self.speed('+')
        if event.keysym == 'KP_Subtract' or event.keysym == 'minus':
            self.speed('-')
        if event.keycode == 80:
            self.pause()
        if event.keycode == 77:
            self.set_game_mode(Constant.GM_WITHOUT_WALL.value)
        if event.keycode == 78:
            self.set_game_mode(Constant.GM_NORMAL.value)

    def speed(self, key):  # Функция задает скорость движения змейки
        if key == '+' and self.snake_speed >= 1 and self.snake_speed < 20:
            self.snake_speed += 1
            print(self.snake_speed)
        elif key == '-' and self.snake_speed > 1 and self.snake_speed <= 20:
            self.snake_speed -= 1
            print(self.snake_speed)

    def pause(self):
        if self.moving_game_id is not None:
            self.window.after_cancel(self.moving_game_id)
            self.moving_game_id = None
        elif self.moving_game_id is None:
            self.moving_game_id = self.window.after(1000 // self.snake_speed, self.moving_game)

    def game_over(self):
        self.canvas.delete(ALL)
        self.canvas.create_text(Constant.WINDOW_WIDTH.value // 2, Constant.WINDOW_HEIGHT.value // 2, font="Arial 14",
                                text="GAME OVER", fill="white")

    def reload_game(self):
        if self.moving_game_id is not None:
            self.window.after_cancel(self.moving_game_id)
            self.moving_game_id = None
        self.start_game()

    @staticmethod
    def load_scorefile():  # Загрузка счета змейки
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", encoding="UTF-8") as file:
                return int(file.read().strip())
        else:
            with open("highscore.txt", "w", encoding="UTF-8") as file:
                file.write("0")
                return 0

    def save_scorefile(self):  # Запись счета змейки
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "w", encoding="UTF-8") as file:
                file.write(str(self.snake.score))

    def menu_bar(self):
        menubar = Menu(self.window)
        self.window.config(menu=menubar)
        fondmenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Фонд", menu=fondmenu)
        fondmenu.add_command(label="Рестарт", accelerator="Ctrl + R", command=self.reload_game)
        fondmenu.add_command(label="Пауза", accelerator="P", command=self.pause)
        fondmenu.add_separator()
        fondmenu.add_command(label="Выход", accelerator="Ctrl + X", command=self.close_game)
        gamemodemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Режим игры", menu=gamemodemenu)
        gamemodemenu.add_command(label="Обычный", accelerator="N",
                                 command=lambda: self.set_game_mode(Constant.GM_NORMAL.value))
        gamemodemenu.add_command(label="Без стен", accelerator="M",
                                 command=lambda: self.set_game_mode(Constant.GM_WITHOUT_WALL.value))
        referencemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=referencemenu)
        referencemenu.add_command(label="Управление", command=self.content)
        referencemenu.add_separator()
        referencemenu.add_command(label="О программе", accelerator='F1', command=self.about_program)

    def close_game(self):
        self.window.quit()

    def content(self):
        content_window = Toplevel(self.window)
        content_window.title("Управление")
        content_window.geometry(f'{Constant.CONTENT_WIDTH.value}x{Constant.CONTENT_HEIGHT.value}')
        content_window.resizable(FALSE, FALSE)
        Label(content_window, text=Constant.TXT.value, justify=LEFT).place(x=0, y=0)
        Button(content_window, text="Выход", command=content_window.destroy).pack(side=BOTTOM, anchor=SE, padx=10,
                                                                                  pady=10)

    @staticmethod
    def about_program():
        messagebox.showinfo("О программе",
                            'Игра змейка"' "\n(c) Tishkov G.V., Russia, 2025")

    def status_bar(self):
        self.status = Label(
            text=f' Счет: {self.snake.score}  |  Рекорд:  {self.save_score}  |   F1 - Справка   |  Ctrl + R - Рестарт '
                 f' | Ctrl + X - Выход  |  Режим Игры: Не Установлен',
            bd=1, relief=SUNKEN, anchor=W, bg='#38a3a5', fg='#132a13')
        self.status.pack(side=BOTTOM, fill=X)

    def update_status_bar(self):
        if self.status:
            self.status.config(
                text=f' Счет: {self.snake.score}  |  Рекорд:  {self.save_score}  |   F1 - Справка  '
                     f' |  Ctrl + R - Рестарт  | Ctrl + X - Выход  |  Режим Игры: {self.game_mode}')


class Snake:
    def __init__(self):
        self.body = [(Constant.GRID_WIDTH.value // 2, Constant.GRID_HEIGHT.value // 2)]
        self.position = None
        self.grow = False
        self.score = 0

    def move(self):  # Движение змейки в игре со стенами
        if self.position is not None:
            head_x, head_y = self.body[0]
            pos_x, pos_y = self.position
            new_head = head_x + pos_x, head_y + pos_y
            self.body.insert(0, new_head)
            self.body.pop()

    def move_without_wall(self):
        if self.position is not None:
            head_x, head_y = self.body[0]
            pos_x, pos_y = self.position
            new_head = head_x + pos_x, head_y + pos_y

            if new_head[0] < 0:
                new_head = Constant.GRID_WIDTH.value - 1, new_head[1]
            elif new_head[0] >= Constant.GRID_WIDTH.value:
                new_head = 0, new_head[1]
            elif new_head[1] < 0:
                new_head = new_head[0], Constant.GRID_HEIGHT.value - 1
            elif new_head[1] >= Constant.GRID_HEIGHT.value:
                new_head = new_head[0], 0

            self.body.insert(0, new_head)
            self.body.pop()

    def change_position(self, x, y):  # Изменение позиции змейки на экране по векторам
        if self.position is None:
            self.position = (x, y)
        elif (x, y) != (-self.position[0], -self.position[1]):
            self.position = (x, y)

    def add_element(self):
        self.body.append(self.body[-1])
        self.move()

    def check_wall_collision(self):
        head_x, head_y = self.body[0]
        return head_x < 0 or head_x >= Constant.GRID_WIDTH.value or head_y < 0 or head_y >= Constant.GRID_HEIGHT.value

    def check_food_collision(self, food):
        if self.body[0] == food.food_position:
            self.score += 1
            return True
        return False

    def check_self_collision(self):
        return self.body[0] in self.body[1:]


class Food:
    def __init__(self, game):
        self.game = game
        self.food_position = self.reposition()

    def reposition(self):
        while True:
            position = (randint(0, Constant.GRID_WIDTH.value - 1), randint(0, Constant.GRID_HEIGHT.value - 1))
            if position not in self.game.snake.body:
                return position

    def reposition_food(self):
        self.food_position = self.reposition()


if __name__ == '__main__':
    root = Tk()
    game = GameSnake(root)
    root.mainloop()
