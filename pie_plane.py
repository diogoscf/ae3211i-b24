import fokker_100 as f100
import constants as c
import matplotlib.pyplot as plt


OEW = f100.EMPTY_WEIGHT*c.G
Fuel = f100.FUEL_CAPACITY*c.G
Payload = f100.MAX_PAYLOAD*c.G
MTOW = f100.MTOW*c.G
sizes = [OEW, Fuel, Payload]


labels = [f'OEW\n{OEW:.2f} [N]', f"Fuel Weight\n{Fuel:.2f} [N]", f"Payload Weight\n{Payload:.2f}"]


fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.show()