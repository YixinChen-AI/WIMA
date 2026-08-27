import numpy as np

from imd import (
    aggregate_subnetwork_fingerprints,
    fit_reference_metabolic_graph,
)


def make_outputs():
    rng = np.random.default_rng(7)

    n_controls = 50
    n_targets = 5
    n_rois = 6

    control_age = rng.normal(70, 6, n_controls)
    control_sex = rng.integers(0, 2, n_controls)
    control_latent = rng.normal(size=(n_controls, 1))

    loadings = np.array(
        [0.8, 0.6, -0.5, -0.4, 0.3, 0.2]
    )

    control_uptake = (
        2.0
        + 0.01 * control_age[:, None]
        + 0.05 * control_sex[:, None]
        + control_latent * loadings
        + rng.normal(0, 0.2, (n_controls, n_rois))
    )

    model = fit_reference_metabolic_graph(
        control_uptake,
        control_age,
        control_sex,
    )

    target_age = rng.normal(72, 5, n_targets)
    target_sex = rng.integers(0, 2, n_targets)
    target_latent = rng.normal(size=(n_targets, 1))

    target_uptake = (
        2.0
        + 0.01 * target_age[:, None]
        + 0.05 * target_sex[:, None]
        + target_latent * loadings
        + rng.normal(0, 0.2, (n_targets, n_rois))
    )
    target_uptake[:, 1] += 0.6

    imd = model.transform(
        target_uptake,
        target_age,
        target_sex,
    )

    labels = (
        "Network-A",
        "Network-A",
        "Network-B",
        "Network-B",
        "Network-C",
        "Network-C",
    )

    fingerprints, names = (
        aggregate_subnetwork_fingerprints(
            imd,
            model.reliability_weight,
            labels,
        )
    )

    return model, imd, fingerprints, names


def test_imd_matrices():
    model, imd, _, _ = make_outputs()

    assert imd.shape == (5, 6, 6)
    assert np.isfinite(imd).all()
    assert np.allclose(
        imd,
        imd.transpose(0, 2, 1),
    )
    assert np.allclose(
        np.diagonal(imd, axis1=1, axis2=2),
        0.0,
    )
    assert np.allclose(
        model.reliability_weight,
        model.reliability_weight.T,
        equal_nan=True,
    )
    assert np.allclose(
        np.diag(model.reliability_weight),
        0.0,
    )


def test_subnetwork_fingerprints():
    _, _, fingerprints, names = make_outputs()

    assert fingerprints.shape == (5, 9)
    assert len(names) == 9
    assert np.isfinite(fingerprints).all()
    assert names == (
        "Delta_w[Network-A]",
        "Sigma_w[Network-A]",
        "Delta_w[Network-B]",
        "Sigma_w[Network-B]",
        "Delta_w[Network-C]",
        "Sigma_w[Network-C]",
        "Gamma_w[Network-A,Network-B]",
        "Gamma_w[Network-A,Network-C]",
        "Gamma_w[Network-B,Network-C]",
    )
