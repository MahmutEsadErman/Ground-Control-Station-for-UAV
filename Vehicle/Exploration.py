import math

# Directions
up_left = 0
up_right = 1
down_right = 2
down_left = 3

horizontal = False
vertical = True


def exploration(vehicle, point1, point2, altitude, fov):
    # Sorting 4 angles as up-left:0, up-right:1, down-right:2, down-left:3
    if point1[0] <= point2[0] and point1[1] <= point2[1]:
        point_list = [[point2[0], point1[1]], point2, [point1[0], point2[1]], point1]
    elif point1[0] >= point2[0] and point1[1] <= point2[1]:
        point_list = [point1, [point1[0], point2[1]], point2, [point2[0], point1[1]]]
    elif point1[0] <= point2[0] and point1[1] >= point2[1]:
        point_list = [point2, [point2[0], point1[1]], point1, [point1[0], point2[1]]]
    elif point1[0] >= point2[0] and point1[1] >= point2[1]:
        point_list = [[point1[0], point2[1]], point1, [point2[0], point1[1]], point2]

    waypoint_list = []

    # Find first waypoint
    starting_point_no = find_closest_point([vehicle.latitude, vehicle.longitude], point_list)
    ending_point_no = (starting_point_no + 2) % 4

    # Find Short Edge
    short_edge = find_short_edge(point1, point2)  # 0 for horizontal, 1 for vertical edge
    if short_edge == vertical:
        short_edge_length = get_distance_from_lat_lon_in_km(point_list[up_left], point_list[down_left])
    else:
        short_edge_length = get_distance_from_lat_lon_in_km(point_list[up_left], point_list[up_right])

    # Calculate Distance Between Waypoint (in short edge)
    distance_between_wp = calculate_distance_between_waypoints(fov, vehicle.camera_angle, altitude)

    if short_edge == horizontal:
        direction = 0
        new_lng = point_list[starting_point_no][1]
        if starting_point_no == up_right or starting_point_no == down_right:
            direction = 180
        _, new_lng = get_point_at_distance(point_list[starting_point_no][0], point_list[starting_point_no][1],
                                           90 + direction,
                                           distance_between_wp / 2)
        waypoint_list.append([point_list[starting_point_no][0], new_lng])

    elif short_edge == vertical:
        if starting_point_no == up_right or starting_point_no == up_left:
            direction = 0
        else:
            direction = 180

        # Put the first waypoint
        new_lat, _ = get_point_at_distance(point_list[starting_point_no][0], point_list[starting_point_no][1],
                                           180 + direction,
                                           distance_between_wp / 2)
        waypoint_list.append([new_lat, point_list[starting_point_no][1]])

    i = 0
    # loop while not reached to the ending point
    while (i // 2) * distance_between_wp < (short_edge_length - distance_between_wp):
        i += 1
        if short_edge == vertical:
            if i % 4 == 2 or i % 4 == 0:  # movement in short edge
                new_lat, _ = get_point_at_distance(waypoint_list[i - 1][0], waypoint_list[i - 1][1], 180 + direction,
                                                   distance_between_wp)
            if i % 4 == 1 or i % 4 == 2:  # movement in opposite edge
                waypoint_list.append([new_lat, point_list[ending_point_no][1]])
            if i % 4 == 0 or i % 4 == 3:  # movement in starting edge
                waypoint_list.append([new_lat, point_list[starting_point_no][1]])

        elif short_edge == horizontal:
            if i % 4 == 2 or i % 4 == 0:  # movement in short edge
                _, new_lng = get_point_at_distance(waypoint_list[i - 1][0], waypoint_list[i - 1][1], 90 + direction,
                                                   distance_between_wp)
            if i % 4 == 1 or i % 4 == 2:  # movement in opposite edge
                waypoint_list.append([point_list[ending_point_no][0], new_lng])
            elif i % 4 == 0 or i % 4 == 3:  # movement in starting edge
                waypoint_list.append([point_list[starting_point_no][0], new_lng])

    # For last long edge movement
    i += 1
    if short_edge == vertical:
        if i % 4 == 1 or i % 4 == 2:  # movement in opposite edge
            waypoint_list.append([new_lat, point_list[ending_point_no][1]])
        if i % 4 == 0 or i % 4 == 3:  # movement in starting edge
            waypoint_list.append([new_lat, point_list[starting_point_no][1]])
    else:
        if i % 4 == 1 or i % 4 == 2:  # movement in opposite edge
            waypoint_list.append([point_list[ending_point_no][0], new_lng])
        elif i % 4 == 0 or i % 4 == 3:  # movement in starting edge
            waypoint_list.append([point_list[starting_point_no][0], new_lng])

    return waypoint_list


def find_closest_point(initial_location, point_list):
    """
    Finds the closest point to the initial location
    """
    min_distance = get_distance_from_lat_lon_in_km(initial_location, point_list[0])
    closest_point = 0
    for i in range(1, 4):
        distance = get_distance_from_lat_lon_in_km(initial_location, point_list[i])
        if distance < min_distance:
            min_distance = distance
            closest_point = i
    return closest_point


def find_short_edge(point1, point2):
    """
    Finds which edge is shorter, horizontal or vertical
    0 for horizontal, 1 for vertical edge
    """
    if get_distance_from_lat_lon_in_km([point1[0], 0], [point2[0], 0]) < get_distance_from_lat_lon_in_km([0, point1[1]],
                                                                                                         [0,
                                                                                                          point2[1]]):
        return True
    else:
        return False


def calculate_distance_between_waypoints(fov, camera_angle, altitude):
    """
    Calculates the distance between waypoints in km
    """
    hypotenuse = (1 / math.cos(deg2rad(camera_angle))) * altitude
    return (2 * math.tan(deg2rad(fov / 2)) * hypotenuse) / 1000


def get_point_at_distance(lat, lng, angle, d):
    """
    lat: initial latitude, in degrees
    lon: initial longitude, in degrees
    d: target distance from initial
    bearing: (true) heading in degrees
    R: optional radius of sphere, defaults to mean radius of earth

    Returns new lat/lon coordinate {d}km from initial, in degrees
    """
    R = 6371
    lat1 = math.radians(lat)
    lon1 = math.radians(lng)
    a = math.radians(angle)
    lat2 = math.asin(math.sin(lat1) * math.cos(d / R) + math.cos(lat1) * math.sin(d / R) * math.cos(a))
    lon2 = lon1 + math.atan2(
        math.sin(a) * math.sin(d / R) * math.cos(lat1),
        math.cos(d / R) - math.sin(lat1) * math.sin(lat2)
    )
    return math.degrees(lat2), math.degrees(lon2)


def get_distance_from_lat_lon_in_km(point1, point2):
    R = 6371  # Radius of the earth in km
    dLat = deg2rad(point2[0] - point1[0])
    dLon = deg2rad(point2[1] - point1[1])
    a = (
            math.sin(dLat / 2) * math.sin(dLat / 2) +
            math.cos(deg2rad(point1[0])) * math.cos(deg2rad(point2[0])) *
            math.sin(dLon / 2) * math.sin(dLon / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d


def deg2rad(deg):
    return deg * (math.pi / 180)
