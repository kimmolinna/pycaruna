import pycaruna

session = pycaruna.login_caruna("", "")
customer = pycaruna.get_current(session)
metering_points = pycaruna.get_metering_points(session, customer)
consumption = pycaruna.get_cons_hours(session, customer, metering_points[1][0], "2022-11-01", "2022-11-30")
print( consumption)
#Kimmo Linna