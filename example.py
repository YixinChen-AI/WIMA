import numpy as np

from imd import (
    aggregate_subnetwork_fingerprints,
    fit_reference_metabolic_graph,
)


def main() -> None:
    rng = np.random.default_rng(42)

    n_controls = 60
    n_targets = 8
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

    subnetwork_labels = (
        "Network-A",
        "Network-A",
        "Network-B",
        "Network-B",
        "Network-C",
        "Network-C",
    )

    fingerprints, feature_names = (
        aggregate_subnetwork_fingerprints(
            imd,
            model.reliability_weight,
            subnetwork_labels,
        )
    )

    print("IMD matrix shape:", imd.shape)
    print("Fingerprint shape:", fingerprints.shape)

    for name, value in zip(
        feature_names,
        fingerprints[0],
    ):
        print(f"{name}: {value:.4f}")


if __name__ == "__main__":
    main()
