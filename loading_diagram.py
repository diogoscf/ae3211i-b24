from constants import G

import matplotlib.pyplot as plt


def add_cargo(ax, start_weight, start_cg, front_cargo_position, back_cargo_position, front_cargo, back_cargo):
    full_cargo_weight = start_weight + front_cargo + back_cargo
    full_cargo_cg = (
        start_weight * start_cg
        + front_cargo * front_cargo_position
        + back_cargo * back_cargo_position
    ) / (full_cargo_weight)
    front_cgs = [
        start_cg,
        (start_weight * start_cg + front_cargo * front_cargo_position) / (start_weight + front_cargo),
        full_cargo_cg,
    ]
    front_weights = [start_weight, start_weight + front_cargo, full_cargo_weight]
    back_cgs = [
        start_cg,
        (start_weight * start_cg + back_cargo * back_cargo_position) / (start_weight + back_cargo),
        full_cargo_cg,
    ]
    back_weights = [start_weight, start_weight + back_cargo, full_cargo_weight]
    ax.plot(front_cgs, front_weights, "orangered", label="Cargo loading (front to back)")
    ax.plot(back_cgs, back_weights, "darkred", label="Cargo loading (back to front)")
    return full_cargo_weight, full_cargo_cg, {start_cg, full_cargo_cg, *front_cgs, *back_cgs}


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


def add_fuel(ax, start_weight, start_cg, load_wing_tank_first, wing_tank_capacity, center_tank_capacity, wing_tank_position, center_tank_position, fuel_load):
    if load_wing_tank_first:
        pass

    return 1, 2, {start_cg}


def generate_loading_diagram(
    filename, show_legend, cargo_first, OEW_kg, xcg_oew, x_LEMAC_m, MAC_m, front_cargo_position_m,
    back_cargo_position_m, front_cargo_kg, back_cargo_kg, num_pax, pax_kg, first_row_position_m, seat_pitch_in,
    load_wing_tank_first, wing_tank_capacity_kg, center_tank_capacity_kg, wing_tank_position_mac,
    center_tank_position_mac, fuel_load_kg
):
    fig, ax = plt.subplots(figsize=(12, 8))
    OEW = OEW_kg * G  # convert to [N]
    all_cgs = {xcg_oew}

    if cargo_first:
        after_cargo_weight, after_cargo_cg, cargo_cgs = add_cargo(
            ax,
            OEW,
            xcg_oew,
            (front_cargo_position_m - x_LEMAC_m) / MAC_m,
            (back_cargo_position_m - x_LEMAC_m) / MAC_m,
            front_cargo_kg * G,
            back_cargo_kg * G,
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
            (front_cargo_position_m - x_LEMAC_m) / MAC_m,
            (back_cargo_position_m - x_LEMAC_m) / MAC_m,
            front_cargo_kg * G,
            back_cargo_kg * G,
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
        fuel_load_kg * G
    )
    
    # final cg bounds
    all_cgs.update(cargo_cgs, pax_cgs, fuel_cgs)
    cg_margin = 0.02  # cg margin, in % MAC
    lower_limit = min(all_cgs) - cg_margin
    upper_limit = max(all_cgs) + cg_margin
    ax.axvline(lower_limit, c="k", label="cg limits position with margin")
    ax.axvline(upper_limit, c="k")  # yes this has no label, but they're both black lines

    if show_legend:
        ax.legend()
    ax.set_xlabel(r"$x_{cg}/\bar{c}$ [-]")
    ax.set_ylabel(r"$W$ [N]")
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    full_payload_config = {
        "filename": "full_payload_config",        # filename to save to
        "show_legend": True,                      # whether to display the legend
        "cargo_first": True,                      # whether to load cargo first (True) or passengers (False)
        "x_LEMAC_m": 15,                          # position of the MAC from the nose, in [m]
        "MAC_m": 4,                               # MAC, in [m]
        "OEW_kg": 10_000,                         # OEW, in [kg]
        "xcg_oew": 0.3,                           # xcg of the OEW, in % MAC [-]
        "front_cargo_position_m": 10,             # xcg of the front cargo hold, from the nose in [m]
        "back_cargo_position_m": 20,              # xcg of the back cargo hold, from the nose in [m]
        "front_cargo_kg": 6000,                   # weight of the front cargo, in [kg]
        "back_cargo_kg": 5000,                    # weight of the back cargo, in [kg]
        "num_pax": 109,                           # number of passengers [-]
        "pax_kg": 79,                             # weight of each passenger, in [kg]
        "first_row_position_m": 8,                # position of the first row, from the nose in [m]
        "seat_pitch_in": 32,                      # seat pitch, in [in]
        "load_wing_tank_first": True,             # whether to load the wing tank first (True), or the center tank (False)
        "wing_tank_capacity_kg": 7000,            # capacity of both wing tanks, in [kg] of fuel
        "center_tank_capacity_kg": 3000,          # capacity of the center tank, in [kg] of fuel
        "wing_tank_position_mac": 0.6,            # wing tank cg, in % MAC from LEMAC [-]
        "center_tank_position_mac": 0.4,          # center tank cg, in % MAC from LEMAC [-]
        "fuel_load_kg": 9000,                     # total fuel load, in [kg]
    }
    generate_loading_diagram(**full_payload_config)
