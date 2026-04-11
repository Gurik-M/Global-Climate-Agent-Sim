import os
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d

mpl.rcParams.update({
        "text.usetex": False,
        "mathtext.fontset": "cm",
        "font.family": "serif",
        "font.size": 11,
        "legend.fontsize": 9
    })

# =======================================================
# Get predicted anthropogenic emissions from .json file

def get_anthropogenic_predictions(filename):
    with open(filename, 'r') as file:
        emissions_data = json.load(file)

    return pd.DataFrame(emissions_data['global_emissions_by_step'])


def process_emissions(emissions_dataframe):
    start_year = emissions_dataframe['year'].iloc[0]
    time_years = emissions_dataframe['year'] - start_year

    energy_heat     = emissions_dataframe['energy_heat']
    transport       = emissions_dataframe['transport']
    buildings       = emissions_dataframe['buildings']
    industry        = emissions_dataframe['industry']
    deforestation   = emissions_dataframe['deforestation']
    agriculture     = emissions_dataframe['agriculture']
    carbon_removal  = emissions_dataframe['carbon_removal']
    ff_total        = (energy_heat + transport + buildings + industry) / 4
    land_use        = (deforestation + agriculture) / 2

    E_fossilfuels   = interp1d(time_years, ff_total, fill_value="extrapolate")
    E_land_use      = interp1d(time_years, land_use, fill_value="extrapolate")
    R_ind_removal   = interp1d(time_years, carbon_removal, fill_value="extrapolate")

    simulated_data  = [E_fossilfuels, E_land_use, R_ind_removal]

    return simulated_data


# =======================================================
# Define system of ODEs

def climate_model(t, y, simulated_data, initial_emissions):
    """
    State vector y:
    y[0] = C_A: Atmospheric Carbon (GtC)
    y[1] = C_B: Biosphere Carbon (GtC)
    y[2] = C_O: Ocean Carbon (GtC)
    y[3] = T_S: Global Surface Temp Anomaly (deg C)
    y[4] = T_O: Ocean Temp Anomaly (deg C)
    """

    C_atmosphere, C_biosphere, C_ocean, T_surface, T_ocean = y
    E_fossilfuels, E_land_use, R_ind_removal = simulated_data
    E_ff_init, E_luc_init, R_ind_init = initial_emissions

    # Physical parameters
    C_A0        = 589.0     # Pre-industrial atmospheric carbon (GtC)
    S           = 1361.0    # Solar constant (W/m^2)
    alpha_0     = 0.3
    A_polar     = 0.07

    # Heat capacities & feedbacks
    C_s         = 8.0       # Surface heat capacity (W*yr/m^2/K)
    C_o         = 120.0     # Ocean heat capacity
    lambda_fb   = 1.3       # Climate feedback parameter (W/m^2/C)
    gamma       = 0.77      # Heat exchange rate between surface and ocean

    # Human inputs (from CSVs)
    E_ff        = max(0, E_fossilfuels(t)) * E_ff_init + 2.55
    E_luc       = max(0, E_land_use(t)) * E_luc_init
    R_ind       = max(0, R_ind_removal(t)) * R_ind_init

    # Natural carbon fluxes (GtC/yr)
    F_volc      = 0.1
    F_photo     = 120.0 * (1 + 0.35 * np.log(C_atmosphere / C_A0))
    F_resp      = 120.0 * (C_biosphere / 2000.0) * (1 + 0.05 * T_surface)
    F_wf        = 3.4 * (C_biosphere / 2000.0) * (1 + 0.1 * T_surface)
    F_perma     = 0.25 * max(0, T_surface)
    F_ocean     = 2.5 * (C_atmosphere / C_A0) * (1 - C_ocean / (45000.0 * (1 - 0.02 * T_ocean)))
    F_algae     = 0.95

    # Energy & temperature dynamics
    RF_CO2      = 5.35 * np.log(C_atmosphere / C_A0)  # CO2 forcing factor

    # Albedo forcing factor
    def calc_alpha(T, alpha0, alphai=0.5, deltaT=10.):
        if T < - deltaT:
            return alphai
        elif -deltaT <= T < 2 * deltaT:
            return alphai + (alpha0 - alphai) * (T + 14) / (3 * deltaT)
        elif T >= 2 * deltaT:
            return alpha0

    alpha       = calc_alpha(T_surface + 14, alpha_0)
    RF_alpha    = (S / 4.0) * (alpha_0 - alpha) * A_polar

    # Calculate differentials
    dC_A_dt     = E_ff + E_luc + F_volc + F_wf + F_resp + F_perma - F_photo - R_ind - F_ocean
    dC_B_dt     = F_photo - F_resp - F_wf - E_luc
    dC_O_dt     = F_ocean + F_algae

    dT_S_dt     = (RF_CO2 + RF_alpha - lambda_fb * T_surface - gamma * (T_surface - T_ocean)) / C_s
    dT_O_dt     = (gamma * (T_surface - T_ocean)) / C_o

    return [dC_A_dt, dC_B_dt, dC_O_dt, dT_S_dt, dT_O_dt]


# =======================================================
# Define solver

# Initial Conditions (convert from GtCO2 to GtC)
E_energy        = 8.653 / 3.67
E_transport     = 4.734 / 3.67
E_buildings     = 4.000 / 3.67
E_industry      = 1.004 / 3.67
E_land_use      = 4.976 / 3.67
R_ind_removal   = 0.0

C_atmosphere    = 750.0
C_biosphere     = 2000.0
C_ocean         = 38000.0
T_surface       = 0.6
T_ocean         = 0.3

init_emissions  = [E_energy + E_transport + E_buildings + E_industry, E_land_use, R_ind_removal]
y0              = [C_atmosphere, C_biosphere, C_ocean, T_surface, T_ocean]

# Evaluate monthly for 100 years
t_span          = (0, 110)
t_eval          = np.linspace(t_span[0], t_span[1], t_span[1] * 12)

# Setup
# filename        = 'Agent Results/climate_protect.json'
filename        = 'Agent Results/standard_results.json'
emissions_df    = get_anthropogenic_predictions(filename)
sim_emissions   = process_emissions(emissions_df)

# Solve the ODEs
solution = solve_ivp(climate_model, t_span, y0, t_eval=t_eval, method='RK45', args=[sim_emissions, init_emissions])

# Extract results
time            = solution.t
calendar_years  = time + 1990  # 1) Shift x-axis to start at 1990

C_A_out         = solution.y[0]
T_S_out         = solution.y[3]
T_O_out         = solution.y[4]

# Convert GtC back to ppm for atmospheric CO2
CO2_ppm         = C_A_out / 2.12

# Normalize CO2 relative to the initial concentration
CO2_normalized  = C_A_out / C_A_out[0]

# Calculate and normalize total human emissions
E_ff_func, E_luc_func, R_ind_func = sim_emissions
E_ff_init, E_luc_init, R_ind_init = init_emissions

# Evaluate the interpolated emission functions at every time step
total_emissions = np.array([
    max(0, E_ff_func(t)) * E_ff_init + max(0, E_luc_func(t)) * E_luc_init
    for t in time
])

# Normalize relative to the emissions at t=0
emissions_normalized = total_emissions / total_emissions[0]

# =======================================================
# Plotting

# Get IPCC data
ipcc_ppm        = pd.read_csv('ipcc_concentrations.csv', header=0)
ipcc_temps      = pd.read_csv('ipcc_temperatures.csv', header=0)
years           = ipcc_ppm['Year']
colors          = ['dodgerblue', 'limegreen', 'goldenrod', 'orangered', 'maroon']
ipcc_scenarios  = ['SSP1 - Baseline', 'SSP2 - Baseline', 'SSP3 - Baseline', 'SSP4 - Baseline', 'SSP5 - Baseline']

fig, ax = plt.subplots(2, 1, figsize=(8, 8))

# Plot temperatures
ax[0].set_xlabel('Year')
ax[0].set_ylabel('Global Temp Anomaly (°C)', color='black')
ax[0].plot(calendar_years, T_S_out, color='red', linewidth=1.5, label='Surface Temp ($T_S$)')
ax[0].plot(calendar_years, T_O_out, color='mediumblue', linewidth=1.5, linestyle='-', label='Ocean Temp ($T_O$)')

for ipcc_scenario, color in zip(ipcc_scenarios, colors):
    ax[0].plot(years, ipcc_temps[ipcc_scenario], color=color, linewidth=1, linestyle='--', label=ipcc_scenario)

ax[0].tick_params(axis='y', labelcolor='black')
ax[0].set_ylim(0)
ax[0].grid(True, alpha=0.3)
ax[0].legend()

# Plot normalized CO2 levels
initial_ppm = 354.45  # CO2 ppm atmospheric concentration in 1990

ax[1].plot(calendar_years, CO2_normalized, color='tab:blue', linewidth=1.5, linestyle='-', label='Atmospheric CO$_2$')
ax[1].plot(calendar_years, emissions_normalized, color='tab:green', linewidth=1.5, linestyle='-', label='Human Emissions')

for ipcc_scenario, color in zip(ipcc_scenarios, colors):
    ax[1].plot(years, ipcc_ppm[ipcc_scenario] / initial_ppm, color=color, linewidth=1, linestyle='--', label=ipcc_scenario)

ax[1].set_xlabel('Year')
ax[1].set_ylabel('Normalized CO2 Values (Relative to 1990)', color='tab:green')
ax[1].tick_params(axis='y', labelcolor='tab:green')
ax[1].grid(True, alpha=0.3)
ax[1].legend()

def norm_to_ppm(norm_val):
    return norm_val * initial_ppm

def ppm_to_norm(ppm_val):
    return ppm_val / initial_ppm


sec_ax_ppm = ax[1].secondary_yaxis('right', functions=(norm_to_ppm, ppm_to_norm))
sec_ax_ppm.set_ylabel('Atmospheric CO$_2$ (ppm)', color='tab:blue')
sec_ax_ppm.tick_params(axis='y', labelcolor='tab:blue')

fig.suptitle('Simulated Global Temperature, CO$_2$, and Emissions (1990-2100)', fontsize=14)
fig.tight_layout()
plt.savefig('Project Figures/1990-2100_Global-Temp-and-CO2_Comparison.png', dpi=300)
plt.show()
