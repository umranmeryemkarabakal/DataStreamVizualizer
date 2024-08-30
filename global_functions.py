def filter_outliers(pitch, yaw, roll):
    return abs(pitch) <= 90 and abs(yaw) <= 90 and abs(roll) <= 90

def lerp(start, end, t):
    return start + t * (end - start)

def normalize_angle(angle):
    return (angle + 360) % 360

