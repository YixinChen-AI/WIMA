from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _matrix(values: object, name: str) -> FloatArray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a two-dimensional array")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def _vector(values: object, name: str, length: int) -> FloatArray:
    array = np.asarray(values, dtype=float).reshape(-1)
    if array.size != length:
        raise ValueError(f"{name} must contain {length} values")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


@dataclass(frozen=True)
class ReferenceMetabolicGraph:
    demographic_coefficients: FloatArray
    intercept: FloatArray
    slope: FloatArray
    residual_standard_error: FloatArray
    predictor_mean: FloatArray
    predictor_sum_squares: FloatArray
    reliability_weight: FloatArray
    n_controls: int
    roi_names: tuple[str, ...]

    def adjust(
        self,
        raw_uptake: object,
        age: object,
        sex: object,
    ) -> FloatArray:
        uptake = _matrix(raw_uptake, "raw_uptake")
        if uptake.shape[1] != len(self.roi_names):
            raise ValueError("raw_uptake has a different number of ROIs")

        age_vector = _vector(age, "age", uptake.shape[0])
        sex_vector = _vector(sex, "sex", uptake.shape[0])
        design = np.column_stack(
            (np.ones(uptake.shape[0]), age_vector, sex_vector)
        )
        return uptake - design @ self.demographic_coefficients

    def transform(
        self,
        raw_uptake: object,
        age: object,
        sex: object,
    ) -> FloatArray:
        adjusted = self.adjust(raw_uptake, age, sex)

        predicted = (
            self.intercept[None, :, :]
            + self.slope[None, :, :] * adjusted[:, None, :]
        )
        error = adjusted[:, :, None] - predicted

        leverage = (
            1.0
            + 1.0 / self.n_controls
            + (
                adjusted[:, None, :]
                - self.predictor_mean[None, None, :]
            )
            ** 2
            / self.predictor_sum_squares[None, None, :]
        )

        rse = self.residual_standard_error.copy()
        diagonal = np.arange(rse.shape[0])
        rse[diagonal, diagonal] = np.inf

        standardized = error / (
            rse[None, :, :] * np.sqrt(leverage)
        )
        standardized[:, diagonal, diagonal] = 0.0

        imd = np.sqrt(
            0.5
            * (
                standardized**2
                + standardized.transpose(0, 2, 1) ** 2
            )
        )
        imd[:, diagonal, diagonal] = 0.0
        return imd


def fit_reference_metabolic_graph(
    control_uptake: object,
    age: object,
    sex: object,
    roi_names: Sequence[str] | None = None,
    reliability_epsilon: float = 1e-6,
) -> ReferenceMetabolicGraph:
    uptake = _matrix(control_uptake, "control_uptake")
    n_controls, n_rois = uptake.shape

    if n_controls < 4:
        raise ValueError("at least four controls are required")
    if n_rois < 2:
        raise ValueError("at least two ROIs are required")
    if reliability_epsilon <= 0:
        raise ValueError("reliability_epsilon must be positive")

    age_vector = _vector(age, "age", n_controls)
    sex_vector = _vector(sex, "sex", n_controls)

    design = np.column_stack(
        (np.ones(n_controls), age_vector, sex_vector)
    )
    demographic_coefficients = np.linalg.lstsq(
        design,
        uptake,
        rcond=None,
    )[0]
    adjusted = uptake - design @ demographic_coefficients

    predictor_mean = adjusted.mean(axis=0)
    centered = adjusted - predictor_mean
    predictor_sum_squares = np.sum(centered**2, axis=0)

    if np.any(
        predictor_sum_squares <= np.finfo(float).eps
    ):
        raise ValueError(
            "each ROI must vary among the training controls"
        )

    intercept = np.zeros((n_rois, n_rois), dtype=float)
    slope = np.zeros((n_rois, n_rois), dtype=float)
    residual_standard_error = np.full(
        (n_rois, n_rois),
        np.nan,
        dtype=float,
    )

    for target in range(n_rois):
        for predictor in range(n_rois):
            if target == predictor:
                continue

            slope[target, predictor] = (
                np.dot(
                    centered[:, predictor],
                    centered[:, target],
                )
                / predictor_sum_squares[predictor]
            )
            intercept[target, predictor] = (
                predictor_mean[target]
                - slope[target, predictor]
                * predictor_mean[predictor]
            )

            residual = adjusted[:, target] - (
                intercept[target, predictor]
                + slope[target, predictor]
                * adjusted[:, predictor]
            )
            rse = np.sqrt(
                np.sum(residual**2) / (n_controls - 2)
            )

            if rse <= np.finfo(float).eps:
                raise ValueError(
                    "a directed edge has zero residual uncertainty"
                )

            residual_standard_error[
                target,
                predictor,
            ] = rse

    reliability_weight = 1.0 / (
        0.5
        * (
            residual_standard_error**2
            + residual_standard_error.T**2
        )
        + reliability_epsilon
    )

    diagonal = np.arange(n_rois)
    reliability_weight[diagonal, diagonal] = 0.0

    names = (
        tuple(roi_names)
        if roi_names is not None
        else tuple(f"ROI_{index}" for index in range(n_rois))
    )

    if len(names) != n_rois or len(set(names)) != n_rois:
        raise ValueError(
            "roi_names must contain one unique name per ROI"
        )

    return ReferenceMetabolicGraph(
        demographic_coefficients=demographic_coefficients,
        intercept=intercept,
        slope=slope,
        residual_standard_error=residual_standard_error,
        predictor_mean=predictor_mean,
        predictor_sum_squares=predictor_sum_squares,
        reliability_weight=reliability_weight,
        n_controls=n_controls,
        roi_names=names,
    )


def aggregate_subnetwork_fingerprints(
    imd: object,
    reliability_weight: object,
    subnetwork_labels: Sequence[str],
) -> tuple[FloatArray, tuple[str, ...]]:
    matrices = np.asarray(imd, dtype=float)

    if matrices.ndim == 2:
        matrices = matrices[None, :, :]

    if (
        matrices.ndim != 3
        or matrices.shape[1] != matrices.shape[2]
    ):
        raise ValueError(
            "imd must have shape (subjects, ROIs, ROIs)"
        )

    if not np.isfinite(matrices).all():
        raise ValueError("imd contains non-finite values")

    weights = _matrix(
        reliability_weight,
        "reliability_weight",
    )

    if weights.shape != matrices.shape[1:]:
        raise ValueError(
            "reliability_weight has an incompatible shape"
        )

    labels = tuple(str(label) for label in subnetwork_labels)

    if len(labels) != matrices.shape[1]:
        raise ValueError(
            "subnetwork_labels must contain one label per ROI"
        )

    subnetworks = tuple(dict.fromkeys(labels))
    label_array = np.asarray(labels)
    columns: list[FloatArray] = []
    names: list[str] = []

    for subnetwork in subnetworks:
        indices = np.flatnonzero(
            label_array == subnetwork
        )

        if indices.size < 2:
            continue

        local_row, local_col = np.triu_indices(
            indices.size,
            k=1,
        )
        row = indices[local_row]
        col = indices[local_col]

        edge_weight = weights[row, col]
        weight_sum = edge_weight.sum()

        if weight_sum <= 0:
            raise ValueError(
                f"subnetwork {subnetwork} has no positive edge weight"
            )

        edge_value = np.abs(matrices[:, row, col])
        magnitude = np.sum(
            edge_value * edge_weight,
            axis=1,
        ) / weight_sum

        heterogeneity = np.sqrt(
            np.sum(
                edge_weight
                * (edge_value - magnitude[:, None]) ** 2,
                axis=1,
            )
            / weight_sum
        )

        columns.extend((magnitude, heterogeneity))
        names.extend(
            (
                f"Delta_w[{subnetwork}]",
                f"Sigma_w[{subnetwork}]",
            )
        )

    for first_index, first in enumerate(subnetworks):
        first_rois = np.flatnonzero(
            label_array == first
        )

        for second in subnetworks[first_index + 1 :]:
            second_rois = np.flatnonzero(
                label_array == second
            )

            row = np.repeat(
                first_rois,
                second_rois.size,
            )
            col = np.tile(
                second_rois,
                first_rois.size,
            )

            edge_weight = weights[row, col]
            weight_sum = edge_weight.sum()

            if weight_sum <= 0:
                raise ValueError(
                    f"subnetwork pair ({first}, {second}) "
                    "has no positive edge weight"
                )

            edge_value = np.abs(matrices[:, row, col])
            magnitude = np.sum(
                edge_value * edge_weight,
                axis=1,
            ) / weight_sum

            columns.append(magnitude)
            names.append(
                f"Gamma_w[{first},{second}]"
            )

    if not columns:
        raise ValueError(
            "subnetwork labels do not define any features"
        )

    return np.column_stack(columns), tuple(names)
