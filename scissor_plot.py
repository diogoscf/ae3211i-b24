from math import tan, radians, sqrt, pi, atan2, sin, cos
import matplotlib.pyplot as plt
from constants import G


def datcom(A, M, eta, half_chord_sweep):
    beta = sqrt(1 - M**2)
    C_L_alpha = (2 * pi * A) / (2 + sqrt(4 + (A * beta / eta)**2 * (1 + (tan(half_chord_sweep))**2/(beta**2))))
    return C_L_alpha


def stability_line(
    ax, max_Sh_S, M, S, S_net, b, c, quarter_chord_sweep, half_chord_sweep, taper_ratio, A_h,
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
    
    one_minus_d_eps_d_alpha = 1 - 0.10

    x_ac_f1 = (-1.8 / C_L_alpha_A_H) * (b_f * h_f * l_fn) / (S * c)
    c_g = S / b
    x_ac_f2 = (0.273 / (1 + taper_ratio)) * (b_f * c_g * (b - b_f)) / (c ** 2 * (b + 2.15 * b_f)) * tan(quarter_chord_sweep)
    x_ac_n = 2 * k_n * (b_n ** 2 * l_n) / (S * c * C_L_alpha_A_H)
    x_ac = x_ac_w + x_ac_f1 + x_ac_f2 + x_ac_n

    denom = (C_L_alpha_H / C_L_alpha_A_H * one_minus_d_eps_d_alpha * l_h / c * Vh_V ** 2)
    intercept = (x_ac - stability_margin) / denom
    slope = 1 / denom
    x_points = [x_ac - stability_margin, (max_Sh_S - intercept) / slope]
    y_points = [0, max_Sh_S]
    # breakpoint()
    ax.plot(x_points, y_points, label="Stability curve")


def controllability_line(
    ax, max_Sh_S, M, alpha_0_l, delta_alpha_0_l, C_m_0_airfoil, C_l_max, eta, S, S_prime, S_wf, c, b, b_f, h_f, l_f,
    l_h, x_ac, quarter_chord_sweep, half_chord_sweep, flap_hinge_sweep_angle, V_app, rho, W, Vh_V, c_prime, C_L_H, mu_1,
    mu_2, mu_3,
):
    A = b**2 / S
    C_L_alpha_A_H = datcom(A, M, eta, half_chord_sweep)
    alpha_0_L = alpha_0_l
    delta_alpha_0_L = delta_alpha_0_l * (S_wf / S) * cos(flap_hinge_sweep_angle)
    C_L_alpha_clean = C_L_alpha_A_H
    C_L_alpha_flapped = S_prime / S * C_L_alpha_clean
    C_L_alpha_equals_0 = radians(abs(alpha_0_L - delta_alpha_0_L)) * C_L_alpha_flapped
    
    C_m_ac_w = C_m_0_airfoil * (A * cos(quarter_chord_sweep)**2) / (A + 2*cos(quarter_chord_sweep))
    delta_fus_C_m_ac = -1.8 * (1 - 2.5*b_f/l_f) * (pi * b_f * h_f * l_f) / (4 * S * c) * (C_L_alpha_equals_0 / C_L_alpha_A_H)
    delta_nac_C_m_ac = 0

    delta_f_c_l = 1.6 * c_prime / c
    C_L = sqrt(2/rho * W/S * 1 / V_app**2)
    c_l = C_L - delta_f_c_l * (1 - S_wf / S)
    delta_f_c_m_1_4 = -mu_1 * delta_f_c_l * (c_prime / c) - c_l * (1/8) * (c_prime / c) * (c_prime / c - 1)
    delta_f_C_m_ac = mu_2 * delta_f_c_m_1_4 + 0.7 * A / (1 + 2/A) * mu_3 * delta_f_c_l * tan(quarter_chord_sweep)
    C_m_ac = C_m_ac_w + delta_f_C_m_ac + delta_fus_C_m_ac + delta_nac_C_m_ac

    delta_C_l_max = delta_f_c_l
    delta_C_L_max = 0.9 * delta_C_l_max * (S_wf / S) * cos(flap_hinge_sweep_angle)
    C_L_max_clean = 0.9 * C_l_max * cos(quarter_chord_sweep)
    C_L_max = C_L_max_clean + delta_C_L_max
    V_s = V_app / 1.3
    C_L_landing = (V_s / V_app)**2 * C_L_max
    C_L_w = C_L_landing
    C_L_A_H = C_L_w

    denom = (C_L_H / C_L_A_H) * (l_h / c) * Vh_V ** 2
    intercept = (C_m_ac / C_L_A_H - x_ac) / denom
    slope = 1 / denom
    x_points = [(max_Sh_S - intercept) / slope, -intercept / slope]
    y_points = [intercept + max_Sh_S, 0]
    ax.plot(x_points, y_points, label="Controllability curve")


def scissor_plot(
    filename, show_legend, max_Sh_S, M_cruise, S, S_net, b, mac, quarter_chord_sweep_deg, half_chord_sweep_deg,
    taper_ratio, A_h, horizontal_stab_half_chord_sweep_deg, use_torenbeek_method, eta, l_h, delta_z_wing_tail_acs, b_f,
    h_f, l_fn, b_n, l_n, c_l_des, x_ac_w_cruise, k_n, Vh_V, stability_margin, V_app_kts, alpha_0_l, delta_alpha_0_l,
    C_m_0_airfoil, C_l_max, S_prime, S_wf, l_f, x_ac_w_landing, flap_hinge_sweep_deg, rho_landing, m_landing_kg,
    delta_c_cf, cf, C_L_H, mu_1, mu_2, mu_3,
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
        x_ac_w_cruise,
        k_n,
        Vh_V,
        stability_margin,
    )

    controllability_line(
        ax,
        max_Sh_S,
        V_app_kts * 1852/3600 / sqrt(1.4 * 287 * 288.15),
        alpha_0_l,
        delta_alpha_0_l,
        C_m_0_airfoil,
        C_l_max,
        eta,
        S,
        S_prime,
        S_wf,
        mac,
        b,
        b_f,
        h_f,
        l_f,
        l_h,
        x_ac_w_landing,
        radians(quarter_chord_sweep_deg),
        radians(half_chord_sweep_deg),
        radians(flap_hinge_sweep_deg),
        V_app_kts * 1852/3600,
        rho_landing,
        m_landing_kg * G,
        Vh_V,
        mac + delta_c_cf*cf,
        C_L_H,
        mu_1,
        mu_2,
        mu_3,
    )

    if show_legend:
        ax.legend()
    ax.set_xlabel(r"$x_{cg}/\bar{c}$ [-]")
    ax.set_ylabel(r"$S_h/S$ [-]")
    fig.tight_layout()

    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    reference_aircraft_config = {
        "filename": "ref_aircraft_scissor_plot",          # filename to save to
        "show_legend": True,                              # whether to show the legend
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
        "x_ac_w_cruise": 0.445,                           # from Torenbeek figure E-10 [-]
        "k_n": -2.5,                                      # nacelle a.c. shift coefficient [-]; -2.5 for rear fuselage podded engines
        "Vh_V": 1,                                        # tail speed ratio [-]; 1 for T-tail
        "stability_margin": 0.05,                         # stability margin, in fraction m.a.c. [-]
        "V_app_kts": 130,                                 # approach speed in [kts]
        "alpha_0_l": -0.78,                               # airfoil angle of attack at which C_l = 0, [deg]
        "delta_alpha_0_l": -15,                           # change in airfoil C_l = 0 in [deg], approx. -15 deg from ADSEE II
        "C_m_0_airfoil": -0.013,                          # airfoil C_m when C_l = 0, [-]
        "C_l_max": 1.618,                                 # airfoil max C_l, [-]
        "S_prime": 98.2905,                               # entire surface of new wing when flaps are extended, should be >S, [m]
        "S_wf": 26.8456 * 2,                              # portion of unflapped wing in front of flaps, should be <S, [m]
        "l_f": 32.501,                                    # fuselage length [m]
        "x_ac_w_landing": 0.355,                          # from Torenbeek figure E-10 [-]
        "flap_hinge_sweep_deg": 6.59,                     # sweep of flap hinge line, [deg]
        "rho_landing": 1.225,                             # air density at landing, [kg/m^3]
        "m_landing_kg": 39915,                            # landing mass in [kg]
        "delta_c_cf": 0.79,                               # read from Torenbeek fig. G-7 [-]
        "cf": 1.250,                                      # flap chord as shown in Torenbeek fig. G-7, [m]
        "C_L_H": -0.85,                                   # C_L of the tail at landing, -0.85 for adjustable tails [-]
        "mu_1": 0.12,                                     # from Torenbeek fig. G-15
        "mu_2": 0.78,                                     # from Torenbeek fig. G-16
        "mu_3": 0.0575,                                   # from Torenbeek fig. G-17
    }
    scissor_plot(**reference_aircraft_config)
