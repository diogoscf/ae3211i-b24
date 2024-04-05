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

    legend_fix, = ax.plot(front_cgs, front_weights, "orangered", label="Cargo loading (front to back)")
    ax.plot(back_cgs, back_weights, "darkred", label="Cargo loading (back to front)")

    return front_weights[-1], front_cgs[-1], {*front_cgs, *back_cgs}, legend_fix


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


def add_pax_new(ax, start_weight, start_cg, num_pax, pax_weight, first_row_position, seat_pitch):
    num_full_rows, num_last_row = divmod(num_pax, 5)
    has_extra_row = num_last_row != 0
    if has_extra_row:
        last_row_position = first_row_position + (num_full_rows) * seat_pitch
    else:
        last_row_position = first_row_position + (num_full_rows - 1) * seat_pitch
    
    # windows
    # front to back
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
    # back to front
    for i in range(num_full_rows + has_extra_row + 1):
        Wi = start_weight + 2 * i * pax_weight
        cgs_windows_back_to_front.append(
            (
                start_weight * start_cg
                + 2*i * pax_weight * (last_row_position - (i-1)/2 * seat_pitch)
                
            ) / Wi
        )
    
    # check if last cg front to back is same as last cg back to front
    if cgs_windows_front_to_back[-1] != cgs_windows_back_to_front[-1]:
        print(f"{cgs_windows_front_to_back[-1]} != {cgs_windows_back_to_front[-1]}")
        raise ValueError("CG mismatch between front to back and back to front window seat loading")

    # aisles
    # front to back
    weights_aisles = []
    cgs_aisles_front_to_back = []
    cgs_aisles_back_to_front = []
    for i in range(num_full_rows + has_extra_row + 1):
        Wi = weights_windows[-1] + 2 * i * pax_weight
        weights_aisles.append(Wi)
        cgs_aisles_front_to_back.append(
            (
                weights_windows[-1] * cgs_windows_front_to_back[-1]
                + pax_weight * (
                    (2 * i) * ((i-1)/2 * seat_pitch + first_row_position)
                )
            )
            / Wi
        )
    # back to front
    for i in range(num_full_rows + has_extra_row + 1):
        Wi = weights_windows[-1] + 2 * i * pax_weight
        cgs_aisles_back_to_front.append(
            (
                weights_windows[-1] * cgs_windows_front_to_back[-1]
                + 2*i * pax_weight * (last_row_position - (i-1)/2 * seat_pitch)
                
            ) / Wi
        )
    
    # check if last cg front to back is same as last cg back to front
    if cgs_aisles_front_to_back[-1] != cgs_aisles_back_to_front[-1]:
        print(f"{cgs_aisles_front_to_back[-1]} != {cgs_aisles_back_to_front[-1]}")
        raise ValueError("CG mismatch between front to back and back to front aisle seat loading")

    # middle
    # front to back
    weights_middle = []
    cgs_middle_front_to_back = []
    cgs_middle_back_to_front = []
    if has_extra_row:
        for i in range(num_full_rows + 1):
            Wi = weights_aisles[-1] + i * pax_weight
            weights_middle.append(Wi)
            cgs_middle_front_to_back.append(
                (
                    weights_aisles[-1] * cgs_aisles_front_to_back[-1]
                    + pax_weight * i * (first_row_position+ (i-1)/2* seat_pitch)
                    )
                / Wi
            )
        # back to front
        for i in range(num_full_rows + 1):
            Wi = weights_aisles[-1] +  i * pax_weight
            cgs_middle_back_to_front.append(
                (
                    weights_aisles[-1] * cgs_aisles_front_to_back[-1]
                    + i * pax_weight * (last_row_position - (i+1)/2 * seat_pitch)
                ) / Wi
            )
    else:
        for i in range(num_full_rows+1):

            Wi = weights_aisles[-1] + i * pax_weight
            weights_middle.append(Wi)
            cgs_middle_front_to_back.append(
                (
                    weights_aisles[-1] * cgs_aisles_front_to_back[-1]
                    + pax_weight * i * (first_row_position+ (i-1)/2* seat_pitch)
                    )
                / Wi
            )
        # back to front
        for i in range(num_full_rows+1):
            Wi = weights_aisles[-1] +  i * pax_weight
            cgs_middle_back_to_front.append(
                (
                    weights_aisles[-1] * cgs_aisles_front_to_back[-1]
                    + i * pax_weight * (last_row_position - (i-1)/2 * seat_pitch)
                ) / Wi
            )

    # check if last cg front to back is same as last cg back to front
    if cgs_middle_front_to_back[-1] != cgs_middle_back_to_front[-1]:
        print(f'nrows+1: {num_full_rows+1}')
        print(f"{cgs_middle_front_to_back[-1]} != {cgs_middle_back_to_front[-1]}")
        raise ValueError("CG mismatch between front to back and back to front middle seat loading")
    
    ax.plot(cgs_windows_front_to_back, weights_windows, c="orange", label="Window seats (front to back)")
    ax.plot(cgs_windows_back_to_front, weights_windows, c="peru", label="Window seats (back to front)")
    ax.plot(cgs_aisles_front_to_back, weights_aisles, c="yellowgreen", label="Aisle seats (front to back)")
    ax.plot(cgs_aisles_back_to_front, weights_aisles, c="lawngreen", label="Aisle seats (back to front)")
    ax.plot(cgs_middle_front_to_back, weights_middle, c="aquamarine", label="Middle seats (front to back)")
    ax.plot(cgs_middle_back_to_front, weights_middle, c="lightseagreen", label="Middle seats (back to front)")
    print(f"Added {num_pax} passengers at {pax_weight / G:.2f} [kg] each for a total mass of {num_pax * pax_weight / G:.2f} [kg]")
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

def add_battery(ax, start_weight, start_cg, battery_pos, battery_weight):
    if battery_pos == "none":
        return start_weight, start_cg, {start_cg}
    print(f"Loading battery of {battery_weight / G:.2f} [kg] at {battery_pos:.2f} % MAC from LEMAC")
    new_weight = start_weight + battery_weight
    new_cg = (start_weight * start_cg + battery_weight * battery_pos) / new_weight
    ax.plot([start_cg, new_cg], [start_weight, new_weight], c="darkviolet", label="Battery")
    return new_weight, new_cg, {start_cg, new_cg}


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

    ax.plot(cgs, weights, c="royalblue", label=f"Fuel ({'wing tanks' if load_wing_tank_first else 'center tank'} first)")

    return weights[-1], cgs[-1], {start_cg, *cgs}


def generate_loading_diagram(
    filename, show_legend, cargo_first, x_LEMAC_m, MAC_m, xcg_oew, OEW_kg, mtow_kg, max_payload_kg, total_cargo_kg, 
    front_cargo_max_weight_kg, front_cargo_stations_m, back_cargo_max_weight_kg, back_cargo_stations_m, num_pax,
    pax_kg, first_row_position_m, seat_pitch_in, load_wing_tank_first, wing_tank_capacity_kg, center_tank_capacity_kg, 
    wing_tank_position_mac, center_tank_position_mac, fuel_load_kg, battery_pos, battery_mass=0, fig=None, ax=None, legend_thingy=None
):
    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(6, 4.5))
        double_plot = False
    else:
        # change colour of existing lines to red
        for line in ax.lines:
            line.set_color("red")
        for line in ax.collections:
            print(line)
            line.set_color("red")
        print("existing lines changed to red")
        ax.legend_ = None
        ax.legend([legend_thingy], ['F100'])
        double_plot = True

    OEW = OEW_kg * G  # convert to [N]
    all_cgs = {xcg_oew}

    if cargo_first:
        after_cargo_weight, after_cargo_cg, cargo_cgs, legend_thingy = add_cargo(
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
        after_cargo_and_pax_weight, after_cargo_and_pax_cg, pax_cgs = add_pax_new(
            ax,
            after_cargo_weight,
            after_cargo_cg,
            num_pax,
            pax_kg * G,
            (first_row_position_m - x_LEMAC_m) / MAC_m,
            (seat_pitch_in * 0.0254) / MAC_m, 
        )
        after_cargo_pax_battery_weight, after_cargo_pax_battery_cg, battery_cgs = add_battery(
            ax,
            after_cargo_and_pax_weight,
            after_cargo_and_pax_cg,
            battery_pos,
            battery_mass * G
        )
    else:
        after_pax_weight, after_pax_cg, pax_cgs = add_pax_new(
            ax,
            OEW,
            xcg_oew,
            num_pax,
            pax_kg * G,
            (first_row_position_m - x_LEMAC_m) / MAC_m,
            (seat_pitch_in * 0.0254) / MAC_m,
        )
        after_pax_battery_weight, after_pax_battery_cg, battery_cgs = add_battery(
            ax,
            after_pax_weight,
            after_pax_cg,
            battery_pos,
            battery_mass * G
        )
        after_cargo_pax_battery_weight, after_cargo_pax_battery_cg, cargo_cgs, legend_thingy = add_cargo(
            ax,
            after_pax_battery_weight,
            after_pax_battery_cg,
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
        after_cargo_pax_battery_weight, 
        after_cargo_pax_battery_cg,
        load_wing_tank_first,
        wing_tank_capacity_kg * G,
        center_tank_capacity_kg * G,
        wing_tank_position_mac,
        center_tank_position_mac,
        mtow_kg * G,
        fuel_load_kg * G if isinstance(fuel_load_kg, (int, float)) else fuel_load_kg
    )
    
    # final cg bounds
    all_cgs.update(cargo_cgs, pax_cgs, fuel_cgs, battery_cgs)
    cg_margin = 0.02  # cg margin, in % MAC
    lower_limit = min(all_cgs) - cg_margin
    upper_limit = max(all_cgs) + cg_margin
    ax.axvline(lower_limit, c="k", label=f"cg limits with {cg_margin * 100:.0f}% margin", linestyle="--")
    ax.axvline(upper_limit, c="k", linestyle="--")  # yes this has no label, but they're both black lines
    print(f"LOWER c.g. LIMIT: {lower_limit*100:.2f} % of MAC from LEMAC")
    print(f"UPPER c.g. LIMIT: {upper_limit*100:.2f} % of MAC from LEMAC")

    if show_legend:
        if not double_plot:
            ax.legend()
        if double_plot: 
            # change colour of new lines to blue
            for line in ax.lines:
                if line.get_color() != "red":
                    line.set_color("blue")
            for line in ax.collections:
                if line.get_color() != "red":
                    line.set_color("blue")
            other_legend, = ax.plot([], [], "red", label="F100")
            ax.legend([legend_thingy, other_legend], ['F120', 'F100'], loc='upper right')
    ax.set_xlabel(r"$x_{cg}/\bar{c}$ from $x_{LEMAC}$ [-]")
    ax.set_ylabel(r"$W$ [N]")
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()

    return fig, ax, legend_thingy


if __name__ == "__main__":
    full_payload_config = {
        "filename": "full_payload_config",          # filename to save to
        "show_legend": True,                        # whether to display the legend
        "cargo_first": True,                        # whether to load cargo first (True) or passengers first (False)
        "x_LEMAC_m": 15.8745,                       # position of the MAC from the nose, in [m]
        "MAC_m": 3.79857,                           # MAC, in [m]
        "xcg_oew": 0.816098,                        # xcg of the OEW, in % MAC [-]
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
        "first_row_position_m": 6.90,               # position of the first row, from the nose in [m]
        "seat_pitch_in": 32,                        # seat pitch, in [in]
        "load_wing_tank_first": True,               # whether to load the wing tank first (True), or the center tank (False)
        "wing_tank_capacity_kg": 7744,              # capacity of both wing tanks, in [kg] of fuel
        "center_tank_capacity_kg": 2512,            # capacity of the center tank, in [kg] of fuel
        "wing_tank_position_mac": 0.4564,           # wing tank cg, in % MAC from LEMAC [-]
        "center_tank_position_mac": 0.1133,         # center tank cg, in % MAC from LEMAC [-]
        "fuel_load_kg": "max",                      # total fuel load, in [kg], or "max" to load up to limiting factor (MTOW or tank capacity)
        "battery_pos": 'none',                      # position of the battery, in % MAC [-] or "none" if no battery
    }
    fig, ax, legend_thingy = generate_loading_diagram(**full_payload_config)

    f120_config = full_payload_config.copy()

    f120_config["filename"] = "f120_config"
    f120_config['battery_pos'] = -3.047071139
    f120_config['battery_mass'] = 400
    f120_config['wing_tank_capacity_kg'] = 0
    f120_config['center_tank_capacity_kg'] = 3110.2
    f120_config['fuel_load_kg'] = 500
    f120_config['num_pax'] = 90
    f120_config['load_wing_tank_first'] = False
    f120_config['OEW_kg'] = 25507.59
    f120_config['mtow_kg'] = 41311.79
    f120_config['center_tank_position_mac'] = 2.0010
    f120_config['xcg_oew'] = 0.90765
    f120_config['max_payload_kg'] = 12294
    
    f120_config["fig"] = fig
    f120_config["ax"] = ax
    f120_config["legend_thingy"] = legend_thingy
    generate_loading_diagram(**f120_config)
    