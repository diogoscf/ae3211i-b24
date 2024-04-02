import fokker_100 as f100
import constants as c
import matplotlib.pyplot as plt


OEW = f100.EMPTY_WEIGHT * c.G
fuel_weight = f100.FUEL_CAPACITY * c.G
payload_weight = f100.MAX_PAYLOAD * c.G
MTOW = f100.MTOW * c.G
sizes = [OEW, fuel_weight, payload_weight]


labels = [
    f"OEW\n{OEW:.2f} N\n{100*OEW/MTOW:.2f} % of MTOW",
    f"Fuel Weight\n{fuel_weight:.2f} N\n{100*fuel_weight/MTOW:.2f} % of MTOW",
    f"Payload Weight\n{payload_weight:.2f} N\n{100*payload_weight/MTOW:.2f} % of MTOW",
]


fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(sizes)
ax.legend(labels=labels, bbox_to_anchor=(1.3, 1.0))
fig.savefig("pie_chart.png", dpi=300, bbox_inches="tight")
plt.show()
