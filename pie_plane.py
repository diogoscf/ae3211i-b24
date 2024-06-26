import fokker_100 as f100
import constants as c
import matplotlib.pyplot as plt


OEW = f100.EMPTY_WEIGHT * c.G
fuel_weight = f100.FUEL_CAPACITY * c.G
payload_weight = f100.MAX_PAYLOAD * c.G
MTOW = f100.MTOW * c.G
sizes = [OEW, fuel_weight, payload_weight]


def more_than_100_percent():
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


def max_payload_weight_breakdown():
    OEW = f100.EMPTY_WEIGHT * c.G
    fuel_weight = 9070 * c.G
    payload_weight = f100.MAX_PAYLOAD * c.G

    sizes = [OEW, fuel_weight, payload_weight]

    labels = [
        f" OEW\n{OEW:.2f} N",
        f" Fuel Weight\n{fuel_weight:.2f} N",
        f" Payload Weight\n{payload_weight:.2f} N",
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes, autopct="%1.2f%%")
    ax.legend(labels=labels, bbox_to_anchor=(1.3, 1.0))
    fig.savefig("pie_chart_1.png", dpi=300, bbox_inches="tight")
    plt.show()


def f120_weight_breakdown():
    OEW = 25507.59 * c.G
    fuel_weight = 500 * c.G
    payload_weight = 12294 * c.G
    MTOW_120 = 41311.79 * c.G
    BW = 400 * c.G

    sizes = [OEW, fuel_weight, payload_weight, BW]

    labels = [
        f" OEW\n{OEW:.2f} N\n{100*OEW/MTOW_120:.2f} % of MTOW_120",
        f" Fuel Weight\n{fuel_weight:.2f} N\n{100*fuel_weight/MTOW_120:.2f} % of MTOW_120",
        f" Payload Weight\n{payload_weight:.2f} N\n{100*payload_weight/MTOW_120:.2f} % of MTOW_120",
        f" Battery Weight\n{BW:.2f} N\n{100*BW/MTOW_120:.2f} % of MTOW_120"
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(sizes)
    ax.legend(labels=labels, bbox_to_anchor=(1.3, 1.0))
    fig.savefig("pie_chart_f120.png", dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    f120_weight_breakdown()
