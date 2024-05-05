import random

class SnakeGame:
    def __init__(self):
        self.snake_position = [100, 100]
        self.snake_body = [[100, 100], [90, 100], [80, 100], [70, 100]]
        self.food_position = [random.randrange(1, 50) * 10, random.randrange(1, 50) * 10]
        self.food_spawn = True
        self.direction = 'RIGHT'

    def game_over(self):
        return self.snake_position in self.snake_body

    def eat(self):
        if self.snake_position == self.food_position:
            self.snake_body.insert(0, list(self.snake_position))
            self.food_spawn = False
        else:
            self.snake_body.insert(0, list(self.snake_position))
            self.snake_body.pop()

    def validate_direction(self, direction):
        opposite_direction = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
        return opposite_direction[direction] != self.direction

    def change_direction(self, direction):
        if self.validate_direction(direction):
            self.direction = direction

    def update(self):
        if self.direction == 'UP':
            self.snake_position[1] -= 10
        elif self.direction == 'DOWN':
            self.snake_position[1] += 10
        elif self.direction == 'LEFT':
            self.snake_position[0] -= 10
        elif self.direction == 'RIGHT':
            self.snake_position[0] += 10
        self.snake_body.insert(0, list(self.snake_position))
        if self.snake_position == self.food_position:
            self.eat()
            self.food_spawn = False
        else:
            self.snake_body.pop()
        if self.game_over():
            print('Game Over!')</p>

    def run_game(self):
        while True:
            self.update()
            if self.game_over():
                break

if __name__ == '__main__':
    game = SnakeGame()
    game.run_game()