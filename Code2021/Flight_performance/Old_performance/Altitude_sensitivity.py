import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as opt

plt.rcParams.update({'font.size': 16})
h = np.array([ 300, 400, 500, 600, 700, 800, 900,1000,1100,1200,1300,1400,1500,1600,
 1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900])
E1 = np.array([426.33227907311414, 428.1321841680682, 429.93254788727734, 431.73337284973326, 433.5346616893239, 435.3364170549424, 437.138641610595, 438.941338035511, 440.74450902425286, 442.54815728682854, 444.3522855488021, 446.1568965514085, 447.96199305166675, 449.76757782249524, 451.573653652828, 453.38022334773126, 455.18728972852136, 456.99485563288437, 458.80292391499484, 460.6114974456373, 462.42057911232877, 464.2301718194401, 466.0402784883212, 467.8509020574251, 469.66204548243496, 471.4737117363901, 473.28590380981456])
E2 = np.array([562.7193433496448, 564.6957239995497, 566.67259610923, 568.6499624876279, 570.62782595966, 572.6061893663301, 574.5850555648481, 576.564427428746, 578.5443078479971, 580.5246997291351, 582.505605995375, 584.4870295867338, 586.468973460153, 588.451440589623, 590.434433966306, 592.4179565986623, 594.4020115125768, 596.3866017514865, 598.3717303765087, 600.3574004665709, 602.3436151185412, 604.3303774473607, 606.317690586176, 608.3055576864731, 610.2939819182128, 612.2829664699664, 614.2725145490539])
E3 = np.array([379.4191576501699, 381.114278533891, 382.8098030645582, 384.50573359352927, 386.20207248543323, 387.8988221182664, 389.5959848834901, 391.29356318612895, 392.9915594448693, 394.6899760921593, 396.38881557430943, 398.0880803515936, 399.78777289835136, 401.4878957030917, 403.18845126859566, 404.8894421120222, 406.59087076501294, 408.2927397737991, 409.99505169930893, 411.6978091172753, 413.40101461834536, 415.1046708081905, 416.8087803076174, 418.513345752679, 420.21836979478854, 421.9238551008325, 423.6298043532856])

energies = np.vstack((np.vstack((E1, E2)), E3))

def f(x, a, b):
    return a*x + b

# Loop through the energies of all concepts
for i in range(3):

    # Select the correct energies
    E = energies[i, :]

    # Fit a curve
    vals, _ = opt.curve_fit(f, h, E)

    # Print results
    title = 'f(x) = ' + str(np.round(vals[0], 4)) + 'x + ' + str(np.round(vals[1], 3))

    fit = f(h, vals[0], vals[1])
    plt.plot(h, fit, label = 'Curve fit')
    plt.plot(h, E, 'x', label = 'Simulation')
    plt.title(title)
    plt.xlabel('Cruising Altitude [m]')
    plt.ylabel('Required Energy [MJ]')
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Save the figure
    path = 'C:/Users/Egon Beyne/Desktop/DSE/Plots/Energy_altitude_' + str(i + 1) + '.pdf'
    plt.savefig(path)

    plt.show()




