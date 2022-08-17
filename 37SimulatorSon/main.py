import random

def simulate_son(n):
    girl_num = 0
    boy_num = 0

    for _ in range(n):
        girl_num, boy_num = get_boy(girl_num, boy_num)

    return girl_num, boy_num

def get_boy(girl_num, boy_num):
    if random.random() < 0.5:
        boy_num += 1
    else:
        girl_num += 1
        girl_num,boy_num = get_boy(girl_num, boy_num)

    return girl_num, boy_num

girl_num, boy_num = simulate_son(100000000)
print("girl_num: {}, boy_num:{}, ratio:{}".format(girl_num, boy_num, girl_num/boy_num))