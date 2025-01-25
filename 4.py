from pygame import *
from random import randint
import time as pytime

# фонова музика
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')
 
# шрифти і написи
font.init()
font1 = font.Font(None, 80)
font2 = font.Font(None, 36)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))

# нам потрібні такі картинки:
img_back = "galaxy.jpg"  # фон гри
img_hero = "rocket.png"  # герой
img_bullet = "bullet.png" # куля
img_enemy = "ufo.png"  # ворог

clock = time.Clock()
FPS = 30
 
score = 0  # збито кораблів
goal = 50 # стільки кораблів потрібно збити для перемоги
lost = 0  # пропущено кораблів
max_lost = 3 # програли, якщо пропустили стільки
life = 3
bullet_count = 10
reload_start_time = None

# клас-батько для інших спрайтів
class GameSprite(sprite.Sprite):
    # конструктор класу
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # викликаємо конструктор класу (Sprite):
        super().__init__()
 
        # кожен спрайт повинен зберігати властивість image - зображення
        self.image = transform.scale(
            image.load(player_image), (size_x, size_y))
        self.speed = player_speed
 
        # кожен спрайт повинен зберігати властивість rect - прямокутник, в який він вписаний
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
 
    # метод, що малює героя у вікні
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# клас спрайта-кулі   
class Bullet(GameSprite):
    # рух ворога
    def update(self):
        self.rect.y += self.speed
        # зникає, якщо дійде до краю екрана
        if self.rect.y < 0:
            self.kill()

# клас головного гравця
class Player(GameSprite):
    # метод для керування спрайтом стрілками клавіатури
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
 
    # метод "постріл" (використовуємо місце гравця, щоб створити там кулю)
    def fire(self):
        bullet = Bullet(
            img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15
        )
        bullets.add(bullet)
 
# клас спрайта-ворога
class Enemy(GameSprite):
    # рух ворога
    def update(self):
        self.rect.y += self.speed
        global lost
        # зникає, якщо дійде до краю екрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost = lost + 1

# створюємо віконце
win_width = 700
win_height = 800
display.set_caption("Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))
 
# створюємо спрайти
ship = Player(img_hero, 5, win_height - 100, 80, 100, 5)
 
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(
        80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)
 
bullets = sprite.Group()

# змінна "гра закінчилася": як тільки вона стає True, в основному циклі перестають працювати спрайти
finish = False
# Основний цикл гри:
run = True  # прапорець скидається кнопкою закриття вікна
 
while run:
    # подія натискання на кнопку Закрити
    for e in event.get():
        if e.type == QUIT:
            run = False
        #подія натискання на пробіл - спрайт стріляє
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and bullet_count > 0 and reload_start_time is None:
                bullet_count -= 1
                fire_sound.play()
                ship.fire()
    
    # сама гра: дії спрайтів, перевірка правил гри, перемальовка
    if not finish:
        # оновлюємо фон
        window.blit(background, (0, 0))
 
        # пишемо текст на екрані
        text = font2.render("Рахунок: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))
 
        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        # рухи спрайтів
        ship.update()
        monsters.update()
        bullets.update()

        # оновлюємо їх у новому місці при кожній ітерації циклу
        ship.reset()
        monsters.draw(window)
        bullets.draw(window)

        if bullet_count == 0 and reload_start_time is None:
            reload_start_time = pytime.time()  # Починаємо відлік часу перезарядки

        if reload_start_time:
            if pytime.time() - reload_start_time > 3:  # Чекаємо 3 секунди
                bullet_count = 10  # Повертаємо кулі
                reload_start_time = None  # Скидаємо таймер

        # перевірка зіткнення кулі та монстрів (і монстр, і куля при зіткненні зникають)
        collides = sprite.groupcollide(monsters, bullets, True, True)
        for collide in collides:
            # цей цикл повториться стільки разів, скільки монстрів збито
            score = score + 1
            monster = Enemy(
                img_enemy, 
                randint(80, win_width - 80), -40, 80, 50, randint(1, 5)
            )
            monsters.add(monster)

        if sprite.spritecollide(ship, monsters, True):
            life -= 1
            monster = Enemy(
                img_enemy, 
                randint(80, win_width - 80), -40, 80, 50, randint(1, 5)
            )
            monsters.add(monster)

        text_life = font1.render(str(life), 1, (255, 0, 0))
        window.blit(text_life, (650, 10)) 

        # можливий програш: пропустили занадто багато або герой зіткнувся з ворогом
        if life == 0 or lost >= max_lost:
            finish = True # програли, ставимо тло і більше не керуємо спрайтами.
            mixer.music.stop()
            window.blit(lose, (200, 200))
            
        # перевірка виграшу: скільки очок набрали?
        if score >= goal:
            finish = True
            mixer.music.stop()
            window.blit(win, (200, 200))

    display.update()
    clock.tick(FPS)
