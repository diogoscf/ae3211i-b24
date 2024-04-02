from constants import G

import matplotlib.pyplot as plt


def add_cargo(ax, start_weight, start_cg, total_cargo, front_cargo_max_weight, front_cargo_position, back_cargo_max_weight, back_cargo_position, payload_weight, num_pax, pax_weight):
    if isinstance(total_cargo, (int, float)):
        if total_cargo > front_cargo_max_weight + back_cargo_max_weight:
            raise ValueError(
                f"requested cargo load of {total_cargo / G} [kg] exceeds cargo capacity of "
                f"{(front_cargo_max_weight + back_cargo_max_weight) / G} [kg]"
            )
        if total_cargo + num_pax * pax_weight > payload_weight:
            raise ValueError(
                f"requested cargo load of {total_cargo / G} [kg] plus the total pax weight of "
                f"{num_pax * pax_weight / G} exceeds the max payload weight of {payload_weight / G} [kg]"
            )
        fraction = total_cargo / (front_cargo_max_weight + back_cargo_max_weight)  # assume balanced
    elif isinstance(total_cargo, str):
        if total_cargo != "max":
            raise ValueError(f"invalid total cargo choice {total_cargo}")
        total_cargo = min(front_cargo_max_weight + back_cargo_max_weight, payload_weight - num_pax * pax_weight)
        fraction = total_cargo / (front_cargo_max_weight + back_cargo_max_weight)
    else:
        raise TypeError(f"invalid type of total cargo {type(total_cargo)}")
    
    print(f"Loading cargo: {total_cargo/G:.2f} kg")
    print(f"  Cargo fraction: {fraction*100:.2f} %")
    front_weights = [start_weight, start_weight + front_cargo_max_weight * fraction, start_weight + total_cargo]
    front_cgs = [
        start_cg,
        (start_weight * start_cg + fraction * (front_cargo_max_weight * front_cargo_position)) / (start_weight + front_cargo_max_weight * fraction),
        (start_weight * start_cg + fraction * (front_cargo_max_weight * front_cargo_position + back_cargo_max_weight * back_cargo_position)) / (start_weight + total_cargo)
    ]
    back_weights = [start_weight, start_weight + back_cargo_max_weight * fraction, start_weight + total_cargo]
    back_cgs = [
        start_cg,
        (start_weight * start_cg + fraction * (back_cargo_max_weight * back_cargo_position)) / (start_weight + back_cargo_max_weight * fraction),
        (start_weight * start_cg + fraction * (front_cargo_max_weight * front_cargo_position + back_cargo_max_weight * back_cargo_position)) / (start_weight + total_cargo)
    ]

    ax.plot(front_cgs, front_weights, "orangered", label="Cargo loading (front to back)")
    ax.plot(back_cgs, back_weights, "darkred", label="Cargo loading (back to front)")

    return front_weights[-1], front_cgs[-1], {*front_cgs, *back_cgs}


def add_pax(ax, start_weight, start_cg, num_pax, pax_weight, first_row_position, seat_pitch):
    num_full_rows, num_last_row = divmod(num_pax, 5)
    has_extra_row = num_last_row != 0
    last_row_position = first_row_position + (num_full_rows - 1) * seat_pitch

    # TODO: figure out why i-3 works for backwards loading - doesn't make sense at all, even though it looks right

    # Windows
    weights_windows = []
    cgs_windows_front_to_back = []
    cgs_windows_back_to_front = []
    for i in range(num_full_rows + has_extra_row + 1):
        Wi = start_weight + 2 * i * pax_weight
        weights_windows.append(Wi)
        cgs_windows_front_to_back.append(
            (
                start_weight * start_cg
                + pax_weight * (
                    (2 * i) * ((i-1)/2 * seat_pitch + first_row_position)
                )
            )
            / Wi
        )
        cgs_windows_back_to_front.append(
            (
                start_weight * start_cg
                + pax_weight * (
                    (2 * i) * (last_row_position - (i-3)/2 * seat_pitch)
                )
            ) / Wi
        )

    # Aisles
    weights_aisles = []
    cgs_aisles_front_to_back = []
    cgs_aisles_back_to_front = []
    for i in range(num_full_rows + has_extra_row + 1):
        Wi = start_weight + 2 * pax_weight * ((num_full_rows + has_extra_row) + i)
        weights_aisles.append(Wi)
        cgs_aisles_front_to_back.append(
            (
                start_weight * start_cg
                + pax_weight * (
                    (2 * (num_full_rows + has_extra_row)) * ((num_full_rows + has_extra_row - 1)/2 * seat_pitch + first_row_position)
                    + (2 * i) * ((i-1)/2 * seat_pitch + first_row_position)
                )
            )
            / Wi
        )
        cgs_aisles_back_to_front.append(
            (
                start_weight * start_cg
                + pax_weight * (
                    (2 * (num_full_rows + has_extra_row)) * ((num_full_rows + has_extra_row - 1)/2 * seat_pitch + first_row_position)
                    + (2 * i) * (last_row_position - (i-3)/2 * seat_pitch)
                )
            )
            / Wi
        )

    # middle
    weights_middle = []
    cgs_middle_front_to_back = []
    cgs_middle_back_to_front = []
    for i in range(num_full_rows + 1):
        Wi = start_weight + pax_weight * (4 * (num_full_rows + has_extra_row) + i)
        weights_middle.append(Wi)
        cgs_middle_front_to_back.append(
            (
                start_weight * start_cg
                + pax_weight * (
                    (4 * (num_full_rows + has_extra_row)) * ((num_full_rows + has_extra_row - 1)/2 * seat_pitch + first_row_position)
                    + i * ((i-1)/2 * seat_pitch + first_row_position)
                )
            )
            / Wi
        )
        cgs_middle_back_to_front.append(
            (
                start_weight * start_cg
                + pax_weight * (
                    (4 * (num_full_rows + has_extra_row)) * ((num_full_rows + has_extra_row - 1)/2 * seat_pitch + first_row_position)
                    + i * (last_row_position - seat_pitch - (i-3)/2 * seat_pitch)
                )
            )
            / Wi
        )
    
    ax.plot(cgs_windows_front_to_back, weights_windows, c="orange", label="Window seats (front to back)")
    ax.plot(cgs_windows_back_to_front, weights_windows, c="peru", label="Window seats (back to front)")
    ax.plot(cgs_aisles_front_to_back, weights_aisles, c="yellowgreen", label="Aisle seats (front to back)")
    ax.plot(cgs_aisles_back_to_front, weights_aisles, c="lawngreen", label="Aisle seats (back to front)")
    ax.plot(cgs_middle_front_to_back, weights_middle, c="aquamarine", label="Middle seats (front to back)")
    ax.plot(cgs_middle_back_to_front, weights_middle, c="lightseagreen", label="Middle seats (back to front)")
    print(f"Added {num_pax} passengers at {pax_weight / G:.2f} [kg] each for a total weight of {num_pax * pax_weight / G:.2f} [kg]")

    return (
        start_weight + num_pax * pax_weight,
        (
            start_weight * start_cg
            + pax_weight * (
                (4 * (num_full_rows + has_extra_row)) * ((num_full_rows + has_extra_row - 1)/2 * seat_pitch + first_row_position)
                + (num_full_rows) * ((num_full_rows-1)/2 * seat_pitch + first_row_position)
            )
        ) / (start_weight + num_pax * pax_weight),
        {
            start_cg, *cgs_windows_front_to_back, *cgs_windows_back_to_front, *cgs_aisles_front_to_back, 
            *cgs_aisles_back_to_front, *cgs_middle_front_to_back, *cgs_middle_back_to_front
        }
    )


def add_fuel(ax, start_weight, start_cg, load_wing_tank_first, wing_tank_capacity, center_tank_capacity, wing_tank_position, center_tank_position, mtow, fuel_load):
    if isinstance(fuel_load, str):
        if fuel_load != "max":
            raise ValueError(f"invalid fuel load option {fuel_load}")
        fuel_load = min(mtow - start_weight, wing_tank_capacity + center_tank_capacity)
    elif isinstance(fuel_load, (float, int)):
        if fuel_load > wing_tank_capacity + center_tank_capacity:
            raise ValueError(
                f"fuel load of {fuel_load / G} [kg] is beyond total tank capacity of "
                f"{(wing_tank_capacity + center_tank_capacity) / G} [kg]"
            )
        if start_weight + fuel_load > mtow:
            raise ValueError(
                f"fuel load of {fuel_load / G} [kg] plus ZFW of {start_weight / G} [kg] is beyond the MTOW of "
                f"{mtow / G} [kg]"
            )

    if load_wing_tank_first:
        wing_load = min(wing_tank_capacity, fuel_load)
        center_load = max(0, fuel_load - wing_load)
        weights = [start_weight, start_weight + wing_load, start_weight + fuel_load]
        cgs = [
            start_cg,
            (start_weight * start_cg + wing_load * wing_tank_position) / (start_weight + wing_load),
            (start_weight * start_cg + wing_load * wing_tank_position + center_load * center_tank_position) / (start_weight + fuel_load),
        ]
    else:
        center_load = min(center_tank_capacity, fuel_load)
        wing_load = max(0, fuel_load - center_load)
        weights = [start_weight, start_weight + center_load, start_weight + fuel_load]
        cgs = [
            start_cg,
            (start_weight * start_cg + center_load * center_tank_position) / (start_weight + center_load),
            (start_weight * start_cg + center_load * center_tank_position + wing_load * wing_tank_position) / (start_weight + fuel_load),
        ]
    print(f"Loading {fuel_load / G:.2f} [kg] of fuel into {'wing' if load_wing_tank_first else 'center'} tank first")
    print(f"  Wing tank load: {wing_load / G:.2f} [kg]")
    print(f"  Center tank load: {center_load / G:.2f} [kg]")
    print(f"  Fuel tank fill fraction: {fuel_load / (center_tank_capacity + wing_tank_capacity) * 100:.2f} %")
    
    ax.plot(cgs, weights, c="blue", label=f"Fuel ({'wing tanks' if load_wing_tank_first else 'center tank'} first)")

    return weights[-1], cgs[-1], {start_cg, *cgs}


def generate_loading_diagram(
    filename, show_legend, cargo_first, x_LEMAC_m, MAC_m, xcg_oew, OEW_kg, mtow_kg, max_payload_kg, total_cargo_kg, 
    front_cargo_max_weight_kg, front_cargo_stations_m, back_cargo_max_weight_kg, back_cargo_stations_m, num_pax,
    pax_kg, first_row_position_m, seat_pitch_in, load_wing_tank_first, wing_tank_capacity_kg, center_tank_capacity_kg, 
    wing_tank_position_mac, center_tank_position_mac, fuel_load_kg
):
    fig, ax = plt.subplots(figsize=(12, 8))
    OEW = OEW_kg * G  # convert to [N]
    all_cgs = {xcg_oew}

    if cargo_first:
        after_cargo_weight, after_cargo_cg, cargo_cgs = add_cargo(
            ax,
            OEW,
            xcg_oew,
            total_cargo_kg * G if isinstance(total_cargo_kg, (int, float)) else total_cargo_kg,
            front_cargo_max_weight_kg * G,
            ((front_cargo_stations_m[0] + front_cargo_stations_m[1])/2 - x_LEMAC_m) / MAC_m,
            back_cargo_max_weight_kg * G,
            ((back_cargo_stations_m[0] + back_cargo_stations_m[1])/2 - x_LEMAC_m) / MAC_m,
            max_payload_kg * G,
            num_pax,
            pax_kg * G,
        )
        after_cargo_and_pax_weight, after_cargo_and_pax_cg, pax_cgs = add_pax(
            ax,
            after_cargo_weight,
            after_cargo_cg,
            num_pax,
            pax_kg * G,
            (first_row_position_m - x_LEMAC_m) / MAC_m,
            (seat_pitch_in * 0.0254) / MAC_m,
        )
    else:
        after_pax_weight, after_pax_cg, pax_cgs = add_pax(
            ax,
            OEW,
            xcg_oew,
            num_pax,
            pax_kg * G,
            (first_row_position_m - x_LEMAC_m) / MAC_m,
            (seat_pitch_in * 0.0254) / MAC_m,
        )
        after_cargo_and_pax_weight, after_cargo_and_pax_cg, cargo_cgs = add_cargo(
            ax,
            after_pax_weight,
            after_pax_cg,
            total_cargo_kg * G if isinstance(total_cargo_kg, (int, float)) else total_cargo_kg,
            front_cargo_max_weight_kg * G,
            ((front_cargo_stations_m[0] + front_cargo_stations_m[1])/2 - x_LEMAC_m) / MAC_m,
            back_cargo_max_weight_kg * G,
            ((back_cargo_stations_m[0] + back_cargo_stations_m[1])/2 - x_LEMAC_m) / MAC_m,
            max_payload_kg * G,
            num_pax,
            pax_kg * G,
        )
    
    after_fuel_weight, after_fuel_cg, fuel_cgs = add_fuel(
        ax,
        after_cargo_and_pax_weight,
        after_cargo_and_pax_cg,
        load_wing_tank_first,
        wing_tank_capacity_kg * G,
        center_tank_capacity_kg * G,
        wing_tank_position_mac,
        center_tank_position_mac,
        mtow_kg * G,
        fuel_load_kg * G if isinstance(fuel_load_kg, (int, float)) else fuel_load_kg,
    )
    
    # final cg bounds
    all_cgs.update(cargo_cgs, pax_cgs, fuel_cgs)
    cg_margin = 0.02  # cg margin, in % MAC
    lower_limit = min(all_cgs) - cg_margin
    upper_limit = max(all_cgs) + cg_margin
    ax.axvline(lower_limit, c="k", label=f"cg limits with {cg_margin * 100:.0f}% margin")
    ax.axvline(upper_limit, c="k")  # yes this has no label, but they're both black lines
    print(f"LOWER c.g. LIMIT: {lower_limit*100:.2f} % of MAC from LEMAC")
    print(f"UPPER c.g. LIMIT: {upper_limit*100:.2f} % of MAC from LEMAC")

    if show_legend:
        ax.legend()
    ax.set_xlabel(r"$x_{cg}/\bar{c}$ from $x_{LEMAC}$ [-]")
    ax.set_ylabel(r"$W$ [N]")
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    full_payload_config = {
        "filename": "full_payload_config",          # filename to save to
        "show_legend": True,                        # whether to display the legend
        "cargo_first": True,                        # whether to load cargo first (True) or passengers first (False)
        "x_LEMAC_m": 15.8745,                       # position of the MAC from the nose, in [m]
        "MAC_m": 3.79857,                           # MAC, in [m]
        "xcg_oew": 0.76946,                         # xcg of the OEW, in % MAC [-]
        "OEW_kg": 24541,                            # OEW, in [kg]
        "mtow_kg": 45810,                           # MTOW, in [kg]
        "max_payload_kg": 12199,                    # max payload (pax + cargo) weight, in [kg]
        "total_cargo_kg": "max",                    # either the total cargo in [kg], or "max" to fill up to limiting factor (capacity or max payload)
        "front_cargo_max_weight_kg": 1239 + 1387,   # max weights of the front compartment (hold 1 and 2) in [kg]
        "front_cargo_stations_m": (6.920, 14.466),  # the front and rear stations of the front compartments in [m], from the nose
        "back_cargo_max_weight_kg": 1576 + 982,     # iterable of the max weights of the 3 rear compartments in [kg]
        "back_cargo_stations_m": (18.506, 24.878),  # iterable of the 4 inter-compartment stations of the rear compartments in [m], from the nose
        "num_pax": 109,                             # number of passengers [-]
        "pax_kg": 79,                               # weight of each passenger, in [kg]
        "first_row_position_m": (8 * 32 * 0.0254),  # position of the first row, from the nose in [m]
        "seat_pitch_in": 32,                        # seat pitch, in [in]
        "load_wing_tank_first": True,               # whether to load the wing tank first (True), or the center tank (False)
        "wing_tank_capacity_kg": 7744,              # capacity of both wing tanks, in [kg] of fuel
        "center_tank_capacity_kg": 2512,            # capacity of the center tank, in [kg] of fuel
        "wing_tank_position_mac": 0.4564,           # wing tank cg, in % MAC from LEMAC [-]
        "center_tank_position_mac": 0.1133,         # center tank cg, in % MAC from LEMAC [-]
        "fuel_load_kg": "max",                      # total fuel load, in [kg], or "max" to load up to limiting factor (MTOW or tank capacity)
    }
    generate_loading_diagram(**full_payload_config)
