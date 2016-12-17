"""game"""
# http://www.pymunk.org/en/latest/

import math
import random
import sys
import getopt
import os

import pygame
import pymunk
import pymunk.pygame_util

SCREENX = 400
SCREENY = 400
MAX_ASTEROIDS = 8
MAX_ASTEROID_MASS = 15
MAX_ASTEROID_IMPULSE = int(MAX_ASTEROID_MASS * 3.2)
MAX_ASTEROID_ROTATION = 5
SHIP_TORQUE_LIMIT = 65
SHIP_DIM = 17
SENSOR_RANGE = 22
SENSOR_DISTANCE = 26
NUM_SENSORS = 5
ANGLE_APERTURE = (2 * math.pi) / NUM_SENSORS
WALL_THICKNESS = int(SCREENX / 4)

#   for every sensor:
#   IMPULSE (a vector like (x, x))
SHIP_AI = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

COLLISION_TYPE = {
    "ROCK": 1,
    "SHIP": 2,
    "OTHER": 3
}

COLLISIONS = 0
DISTANCE = 0

ship_last_position = 0

SHIP_POINTS_LIST = ((0, 0), (0, 0), (0, 0))

# ship P.I.D.
last_error = 0
#integral = 0
P_FACTOR = 10
#I_FACTOR = 0
D_FACTOR = 400

AUTO_CLOSE_VALUE = 2


def add_meteor(space):
    """create meteor"""
    mass = random.randint(int(MAX_ASTEROID_MASS / 2), MAX_ASTEROID_MASS)
    radius = mass * 1.7
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
    body = pymunk.Body(mass, inertia)
    if random.randint(0, 1):        # from left or right
        if random.randint(0, 1):        # from left
            body.position = SCREENX * -0.1, random.randint(0, SCREENY)
        else:                           # from right
            body.position = SCREENX * 1.1, random.randint(0, SCREENY)
    else:                           # from up or down
        if random.randint(0, 1):        # from up
            body.position = random.randint(0, SCREENX), SCREENY * -0.1
        else:                           # from down
            body.position = random.randint(0, SCREENX), SCREENY * 1.1
    body.apply_impulse_at_local_point(
        (random.randint(-MAX_ASTEROID_IMPULSE, MAX_ASTEROID_IMPULSE), random.randint(-MAX_ASTEROID_IMPULSE, MAX_ASTEROID_IMPULSE)))
    body.angular_velocity = random.randint(
        -MAX_ASTEROID_ROTATION, MAX_ASTEROID_ROTATION)

    shape = pymunk.Circle(body, radius, (0, 0))
    shape.friction = 0
    shape.elasticity = 0.9
    shape.collision_type = COLLISION_TYPE["ROCK"]
    shape.filter = pymunk.ShapeFilter(categories=0x1)
    space.add(body, shape)

    def collision_event(_arb, self, _space):
        """avoid collision between border and asteroid'"""
        return False
    collision = space.add_collision_handler(
        COLLISION_TYPE["ROCK"],
        COLLISION_TYPE["OTHER"])
    collision.begin = collision_event

    return shape


def add_ship(space):
    """create ship"""
    body = pymunk.Body(10, 10)
    body.position = (SCREENX / 4, SCREENY / 4)
    global ship_last_position
    ship_last_position = body.position

    convex_hull = pymunk.Poly(body, [pygame.math.Vector2(
        SHIP_DIM, 0,), pygame.math.Vector2(-SHIP_DIM, SHIP_DIM), pygame.math.Vector2(-SHIP_DIM, -SHIP_DIM)])

    convex_hull.elasticity = 0
    convex_hull.collision_type = COLLISION_TYPE["SHIP"]
    convex_hull.filter = pymunk.ShapeFilter(categories=0x2)
    convex_hull.friction = 0.5
    """segment1 = pymunk.Segment(body, (SHIP_DIM, 0),
                              (-SHIP_DIM, SHIP_DIM), SHIP_DIM / 8)
    segment2 = pymunk.Segment(body, (SHIP_DIM, 0),
                              (-SHIP_DIM, -SHIP_DIM), SHIP_DIM / 8)
    segment3 = pymunk.Segment(body, (-SHIP_DIM, SHIP_DIM),
                              (-SHIP_DIM, -SHIP_DIM), SHIP_DIM / 8)
    segment1.elasticity = 0
    segment2.elasticity = 0
    segment3.elasticity = 0
    segment1.collision_type = COLLISION_TYPE["SHIP"]
    segment2.collision_type = COLLISION_TYPE["SHIP"]
    segment3.collision_type = COLLISION_TYPE["SHIP"]
    segment1.filter = pymunk.ShapeFilter(categories=0x2)
    segment2.filter = pymunk.ShapeFilter(categories=0x2)
    segment3.filter = pymunk.ShapeFilter(categories=0x2)"""

    def collision_event(_arb, self, _space):
        """avoid collision between border and asteroid'"""
        # print "COLLISION", add_collision()
        global COLLISIONS
        COLLISIONS = COLLISIONS + 1
        return True

    collision = space.add_collision_handler(
        COLLISION_TYPE["SHIP"],
        COLLISION_TYPE["ROCK"])
    collision.post_solve = collision_event

    collision = space.add_collision_handler(
        COLLISION_TYPE["SHIP"],
        COLLISION_TYPE["OTHER"])
    collision.post_solve = collision_event

    space.add(convex_hull, body)
    #space.add(segment1, segment2, segment3, body)

    global SHIP_POINTS_LIST
    SHIP_POINTS_LIST = ((SHIP_DIM, 0), (-SHIP_DIM, SHIP_DIM),
                        (-SHIP_DIM, -SHIP_DIM))
    return body


def add_border(space):
    """create border"""
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = (0, 0)
    WALL_THICKNESS
    segment1 = pymunk.Segment(body, (-WALL_THICKNESS-1, -WALL_THICKNESS-1),
                              (SCREENX + WALL_THICKNESS, -WALL_THICKNESS), WALL_THICKNESS)
    segment2 = pymunk.Segment(body, (SCREENX + WALL_THICKNESS, -WALL_THICKNESS),
                              (SCREENX + WALL_THICKNESS, SCREENY + WALL_THICKNESS), WALL_THICKNESS)
    segment3 = pymunk.Segment(body, (SCREENX + WALL_THICKNESS, SCREENY + WALL_THICKNESS),
                              (-WALL_THICKNESS, SCREENY + WALL_THICKNESS), WALL_THICKNESS )
    segment4 = pymunk.Segment(body, (-WALL_THICKNESS-1, SCREENY + WALL_THICKNESS),
                              (-WALL_THICKNESS, -WALL_THICKNESS), WALL_THICKNESS)

    segment1.collision_type = COLLISION_TYPE["OTHER"]
    segment2.collision_type = COLLISION_TYPE["OTHER"]
    segment3.collision_type = COLLISION_TYPE["OTHER"]
    segment4.collision_type = COLLISION_TYPE["OTHER"]
    segment1.filter = pymunk.ShapeFilter(categories=0x1)
    segment2.filter = pymunk.ShapeFilter(categories=0x1)
    segment3.filter = pymunk.ShapeFilter(categories=0x1)
    segment4.filter = pymunk.ShapeFilter(categories=0x1)
    space.add(segment1, segment2, segment3, segment4, body)

    return body


def ship_poke_around(space, ship, screen):
    """check collision around ship in space all into the screen area"""
    # sensori
    sensor_pos = [0, 0]
    # first sensor have x1.7 range because is in front
    sensorrange = int(SENSOR_RANGE * 1.7)
    custom_filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0x2)
    for i in range(0, NUM_SENSORS):
        # like this there will be always a sensor in the head
        angle = -ship.angle + ANGLE_APERTURE * (i + 0.5)  # ? why offest ?
        sensor_pos[0] = (math.cos(angle) + math.sin(angle)) * \
            SENSOR_DISTANCE + ship.position[0]
        sensor_pos[1] = (-math.sin(angle) + math.cos(angle)) * \
            SENSOR_DISTANCE + ship.position[1]
        var = space.point_query_nearest(
            sensor_pos, sensorrange, custom_filter)
        if var is not None:
            new_position = pymunk.pygame_util.to_pygame(var.point, screen)

            delta = ship.position - new_position
            norm = (SENSOR_DISTANCE + sensorrange) / \
                math.sqrt(delta[0] * delta[0] + delta[1] * delta[1])

            pygame.draw.circle(screen, (255, 0, 0),
                               new_position, int(norm * 8), 1)

            # apply sensor response
            ship.apply_force_at_local_point(
                (SHIP_AI[0 + i * 2] * norm, SHIP_AI[1 + i * 2] * norm), (0, 0))

            pygame.draw.circle(screen, (0, 255, 0),
                               new_position, int(norm * 8), 1)

            sens = pygame.math.Vector2(
                SHIP_AI[0 + i * 2] * norm * 2, SHIP_AI[1 + i * 2] * norm * 2)
            sens.rotate_ip(ship.angle * 180 / math.pi)
            target = sens + \
                pygame.math.Vector2(ship.position[0], ship.position[1])
            pygame.draw.line(screen, (255, 128, 0), ship.position, target)

        pygame.draw.circle(screen, (255, 255, 255),
                           ((int)(sensor_pos[0]), (int)(sensor_pos[1])), sensorrange, 1)
        sensorrange = SENSOR_RANGE


def move_rotate_ship(ship):
    """rotate the ship according the trajectory"""
    """
    integral += currentError * timeFrame;
    var deriv = (currentError - lastError) / timeFrame;
    lastError = currentError;
    return currentError * pFactor
        + integral * iFactor
        + deriv * dFactor;"""
    global ship_last_position

    global last_error

    global DISTANCE

    direction = ship.position - ship_last_position
    DISTANCE = DISTANCE + \
        math.sqrt(direction.x * direction.x + direction.y * direction.y)
    ship_angle_direction = math.atan2(direction.y, direction.x)

    current_error = ship_angle_direction - ship.angle

    #integral = integral + current_error
    deriv = current_error - last_error
    last_error = current_error

    #ship.torque = current_error * P_FACTOR + integral * I_FACTOR + deriv * D_FACTOR
    torque = current_error * P_FACTOR + deriv * D_FACTOR
    if torque > SHIP_TORQUE_LIMIT:
        torque = SHIP_TORQUE_LIMIT
    ship.torque = torque
    ship_last_position = ship.position


def move_with_mouse(position, bodysim):
    """move objectSim to the position"""
    position = pygame.mouse.get_pos()
    bodysim.position = position


def manage_asteroid(balls, space):
    """manage asteroid in balls into space like spawing and deleting"""
    if len(balls) < MAX_ASTEROIDS:
        ball_shape = add_meteor(space)
        balls.append(ball_shape)

    balls_to_remove = []
    for ball in balls:
        if ball.body.position.y > SCREENY * 1.2:
            balls_to_remove.append(ball)
        if ball.body.position.x > SCREENX * 1.2:
            balls_to_remove.append(ball)
        if ball.body.position.y < -SCREENY * 0.2:
            balls_to_remove.append(ball)
        if ball.body.position.x < -SCREENX * 0.2:
            balls_to_remove.append(ball)

    for ball in balls_to_remove:
        try:  # strange error
            space.remove(ball, ball.body)
            balls.remove(ball)
        except KeyError:
            print ("ERRORE STRANO")

MINSPEED = 12


def start(datafile=None, limitRun=888888, windowX=0, windowY=0):
    """main loop"""
    # print "Usage:"
    # print "--file:  the file containing the spaceship to simulate"
    # print "--limit: frame limit"

    os.environ['SDL_VIDEO_WINDOW_POS'] = str(windowX) + "," + str(windowY)

    pygame.init()

    # initialize font; must be called after 'pygame.init()' to avoid 'Font not
    # Initialized' error
    myfont = pygame.font.SysFont("monospace", 15)

    # render text

    limit = int(limitRun)

    global SHIP_AI

    if limit == -1:
        limit = 999999999

    if datafile is not None:
        try:
            in_file = open(str(datafile), "r")
        except:
            print ("Error opening file:", datafile)
            sys.exit(-10)
        text = in_file.read().split(";")
        in_file.close()
        for j in range(0, len(SHIP_AI)):
            SHIP_AI[j] = (float(text[j]) - 256.0) / 14.0
    else:
        SHIP_AI = [10, 10, 0, 0, 0, 0, 0, 0, 10, 10]

    print ("Simulation of", datafile, "running for", limit, "iterations")
    # print SHIP_AI

    screen = pygame.display.set_mode((SCREENX, SCREENX), pygame.NOFRAME)
    pygame.display.set_caption("Tests")
    pymunk.pygame_util.positive_y_is_up = False
    clock = pygame.time.Clock()

    space = pymunk.Space()
    space.gravity = (0.0, 0.0)

    balls = []
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    ship = add_ship(space)
    add_border(space)

    ship.apply_impulse_at_local_point((100, 40), (0, 0))

    iteration_count = 0

    while iteration_count < limit:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            """elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit(0)
                elif event.key == pygame.K_DOWN:
                    ship.apply_impulse_at_local_point((0, 100))
                elif event.key == pygame.K_UP:
                    ship.apply_impulse_at_local_point((0, -100))
                elif event.key == pygame.K_RIGHT:
                    ship.apply_impulse_at_local_point((100, 0))
                elif event.key == pygame.K_LEFT:
                    ship.apply_impulse_at_local_point((-100, 0))
                elif event.key == pygame.K_SPACE:
                    ship.angular_velocity = 0"""

        screen.fill((0, 0, 0))

        # game logic
        manage_asteroid(balls, space)
        #move_with_mouse(pygame.mouse.get_pos(), ship)

        speed = ship.velocity.get_length()
        if speed <= MINSPEED:
            ship.apply_force_at_local_point((MINSPEED * 2 / speed, 0), (0, 0))
        ship_poke_around(space, ship, screen)
        move_rotate_ship(ship)

        # game simulation
        space.step(1 / 30.0)
        # clock.tick(60)

        # game draw
        space.debug_draw(draw_options)
        draw(screen, ship, balls, myfont, iteration_count, limit)

        pygame.display.flip()
        # print clock.get_fps()
        iteration_count = iteration_count + 1

        if float(DISTANCE / (COLLISIONS + 1)) < AUTO_CLOSE_VALUE and iteration_count > 10:
            save_and_exit(datafile, float(DISTANCE / (COLLISIONS + 1)))

    save_and_exit(datafile, float(DISTANCE / (COLLISIONS + 1)))


def draw(screen, ship, meteors, myfont, iteration_count, limit):
    """draw function, all the draw calls should go in here"""

    point1 = pygame.math.Vector2(
        (SHIP_POINTS_LIST[0])[0], (SHIP_POINTS_LIST[0])[1])
    point1.rotate_ip(ship.angle * 180 / math.pi)
    point2 = pygame.math.Vector2(
        (SHIP_POINTS_LIST[1])[0], (SHIP_POINTS_LIST[1])[1])
    point2.rotate_ip(ship.angle * 180 / math.pi)
    point3 = pygame.math.Vector2(
        (SHIP_POINTS_LIST[2])[0], (SHIP_POINTS_LIST[2])[1])
    point3.rotate_ip(ship.angle * 180 / math.pi)
    ship_points = ((point1[0] + ship.position[0], point1[1] + ship.position[1]),
                   (point2[0] + ship.position[0],
                    point2[1] + ship.position[1]),
                   (point3[0] + ship.position[0], point3[1] + ship.position[1]))

    pygame.draw.polygon(screen, (51, 153, 255), ship_points, 0)

    for ball in meteors:
        pygame.draw.circle(screen, (128, 128, 128), (int(ball.body.position[
            0]), int(ball.body.position[1])), int(ball.radius), 0)

    label = myfont.render("Distanza   " + str(DISTANCE), 1, (255, 255, 0))
    screen.blit(label, (0, 0))
    label = myfont.render("Collisioni " + str(COLLISIONS), 1, (255, 255, 0))
    screen.blit(label, (0, 15))
    label = myfont.render(
        "Bonta'     " + str(float(DISTANCE / (COLLISIONS + 1))), 1, (255, 255, 0))
    screen.blit(label, (0, 30))
    label = myfont.render(
        "Countdown  " + str(limit - iteration_count), 1, (255, 255, 0))
    screen.blit(label, (0, 45))
    label = myfont.render(
        "Velocita'   " + str(ship.velocity.get_length()), 1, (255, 255, 0))
    screen.blit(label, (0, 60))


def save_and_exit(filename, result):
    """save result on file"""
    in_file = open(filename, "r")
    line = in_file.readline()
    myfile = open(filename, "w+")
    myfile.write(str(line))
    myfile.write(str(result))
    sys.exit(1)

if __name__ == '__main__':
    start()
