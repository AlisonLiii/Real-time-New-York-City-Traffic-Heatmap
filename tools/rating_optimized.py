def do_calculate(speed_data, weather_summary, sc):
    # initialize
    weather_detail = weather_summary[2]
    for i in range(len(speed_data) // 2):
        realtime_speed = speed_data[i * 2]
        free_flow_speed = speed_data[i * 2 + 1]
        crash = 0
        weather = weather_detail[1]
        if weather == 'Rainy':
            amount = weather_detail[4]
        elif weather == 'Snow':
            amount = weather_detail[5]
        else:
            amount = 0
        r_congestion = findRcongestion(weather, amount, free_flow_speed, realtime_speed)
        data = sc.parallelize([[r_congestion, weather, crash]])
        if i == 0:
            prev_data = data
        else:
            data = prev_data.union(data)
    return data


def calculate_coe(weather, amount):
    if weather == ['Rainy']:
        if amount <= 5:
            # small
            upper_boundary = 1
            lower_boundary = 0.96
            amountP = amount / 5  # amount percentage
        elif 5 < amount <= 10:
            # moderate
            upper_boundary = 0.96
            lower_boundary = 0.88
            amountP = amount / 10
        else:
            # heavy
            upper_boundary = 0.88
            lower_boundary = 0.74
            if amount <= 15:
                amountP = amount / 15
            else:
                amountP = 0
                lower_boundary = 0.6
                # too heavy, speed reduction 40%
        wea_coefficient = upper_boundary - (upper_boundary - lower_boundary) * amountP
    elif weather == ['Snow']:
        if amount <= 5:
            # small
            upper_boundary = 0.9
            lower_boundary = 0.69
            amountP = amount / 5  # amount percentage
        elif 5 < amount <= 20:
            # moderate
            upper_boundary = 0.69
            lower_boundary = 0.59
            amountP = amount / 20
        elif 20 < amount <= 75:
            # heavy
            upper_boundary = 0.59
            lower_boundary = 0.50
            amountP = amount / 75
        else:
            upper_boundary = 0.4
            amountP = 0
            # too heavy, fix reduction 60%
        wea_coefficient = upper_boundary - (upper_boundary - lower_boundary) * amountP
    # handle sunny day
    else:
        wea_coefficient = 1
    return wea_coefficient


def findRcongestion(weather, amount, free_flow_speed, realtime_speed):
    weather_coefficient = calculate_coe(weather, amount)
    expected_speed = free_flow_speed * weather_coefficient
    r_congestion = -(expected_speed - realtime_speed) ** 2  # use variance to determine rate of congestion
    return r_congestion
