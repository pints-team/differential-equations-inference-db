"""Script for running the model.
"""

import numpy as np
import matplotlib.pyplot as plt
import pints
import pints.plot
import pystreamflow


def run_inference(optimize=False):
    # Load data and model
    data = pystreamflow.load_data('03451500')

    precip = data['precipitation'].to_numpy()[365:]
    evap = data['evaporation'].to_numpy()[365:]
    flow = data['streamflow'].to_numpy()[365:]
    all_times = np.arange(len(precip))
    m = pystreamflow.RiverModel(all_times, precip, evap, solver='scikit')

    # Time range for data
    data_times = all_times[730:1095]
    data_flow = flow[730:1095]

    # Build prior
    I_max_prior = pints.UniformLogPrior(0, 10)
    S_umax_prior = pints.UniformLogPrior(10, 1000)
    Q_smax_prior = pints.UniformLogPrior(0, 100)
    alpha_e_prior = pints.UniformLogPrior(0, 100)
    alpha_f_prior = pints.UniformLogPrior(-10, 10)
    K_s_prior = pints.UniformLogPrior(0, 150)
    K_f_prior = pints.UniformLogPrior(0, 10)
    sigma_prior = pints.UniformLogPrior(0, 1e6)

    # Good parameter values
    params = [9.0, 200.0, 7.0, 85.0, 0.2, 70.0, 2.5, 1.0]

    # Make objects for pints
    problem = pints.SingleOutputProblem(m, data_times, data_flow)
    likelihood = pints.GaussianLogLikelihood(problem)
    prior = pints.ComposedLogPrior(
        I_max_prior,
        S_umax_prior,
        Q_smax_prior,
        alpha_e_prior,
        alpha_f_prior,
        K_s_prior,
        K_f_prior,
        sigma_prior
    )
    posterior = pints.LogPosterior(likelihood, prior)

    if optimize:
        opt = pints.OptimisationController(
            posterior, params, method=pints.SNES)
        opt.set_parallel(True)
        opt.set_max_iterations(10)
        p, _ = opt.run()
        p = params

        # Plot results
        y = m.simulate(p[:-1], data_times)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(data_times, y, label='Fit')
        ax.plot(
            data_times, data_flow, 'x-', label='Data', color='k', alpha=0.5)
        ax.set_xlabel('Time (days)')
        ax.legend()
        plt.show()

    else:
        mcmc = pints.MCMCController(
            posterior, 6, [params]*6, method=pints.DreamMCMC)
        mcmc.set_max_iterations(10)
        mcmc.set_parallel(True)
        chains = mcmc.run()

        pints.plot.trace(chains)
        plt.show()

        pints.plot.pairwise(chains[0, :, :], kde=True)
        plt.show()


def plot_likelihood():
    # Load data and model
    data = pystreamflow.load_data('03451500')

    precip = data['precipitation'].to_numpy()[365:]
    evap = data['evaporation'].to_numpy()[365:]
    flow = data['streamflow'].to_numpy()[365:]
    all_times = np.arange(len(precip))
    m = pystreamflow.RiverModel(
        all_times, precip, evap, solver='scipy', rtol=1e-3, atol=1e-3)
    m_accurate = pystreamflow.RiverModel(
        all_times, precip, evap, solver='scikit')

    # Time range for data
    data_times = all_times[730:1095]
    data_flow = flow[730:1095]

    # Make objects for pints
    problem = pints.SingleOutputProblem(m, data_times, data_flow)
    likelihood = pints.GaussianLogLikelihood(problem)

    problem_accurate = pints.SingleOutputProblem(
        m_accurate, data_times, data_flow)
    likelihood_accurate = pints.GaussianLogLikelihood(problem_accurate)

    # Other parameters
    params = [9.0, 200.0, 7.0, 85.0, 0.2, 70.0, 2.5, 1.0]

    # Get a slice of the likelihood
    q_range = np.linspace(6.0, 10.0, 50)
    lls = []
    lls_accurate = []
    for q in q_range:
        params[2] = q
        lls.append(likelihood(params))
        lls_accurate.append(likelihood_accurate(params))

    plt.plot(q_range, lls, label='RK23 tol=1e-3')
    plt.plot(q_range, lls_accurate, label='CVODE tol=1e-7')
    plt.legend()
    plt.xlabel('Q_s,max')
    plt.ylabel('Log likelihood')
    plt.show()


if __name__ == '__main__':
    plot_likelihood()
    run_inference(optimize=False)
