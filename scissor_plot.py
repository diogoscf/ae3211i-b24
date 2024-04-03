from math import tan, radians, sqrt, pi, atan2, sin, cos
import matplotlib.pyplot as plt


def datcom(A, M, eta, half_chord_sweep):
    beta = sqrt(1 - M**2)
    C_L_alpha = (2 * pi * A) / (2 + sqrt(4 + (A * beta / eta)**2 * (1 + (tan(half_chord_sweep))**2/(beta**2))))
    return C_L_alpha


def stability_line(
    ax, max_Sh_S, M, S, S_net, b, mac, quarter_chord_sweep, half_chord_sweep, taper_ratio, A_h,
    horizontal_stab_half_chord_sweep, use_torenbeek_method, eta, l_h, delta_z_wing_tail_acs, b_f, h_f, l_fn, b_n, l_n, 
    c_l_des, x_ac_w, k_n, Vh_V, stability_margin,
):
    A = b ** 2 / S
    C_L_alpha_H = datcom(A_h, M, eta, horizontal_stab_half_chord_sweep)
    C_L_alpha_w = datcom(A, M, eta, half_chord_sweep)
    C_L_alpha_A_H = C_L_alpha_w * (1 + 2.15 * b_f/b) * (S_net/S) + (pi/2) * (b_f**2 / S)
    
    r = 2 * l_h / b  # same for both
    
    if not use_torenbeek_method:
        print("hahahaha no")
        raise ValueError("nice try")
        # if r <= r_ruv:
        #     k_m_vsd = ...
        
        # else:
        #     k_m_vsd = ...

        # m_vsd = k_m_vsd * C_L / (pi * A)

        # K_eps_sweep = (0.1124 + 0.1265 * quarter_chord_sweep + 0.1766 * quarter_chord_sweep ** 2) / r**2 + (0.1024 / r) + 2
        # K_eps_sweep_equals_0 = 0.1124 / r**2 + 0.1024 / r + 2
        # d_eps_d_alpha = (K_eps_sweep / K_eps_sweep_equals_0) * (
        #     (r / (r**2 + m_tv**2)) * (0.4876 / sqrt(r**2 + 0.6319 + m_tv**2))
        #     + (1 + (r**2 / (r**2 + 0.7915 + 5.0734*m_tv**2)**0.3113)) * (1 - sqrt(m_tv**2 / (1 + m_tv**2)))
        # ) * C_L_alpha_w / (pi * A)
        # one_minus_d_eps_d_alpha = 1 - d_eps_d_alpha
    
    else:
        zero_lift_angle = radians(4 * c_l_des)
        ac_angle = atan2(delta_z_wing_tail_acs, l_h)
        m_dimensional = l_h * sin(zero_lift_angle + ac_angle) / cos(ac_angle)
        m = 2 * m_dimensional / b
        d_eps_d_alpha = 1.75 * C_L_alpha_w / (pi * A * (taper_ratio * r)**0.25 * (1 + abs(m)))
        one_minus_d_eps_d_alpha = (1 - d_eps_d_alpha) * 0.9  # correct for fuselage engines
    

    x_ac_f1 = (-1.8 / C_L_alpha_A_H) * (b_f * h_f * l_fn) / (S * mac)
    c_g = S / b
    x_ac_f2 = (0.273 / (1 + taper_ratio)) * (b_f * c_g * (b - b_f)) / (mac ** 2 + 2.15 * b_f) * tan(quarter_chord_sweep)
    x_ac_n = 2 * k_n * (b_n ** 2 * l_n) / (S * mac * C_L_alpha_A_H)
    x_ac = x_ac_w + x_ac_f1 + x_ac_f2 + x_ac_n

    denom = (C_L_alpha_H / C_L_alpha_A_H * one_minus_d_eps_d_alpha * l_h / mac * Vh_V ** 2)
    intercept = (x_ac - stability_margin) / denom
    x_points = [x_ac - stability_margin, (max_Sh_S - intercept) * denom]
    y_points = [0, max_Sh_S]
    ax.plot(x_points, y_points, label="Stability curve")


def scissor_plot(
    filename, max_Sh_S, M_cruise, S, S_net, b, mac, quarter_chord_sweep_deg, half_chord_sweep_deg, taper_ratio, A_h,
    horizontal_stab_half_chord_sweep_deg, use_torenbeek_method, eta, l_h, delta_z_wing_tail_acs, b_f, h_f, l_fn, b_n,
    l_n, c_l_des, x_ac_w, k_n, Vh_V, stability_margin,
):
    fig, ax = plt.subplots(figsize=(12, 8))

    stability_line(
        ax,
        max_Sh_S,
        M_cruise,
        S,
        S_net,
        b,
        mac,
        radians(quarter_chord_sweep_deg),
        radians(half_chord_sweep_deg),
        taper_ratio,
        A_h,
        radians(horizontal_stab_half_chord_sweep_deg),
        use_torenbeek_method,
        eta,
        l_h,
        delta_z_wing_tail_acs,
        b_f,
        h_f,
        l_fn,
        b_n,
        -l_n,
        c_l_des,
        x_ac_w,
        k_n,
        Vh_V,
        stability_margin,
    )

    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    reference_aircraft_config = {
        "filename": "ref_aircraft_scissor_plot",          # filename to save to
        "max_Sh_S": 0.7,                                  # max Sh/S to plot
        "M_cruise": 0.7,                                  # cruise Mach number
        "S": 93.5,                                        # wing area in [m^2]
        "S_net": 81.1229,                                 # S less the projection of the wing in the fuselage [m^2]
        "b": 28.076,                                      # wingspan [m]
        "mac": 3.79856,                                   # m.a.c. [m]
        "quarter_chord_sweep_deg": 18.0360317,            # main wing c/4 sweep [deg]
        "half_chord_sweep_deg": 13.5937727,               # main wing c/2 sweep [deg]
        "taper_ratio": 0.23,                              # wing taper ratio [-]
        "A_h": 4.68329,                                   # aspect ratio of the horizontal stabiliser [-]
        "horizontal_stab_half_chord_sweep_deg": 22.9888,  # horizontal stabiliser c/2 sweep [deg]
        "use_torenbeek_method": True,                     # whether to use the Torenbeek method for dε/dα (True), or not (False)
        "eta": 0.95,                                      # airfoil efficiency coefficient for DATCOM method [-]
        "l_h": 16.6012063,                                # length between main wing and horizontal tail a.c.'s [m]
        "delta_z_wing_tail_acs": 5.58227921,              # height difference between main wing and horizontal tail a.c.'s [m]
        "b_f": 3.3,                                       # fuselage width [m]
        "h_f": 3.283,                                     # fuselage height [m]
        "l_fn": 14.04049659,                              # distance from nose to LE of root chord [m]
        "b_n": 1.52530611,                                # max nacelle diameter [m]
        "l_n": 10.32898502,                               # distance from wing a.c. to rear of nacelle [m]; should be positive
        "c_l_des": 3 * 0.15,                              # airfoil design lift coefficient [-]
        "x_ac_w": 0.445,                                  # from Torenbeek figure E-10 [-]
        "k_n": -2.5,                                      # nacelle a.c. shift coefficient [-]; -2.5 for rear fuselage podded engines
        "Vh_V": 1,                                        # tail speed ratio [-]; 1 for T-tail
        "stability_margin": 0.05,                         # stability margin, in fraction m.a.c. [-]
    }
    scissor_plot(**reference_aircraft_config)