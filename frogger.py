import turtle as trtl
import time


SCREEN_WIDTH = 750
SCREEN_HEIGHT = 400
TOP = SCREEN_HEIGHT / 2
BOTTOM = -SCREEN_HEIGHT / 2
LEFTSIDE = -SCREEN_WIDTH / 2
RIGHTSIDE = SCREEN_WIDTH / 2

STARTINGROWS = 2
#NOTE Difficulty of completing all rounds is primarily controlled by these 3 variables: 
MAXROWS = 5  #Don't set lower than STARTINGROWS
LIVES = 5
DEFAULT_SPACING = 100  

ROWHEIGHT = 40 
RIGHT = 0
LEFT = 180

#NOTE 20x20 pixels is recommended size for the frogger and traffic(turtle) shapes
FROGGER_UP = "frogger_up.gif"
FROGGER_DOWN = "frogger_down.gif"
FROGGER_RIGHT = "frogger_right.gif"
FROGGER_LEFT = "frogger_left.gif"
SPLATTED_FROGGER_SHAPE = "skull.gif"
FROGGER_STARTING_HEIGHT = BOTTOM + 35

screen = trtl.Screen()
screen.setup(width=SCREEN_WIDTH, height=400)
screen.bgcolor("black")
screen.title("FROGGER!  by Paul Poling")
screen.tracer(0) 
screen.addshape(FROGGER_UP)
screen.addshape(FROGGER_DOWN)
screen.addshape(FROGGER_RIGHT)
screen.addshape(FROGGER_LEFT)
screen.addshape(SPLATTED_FROGGER_SHAPE) 

writer = trtl.Turtle()
writer.hideturtle()

frogger = trtl.Turtle()
all_turtles = [] 
score = 0
highscores_filepath = "highscores.txt"
lives = LIVES
highest_reached = BOTTOM
gameover = False
splatted = False

#Score Bonus settings
ROW_BONUS = 50  #Awarded each time current frog reaches a higher row than yet visited (resets if life lost)
#SAFELY_ACROSS_BONUS: ROW_BONUS * (#rows cubed)  #Awarded each time frog reaches the other side
LIVES_REMAINING_BONUS = 100 * MAXROWS         # Awarded per remaining life, at end of game
NO_LOST_LIVES_BONUS = 200 * MAXROWS**2  # Awarded at end of game

TURTLE_COLORS = ["red", "orange", "yellow", "green", "blue", "purple", "white", "brown" ]
TURTLE_SHAPES = ["turtle"] * 8

# Load car shapes
CAR_SHAPES_LEFT = ["car/blue.gif","car/brown.gif","car/purple.gif","car/gray.gif","car/green.gif","car/red.gif","car/teal.gif","car/white.gif"]
CAR_SHAPES_RIGHT = []
for car in CAR_SHAPES_LEFT: 
    rightCarFilename = car.replace(".gif","_R.gif")
    CAR_SHAPES_RIGHT.append(rightCarFilename)
    screen.addshape(car)
    screen.addshape(rightCarFilename)


def get_highscores():
    """
    Returns list of high scores from highscores file
    Index in list corresponds to the high score when index=MAXROWS
    """
    try:
        with open(highscores_filepath, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: The file '{highscores_filepath}' was not found.")
    except PermissionError:
        print(f"Error: You do not have permission to read the file '{highscores_filepath}'.")
              
def store_highscore():
    scores = get_highscores()

    # 2. Modify the third line (index 2)
    scores[MAXROWS] = str(highscore) + "\n"
    # 3. Write the modified list back to the file
    with open(highscores_filepath, 'w') as f:
        f.writelines(scores)

def reset_game():
    global score, lives, highest_reached, gameover, splatted
    #Clear turtles
    while (len(all_turtles) > 0):
        row = all_turtles.pop()
        while (len(row) > 0 ):
            t = row.pop()
            t.clear() # Removes its drawings
            t.hideturtle() # Hides the turtle icon
    score = 0
    lives = LIVES
    highest_reached = BOTTOM
    gameover = False
    splatted = False
    
    screen.onkey(None, "y") #disable game reset
    reset_frogger() #call before row buildout, or lose a life! 
    activaterows(STARTINGROWS)
    scoring()
    display_scoring_info()

def reset_frogger():
    global highest_reached, splatted
    frogger.penup()
    frogger.shape(FROGGER_UP)
    frogger.goto(0, FROGGER_STARTING_HEIGHT)
    highest_reached = BOTTOM
    frogger.pendown()
    splatted = False
    screen.update()

def display_scoring_info():
    writer.color("yellow")
    writer.penup()
    writer.goto(-10, 20)
    writer.pendown()
    points = f"""
    Scoring:
        Each row (per life): {ROW_BONUS}
        Successful crossing: {ROW_BONUS} X number of rows cubed
        End of Game:
            Remaining Lives: {LIVES_REMAINING_BONUS} X number of lives
            Cross all {MAXROWS} rows with no lives lost: {NO_LOST_LIVES_BONUS}
      
    """    
    writer.write(points, align="center", font=("Arial", 16, "bold"))
    screen.update()

def handle_collision(turtle):
    """
    Check for "overlap" between this turtle and frogger
    If collision, briefly change frogger to splatted image
    """
    global lives, splatted
    if (abs(turtle.xcor() - frogger.xcor()) < 20) and (abs(turtle.ycor() - frogger.ycor()) < 20):
        splatted = True
        frogger.shape(SPLATTED_FROGGER_SHAPE)
        screen.update()
        time.sleep(1)
        lives -= 1
        scoring()
        reset_frogger()
        time.sleep(0.5) #allow any lingering on_key event listeners to complete

def wrap_around(turtle, direction):
    """
    This produced the continuous scrolling effect: 
    If turtle is beyond the relevant edge, reset it to the other side, 
    giving visual impression that it wrapped around
    """
    global LEFT, RIGHT
    rightgutter= RIGHTSIDE + 20
    leftgutter = rightgutter * -1 
    if direction == RIGHT and turtle.xcor() > rightgutter:
        turtle.setx(leftgutter)
    elif direction == LEFT and turtle.xcor() < leftgutter:
        turtle.setx(rightgutter)

def move_turtles(turts, direction=RIGHT, steps=2, interval=20): 
    """
    Move each turtl in the provided list (row) forward the specified steps
    Also call collision-handling method
    """
    if gameover: return   #This hack is the only way I could determine to properly "freeze" the game when done

    for t in turts:
        t.forward(steps)  
        wrap_around(t, direction)
        handle_collision(t)
    screen.update() 

    #Keep the turtle row running by moving each again, by calling this function again after frequency sec
    screen.ontimer(lambda: move_turtles(turts, direction, steps), interval)        

def load_traffic_row(rownum, direction, shapes, colors, spacing=DEFAULT_SPACING):
    turts = []
    for i, shape in enumerate(shapes):
        t = trtl.Turtle(shape)
        t.fillcolor(colors[i])
        t.penup()
        t.setheading(direction)
        xcor = RIGHTSIDE - (i * spacing)
        bottom = BOTTOM + 75
        t.goto(xcor, bottom + rownum * ROWHEIGHT)  
        turts.append(t)
    all_turtles.append(turts)

def activaterows(numberofrows):
    currentrowcount = len(all_turtles)
    for row in range(currentrowcount, currentrowcount + numberofrows):
        traffic = TURTLE_SHAPES
        direction = RIGHT
        cars = CAR_SHAPES_RIGHT
        spacebetween = DEFAULT_SPACING
        if row % 2 == 0: 
            direction = LEFT
            cars = CAR_SHAPES_LEFT
        if row > 3:
            traffic = cars
            spacebetween += 5
        load_traffic_row(row, direction, traffic, TURTLE_COLORS, spacing = spacebetween)
        move_turtles(all_turtles[row], direction, row + 1)

def hop_leftright(hops):
    if gameover or splatted: return  #Hacky solution to prevent further Frogger movement (and scoring!) at game end
    SIDE_HOP = 20
    if (hops) < 0:
        frogger.shape(FROGGER_LEFT)
    else:
        frogger.shape(FROGGER_RIGHT)

    newX = frogger.xcor() + SIDE_HOP * hops
    if abs(newX) < abs(SCREEN_WIDTH/2 - 20):
        frogger.setx(newX)

def hop_updown(hops):
    if gameover or splatted: return  #Hacky solution to prevent further Frogger movement (and scoring!) at game end
    global highest_reached, score
    VERTICAL_HOP = ROWHEIGHT #fixed, to keep Frogger centered vertically on row
    height = frogger.ycor()
    if (hops) < 0:
        frogger.shape(FROGGER_DOWN)
    else:
        frogger.shape(FROGGER_UP)
        if height > highest_reached:
            score += ROW_BONUS
            scoring()
            highest_reached = height

    newheight = height + VERTICAL_HOP * hops
    maxvertical = ROWHEIGHT * (len(all_turtles) + 1) + FROGGER_STARTING_HEIGHT
    if newheight >= FROGGER_STARTING_HEIGHT and newheight <= maxvertical:  #Keep Frogger in-bounds
        frogger.sety(newheight)
        if newheight == maxvertical and lives > 0:  #Frogger made it through!
            successful_crossing()

def scoring():
    global score, highscore, lives, gameover
    writer.clear()
    writer.color("white")
    writer.penup()
    writer.goto(LEFTSIDE + 10, TOP - 70)
    writer.pendown()
    writer.write(
        f"Score: {score}\nLives: {lives}", align="left", font=("Arial", 16, "normal")
    )
    highscore = max(highscore, score)
    writer.penup()
    writer.goto(RIGHTSIDE - 40, TOP - 35)
    writer.pendown()
    writer.write(
        f"High Score: {highscore}", align="right", font=("Arial", 18, "normal")
    )
    screen.update()
    check_gameover()

def check_gameover():
    global gameover
    if lives == 0:
        store_highscore()
        gameover=True  #Stops movements (move_turtles and hop_* functions)
        writer.color("red")
        writer.penup()
        writer.goto(0, TOP - 50)
        writer.pendown()
        writer.write("Game Over", align="center", font=("Arial", 24, "bold"))
        screen.update()
        time.sleep(1)
        play_again_prompt()

    
def play_again_prompt():
    writer.penup()
    writer.goto(0, TOP - 150)
    writer.pendown()
    writer.write("Play again? ( y / n )", align="center", font=("Arial", 24, "bold"))
    screen.update()
    screen.onkey(reset_game, "y")
    screen.onkey(screen.bye, "n")
   

def successful_crossing():
    """
    Message and scoring for successful crossing, plus adding another row of traffic
    Unless MAXROWS is reached, then display end-of-game message, scoring, and play-again option
    """
    global gameover, score
    writer.color("green")
    writer.penup()
    writer.goto(-50, TOP - 100)
    writer.pendown()
    bonus = ROW_BONUS * len(all_turtles)**3
    writer.write(f"Congrats, you survived! \nBonus: {bonus}\n", align="left", font=("Arial", 18, "bold"))
    score += bonus
    
    # Add a lane (unless game already complete)
    if len(all_turtles) < MAXROWS:
        writer.write("\n\n\nLet's add a lane!", align="left", font=("Arial", 18, "bold"))
        screen.update()
        time.sleep(1)
        scoring()
        reset_frogger()
        activaterows(1)
        time.sleep(1)
    else:
        screen.update()
        time.sleep(1)
        score += LIVES_REMAINING_BONUS * lives
        no_lost_lives_msg = ""
        if (lives == LIVES):
            score += NO_LOST_LIVES_BONUS
            no_lost_lives_msg = f"No lives lost bonus!! {NO_LOST_LIVES_BONUS}"
        scoring()
        store_highscore()
        win_msg = f"""
        !!!!  You Won  !!!!!!
        Remaining lives bonus: {LIVES_REMAINING_BONUS * lives}
        {no_lost_lives_msg}
        """
        writer.color("green")
        writer.penup()
        writer.goto(-50, TOP - 150)
        writer.pendown()
        writer.write(win_msg, align="center", font=("Arial", 24, "bold"))
        screen.update()
        time.sleep(2)
        play_again_prompt()


# Set highscore using value from file, based on current MAXROWS value. Fails if that row in file isn't an integer        
highscore = int(get_highscores()[MAXROWS].strip()) 

screen.onkey(lambda: hop_leftright(-1), "Left")
screen.onkey(lambda: hop_leftright(1), "Right")
screen.onkey(lambda: hop_updown(1), "Up")
screen.onkey(lambda: hop_updown(-1), "5")
screen.onkey(lambda: hop_updown(-1), "Down")
screen.listen()

#=========== Game launch actually begins here ========================
reset_game()

screen.mainloop()