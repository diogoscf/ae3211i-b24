from constants import G

import matplotlib.pyplot as plt


def add_cargo(ax, OEW, xcg_oew, front_cargo_location, back_cargo_location, front_cargo, back_cargo):
    full_cargo_weight = OEW + front_cargo + back_cargo
    full_cargo_cg = (
        OEW * xcg_oew
        + front_cargo * front_cargo_location
        + back_cargo * back_cargo_location
    ) / (full_cargo_weight)
    front_cgs = [
        xcg_oew,
        (OEW * xcg_oew + front_cargo * front_cargo_location) / (OEW + front_cargo),
        full_cargo_cg,
    ]
    front_weights = [OEW, OEW + front_cargo, full_cargo_weight]
    back_cgs = [
        xcg_oew,
        (OEW * xcg_oew + back_cargo * back_cargo_location) / (OEW + back_cargo),
        full_cargo_cg,
    ]
    back_weights = [OEW, OEW + back_cargo, full_cargo_weight]
    ax.plot(front_cgs, front_weights, "orangered", label="Cargo loading (front to back)")
    ax.plot(back_cgs, back_weights, "darkred", label="Cargo loading (back to front)")
    return full_cargo_cg, full_cargo_weight


def add_pax(ax, num_pax, pax_weight, first_row_position, seat_pitch, start_cg, start_weight):
    num_full_rows, num_last_row = divmod(num_pax, 5)
    has_extra_row = num_last_row != 0
    last_row_position = first_row_position + (num_full_rows - 1) * seat_pitch

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

    return ..., num_pax * pax_weight


def generate_loading_diagram(
    filename,
    show_legend,
    OEW_kg,
    xcg_oew,
    x_LEMAC_m,
    MAC_m,
    front_cargo_location_m,
    back_cargo_location_m,
    front_cargo_kg,
    back_cargo_kg,
    num_pax,
    pax_kg,
    first_row_position_m,
    seat_pitch_in,
):
    fig, ax = plt.subplots(figsize=(12, 8))
    OEW = OEW_kg * G  # convert to [N]

    after_cargo_cg, after_cargo_weight = add_cargo(
        ax,
        OEW,
        xcg_oew,
        (front_cargo_location_m - x_LEMAC_m) / MAC_m,
        (back_cargo_location_m - x_LEMAC_m) / MAC_m,
        front_cargo_kg * G,
        back_cargo_kg * G,
    )

    after_pax_cg, after_pax_weight = add_pax(
        ax,
        num_pax,
        pax_kg * G,
        (first_row_position_m - x_LEMAC_m) / MAC_m,
        (seat_pitch_in * 0.0254) / MAC_m,
        after_cargo_cg,
        after_cargo_weight,
    )

    if show_legend:
        ax.legend()
    ax.set_xlabel(r"$x_{cg}/\bar{c}$ [-]")
    ax.set_ylabel(r"$W$ [N]")
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    full_payload_config = {
        "filename": "full_payload_config",  # filename to save to
        "show_legend": True,  # whether to display the legend
        "x_LEMAC_m": 15,  # position of the MAC from the nose, in [m]
        "MAC_m": 4,  # MAC, in [m]
        "OEW_kg": 10_000,  # OEW, in [kg]
        "xcg_oew": 0.3,  # xcg of the OEW, in % MAC [-]
        "front_cargo_location_m": 10,  # xcg of the front cargo hold, from the nose in [m]
        "back_cargo_location_m": 20,  # xcg of the back cargo hold, from the nose in [m]
        "front_cargo_kg": 6000,  # weight of the front cargo, in [kg]
        "back_cargo_kg": 5000,  # weight of the back cargo, in [kg]
        "num_pax": 109,  # number of passengers [-]
        "pax_kg": 79,  # weight of each passenger, in [kg]
        "first_row_position_m": 8,  # position of the first row, from the nose in [m]
        "seat_pitch_in": 32,  # seat pitch, in [in]
    }
    generate_loading_diagram(**full_payload_config)
