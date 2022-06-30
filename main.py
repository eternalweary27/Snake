from datetime import datetime
import random
import pygame
pygame.init()


class Colours:
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    GREY = (25,25,25)
    RED = (200,0,0)
    GREEN = (0,200,0)
    BLUE = (0,0,200)
    CYAN = (0,206,209)
    PURPLE = (148,0,211)
    YELLOW = (255,255,0)
    DARK_GREEN = (0,100,0)

class Snake:
    def __init__(self,window,square_size,colour):
        self.window = window
        self.win_x = window.get_width()
        self.win_y = window.get_height()
        self.square_size = square_size
        self.colour = colour 
        self.initial_len = SNAKE_INITIAL
        self.vel = (1,0)
        self.points = 0
        self.snake_arr = self.createSnake()
        self.dead = False

    def createSnake(self):
        snake_arr = []
        start_pos = (self.win_x / 2, self.win_y / 2)
        for i in range(0,self.initial_len):
            snake_arr.append((start_pos[0] + self.square_size, start_pos[1]))
        return snake_arr
    
    def updatePos(self):
        sx = self.vel[0] * self.square_size
        sy = self.vel[1] * self.square_size
        curr_head = self.snake_arr[-1]
        new_head_x = (curr_head[0] + sx) % self.win_x
        new_head_y = (curr_head[1] + sy) % self.win_y
        self.snake_arr.append((new_head_x,new_head_y))
        self.snake_arr.pop(0)

    def updateLife(self):
        head = self.snake_arr[-1]
        if head in self.snake_arr[0:-1]:
            self.dead = True
            return
    
    def foodOverlapping(self,food):
        for coord in self.snake_arr:
            nx = max(min(coord[0] + self.square_size,food.x),coord[0])
            ny = max(min(coord[1] + self.square_size,food.y),coord[1])
            distance = (food.x - nx)**2 + (food.y - ny)**2
            if distance < food.radius**2:
                return True
        return False
                
    def eatFood(self,food):
        if not self.foodOverlapping(food):
            return

        if food.points < 0:
            reduction = abs(food.points)
            if len(self.snake_arr) > reduction:
                for i in range(0,reduction):
                    self.snake_arr.pop(0)
        else: 
            for i in range(0,food.points):
                tail = self.snake_arr[0]
                sx = self.vel[0] * self.square_size
                sy = self.vel[1] * self.square_size
                newtail_x = (tail[0] - sx) % self.win_x
                newtail_y = (tail[1] - sy) % self.win_y
                self.snake_arr.insert(0,(newtail_x,newtail_y))
        self.points += abs(food.points)
    
    def move(self,keys_pressed):
        vel_right = (1,0)
        vel_left = (-1,0)
        vel_up = (0,-1)
        vel_down = (0,1)

        if keys_pressed[pygame.K_RIGHT] and self.vel != vel_left:
            self.vel = vel_right
        
        if keys_pressed[pygame.K_LEFT] and self.vel != vel_right:
            self.vel = vel_left
        
        if keys_pressed[pygame.K_UP] and self.vel != vel_down:
            self.vel = vel_up
        
        if keys_pressed[pygame.K_DOWN] and self.vel != vel_up:
            self.vel = vel_down
    
        self.updatePos()
    
    def AIControl(self,food):
        pass
        

    def returnHeadColour(self):
        r = 0.5 * self.colour[0]
        g = 0.5 * self.colour[1]
        b = 0.5 * self.colour[2]
        return (r,g,b)
    
    def reset(self):
        self.vel = (1,0)
        self.points = 0
        self.snake_arr = self.createSnake()
        self.dead = False
    
    def draw(self):
        head_colour = self.returnHeadColour()
        for coord in self.snake_arr:
            if coord == self.snake_arr[-1]:
                block_colour = head_colour
            else:
                block_colour = self.colour
            pygame.draw.rect(self.window,head_colour,(coord[0],coord[1],self.square_size,self.square_size))
            pygame.draw.rect(self.window,block_colour,(coord[0],coord[1],self.square_size-1,self.square_size-1))


class Food:
    def __init__(self,window,x,y,radius,colour,points):
        self.window = window
        self.x = x
        self.y = y
        self.radius = radius
        self.colour = colour
        self.points = points

    def draw(self):
        pygame.draw.circle(self.window,self.colour,(self.x,self.y),self.radius)



class Game:
    def __init__(self,win_x,win_y):
        self.win_x = win_x
        self.win_y = win_y
        self.window = pygame.display.set_mode((win_x,win_y))

        self.snake = Snake(self.window,SQUARE_SIZE,SNAKE_COLOUR)
        self.eat_sound = pygame.mixer.Sound("eat_sound.wav")
        self.crash_sound = pygame.mixer.Sound("crash_sound.wav")

        self.food_eaten = True
        self.food = None

        self.fps = FPS
        self.paused = False
    
    def genFood(self):
        if not self.food_eaten:
            return
        print(len(self.snake.snake_arr))
        pygame.mixer.Sound.play(self.eat_sound)
        food_r = FOOD_RADIUS
        food_x = random.uniform(food_r, self.win_x - food_r)
        food_y = random.uniform(food_r, self.win_y - food_r)
        food_points = random.choice([-1,1,3])

        prob = random.randint(1,10)
        if 0 <= prob <= 8:
            food_colour = Colours.CYAN
            food_points = 1
        
        if prob == 9:
            food_colour = Colours.YELLOW
            food_points = -1
        
        if prob == 10:
            food_colour = Colours.PURPLE
            food_points = 3

        food_obj = Food(self.window,food_x,food_y,food_r,food_colour,food_points)
        self.food = food_obj
        self.food_eaten = False

    

    def displayCurrScore(self):
        font = pygame.font.SysFont("Consolas",20,True)
        score_str = "Score: {}".format(self.snake.points)
        score_surf = font.render(score_str,False,Colours.RED)
        score_rect = score_surf.get_rect()
        score_rect.center = (self.win_x * 0.5, self.win_y * 0.1)
        self.window.blit(score_surf,score_rect)

    def displayGameOver(self):
        pygame.time.delay(500)
        font = pygame.font.SysFont("Consolas",30,True)
        gamover_str = "You Crashed! Score: {}".format(self.snake.points)
        gameover_surf = font.render(gamover_str,False,Colours.RED)
        gameover_rect = gameover_surf.get_rect()
        gameover_rect.center = (self.win_x / 2, self.win_y / 2)
        self.window.blit(gameover_surf,gameover_rect)
        pygame.display.update()
        pygame.time.delay(1000)
    
    def displayPauseScreen(self):
        self.snake.draw()
        self.food.draw()
        pause_surf = pygame.font.SysFont("Consolas",30,True).render("Paused",False,Colours.RED)
        pause_surf_rect = pause_surf.get_rect()
        pause_surf_rect.center = (self.win_x / 2, self.win_y / 2)
        self.window.blit(pause_surf,pause_surf_rect)
    
    def reset(self):
        self.snake.reset()
        self.food_eaten = True

    def saveScore(self):
        with open("scores.txt", mode = "a", encoding = "utf-8") as file:
            curr_date = datetime.today().strftime('%Y-%m-%d')
            write_str = "Date:{}, Score: {}".format(curr_date,self.snake.points)
            file.write(write_str)
            file.write("\n")
            file.close()
        print("Score saved")
    
    def startGame(self):
        clock = pygame.time.Clock()
        quit_game = False
        last_hit = None
        while not quit_game:
            clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game = True
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused

            if self.paused:
                self.displayPauseScreen()
            else:
                
                self.genFood()
                self.food.draw()
                self.snake.eatFood(self.food)
                if self.snake.foodOverlapping(self.food):
                    self.food_eaten = True

                keys_pressed = pygame.key.get_pressed()
                self.snake.move(keys_pressed)
                self.snake.updateLife()
                if self.snake.dead:
                    pygame.mixer.Sound.play(self.crash_sound)
                    self.displayGameOver()
                    self.saveScore()
                    self.reset()
                else:
                    self.snake.draw()
                self.displayCurrScore()
                    
            pygame.display.update()
            self.window.fill(Colours.BLACK)
        pygame.quit()
        print("Program exited.")



WIN_X = 400
WIN_Y = 300

SNAKE_INITIAL = 4
SNAKE_COLOUR = Colours.GREEN
SQUARE_SIZE = 10

FOOD_RADIUS = 8

FPS = 20

def main():
    g = Game(WIN_X,WIN_Y)
    g.startGame()

if __name__ == "__main__":
    main()
