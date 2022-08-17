import random

def win_prize_num(n):
    stay_win = 0
    switch_win = 0
    for _ in range(n):
        door_with_car = random.randint(1,3)
        guss_door = random.randint(1, 3)

        if door_with_car == guss_door:
            stay_win += 1
        
        if door_with_car != guss_door:
            switch_win += 1
    
    print("stay_win ratio:{}, switch_win ratio:{}".format(stay_win/n, switch_win/n))


n = 100000
win_prize_num(n)