from __future__ import annotations

import random
from copy import deepcopy
from typing import Any


ENGINE_FAMILY_ENCODING = {
    "honda_k": 0.18,
    "toyota_jz": 0.36,
    "gm_ls": 0.57,
    "ford_coyote": 0.68,
    "nissan_rb": 0.74,
    "subaru_ej": 0.82,
    "mazda_renesis": 0.91,
    "bmw_s": 0.65,
    "bmw_b": 0.66,
}


BASE_ENGINES: list[dict[str, Any]] = [
    {"code": "K20A", "name": "Honda K20A", "family": "honda_k", "layout": "transverse", "displacement_l": 2.0, "cylinders": 4, "compression_ratio": 11.5, "engine_weight_kg": 183, "base_hp": 220, "base_torque_nm": 206, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 660, "image": "/k20a.webp"},
    {"code": "K24A", "name": "Honda K24A", "family": "honda_k", "layout": "transverse", "displacement_l": 2.4, "cylinders": 4, "compression_ratio": 10.5, "engine_weight_kg": 189, "base_hp": 205, "base_torque_nm": 231, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 690, "image": "/k20a.webp"},
    {"code": "2JZ_GTE", "name": "Toyota 2JZ-GTE", "family": "toyota_jz", "layout": "longitudinal", "displacement_l": 3.0, "cylinders": 6, "compression_ratio": 8.5, "engine_weight_kg": 255, "base_hp": 320, "base_torque_nm": 427, "forced_induction": 1, "fuel_type": "gasoline", "donor_mount_width_mm": 760, "image": "/2jz.webp"},
    {"code": "LS3", "name": "GM LS3 V8", "family": "gm_ls", "layout": "longitudinal", "displacement_l": 6.2, "cylinders": 8, "compression_ratio": 10.7, "engine_weight_kg": 205, "base_hp": 430, "base_torque_nm": 575, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 730, "image": "/ls3.webp"},
    {"code": "COYOTE_50", "name": "Ford Coyote 5.0", "family": "ford_coyote", "layout": "longitudinal", "displacement_l": 5.0, "cylinders": 8, "compression_ratio": 12.0, "engine_weight_kg": 202, "base_hp": 460, "base_torque_nm": 570, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 780, "image": "/coyote_50.webp"},
    {"code": "RB26DETT", "name": "Nissan RB26DETT", "family": "nissan_rb", "layout": "longitudinal", "displacement_l": 2.6, "cylinders": 6, "compression_ratio": 8.5, "engine_weight_kg": 260, "base_hp": 276, "base_torque_nm": 353, "forced_induction": 1, "fuel_type": "gasoline", "donor_mount_width_mm": 748, "image": "/rb26dett.webp"},
    {"code": "EJ257", "name": "Subaru EJ257", "family": "subaru_ej", "layout": "longitudinal", "displacement_l": 2.5, "cylinders": 4, "compression_ratio": 8.2, "engine_weight_kg": 180, "base_hp": 305, "base_torque_nm": 393, "forced_induction": 1, "fuel_type": "gasoline", "donor_mount_width_mm": 720, "image": "/engine_img.webp"},
    {"code": "13B_MSP", "name": "Mazda 13B Renesis", "family": "mazda_renesis", "layout": "longitudinal", "displacement_l": 1.3, "cylinders": 2, "compression_ratio": 10.0, "engine_weight_kg": 130, "base_hp": 232, "base_torque_nm": 216, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 640, "image": "/engine_img.webp"},
    {"code": "S54B32", "name": "BMW S54B32", "family": "bmw_s", "layout": "longitudinal", "displacement_l": 3.2, "cylinders": 6, "compression_ratio": 11.5, "engine_weight_kg": 217, "base_hp": 333, "base_torque_nm": 355, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 710, "image": "/engine_img.webp"},
    {"code": "B58B30", "name": "BMW B58B30", "family": "bmw_b", "layout": "longitudinal", "displacement_l": 3.0, "cylinders": 6, "compression_ratio": 11.0, "engine_weight_kg": 190, "base_hp": 382, "base_torque_nm": 500, "forced_induction": 1, "fuel_type": "gasoline", "donor_mount_width_mm": 720, "image": "/engine_img.webp"},
    {"code": "K20C1", "name": "Honda K20C1", "family": "honda_k", "layout": "transverse", "displacement_l": 2.0, "cylinders": 4, "compression_ratio": 9.8, "engine_weight_kg": 185, "base_hp": 315, "base_torque_nm": 400, "forced_induction": 1, "fuel_type": "gasoline", "donor_mount_width_mm": 670, "image": "/k20a.webp"},
    {"code": "SR20DET", "name": "Nissan SR20DET", "family": "nissan_rb", "layout": "longitudinal", "displacement_l": 2.0, "cylinders": 4, "compression_ratio": 8.5, "engine_weight_kg": 149, "base_hp": 250, "base_torque_nm": 274, "forced_induction": 1, "fuel_type": "gasoline", "donor_mount_width_mm": 680, "image": "/k20a.webp"},
    {"code": "LS7", "name": "GM LS7 V8", "family": "gm_ls", "layout": "longitudinal", "displacement_l": 7.0, "cylinders": 8, "compression_ratio": 11.0, "engine_weight_kg": 208, "base_hp": 505, "base_torque_nm": 637, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 740, "image": "/ls3.webp"},
    {"code": "F20C", "name": "Honda F20C", "family": "honda_k", "layout": "longitudinal", "displacement_l": 2.0, "cylinders": 4, "compression_ratio": 11.7, "engine_weight_kg": 148, "base_hp": 240, "base_torque_nm": 220, "forced_induction": 0, "fuel_type": "gasoline", "donor_mount_width_mm": 670, "image": "/k20a.webp"},
]


CHASSIS: list[dict[str, Any]] = [
    {"code": "MX5_NA", "name": "Mazda MX-5 NA", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 970, "stock_hp": 116, "engine_bay_width_mm": 720, "wheelbase_mm": 2265, "drag_coefficient": 0.38, "stock_gear_ratio": 4.10, "cooling_capacity_index": 0.60, "suspension_index": 0.58, "tire_grip_index": 0.62, "image": "/mx5_na.webp"},
    {"code": "CIVIC_EK", "name": "Honda Civic EK", "layout": "transverse", "drivetrain": "FWD", "recipient_weight_kg": 1080, "stock_hp": 127, "engine_bay_width_mm": 700, "wheelbase_mm": 2620, "drag_coefficient": 0.34, "stock_gear_ratio": 4.25, "cooling_capacity_index": 0.62, "suspension_index": 0.56, "tire_grip_index": 0.58, "image": "/civic_ek.webp"},
    {"code": "BRZ_ZC6", "name": "Subaru BRZ / Toyota 86", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1250, "stock_hp": 200, "engine_bay_width_mm": 755, "wheelbase_mm": 2570, "drag_coefficient": 0.29, "stock_gear_ratio": 4.10, "cooling_capacity_index": 0.68, "suspension_index": 0.71, "tire_grip_index": 0.70, "image": "/brz.webp"},
    {"code": "S13_240SX", "name": "Nissan 240SX S13", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1220, "stock_hp": 140, "engine_bay_width_mm": 780, "wheelbase_mm": 2475, "drag_coefficient": 0.33, "stock_gear_ratio": 4.08, "cooling_capacity_index": 0.64, "suspension_index": 0.66, "tire_grip_index": 0.63, "image": "/s13.webp"},
    {"code": "E36_325", "name": "BMW E36 325i", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1380, "stock_hp": 189, "engine_bay_width_mm": 790, "wheelbase_mm": 2700, "drag_coefficient": 0.32, "stock_gear_ratio": 3.91, "cooling_capacity_index": 0.70, "suspension_index": 0.68, "tire_grip_index": 0.66, "image": "/e36.webp"},
    {"code": "WRX_GD", "name": "Subaru WRX GD", "layout": "longitudinal", "drivetrain": "AWD", "recipient_weight_kg": 1420, "stock_hp": 227, "engine_bay_width_mm": 760, "wheelbase_mm": 2525, "drag_coefficient": 0.34, "stock_gear_ratio": 3.90, "cooling_capacity_index": 0.72, "suspension_index": 0.70, "tire_grip_index": 0.74, "image": "/brz.webp"},
    {"code": "FD_RX7", "name": "Mazda RX-7 FD", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1280, "stock_hp": 255, "engine_bay_width_mm": 740, "wheelbase_mm": 2425, "drag_coefficient": 0.31, "stock_gear_ratio": 4.10, "cooling_capacity_index": 0.65, "suspension_index": 0.72, "tire_grip_index": 0.68, "image": "/fd_rx7.webp"},
    {"code": "AP1_S2000", "name": "Honda S2000 AP1", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1250, "stock_hp": 240, "engine_bay_width_mm": 710, "wheelbase_mm": 2400, "drag_coefficient": 0.38, "stock_gear_ratio": 4.10, "cooling_capacity_index": 0.67, "suspension_index": 0.75, "tire_grip_index": 0.70, "image": "/ap1_s2000.webp"},
    {"code": "JZA80_SUPRA", "name": "Toyota Supra JZA80", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1550, "stock_hp": 320, "engine_bay_width_mm": 770, "wheelbase_mm": 2550, "drag_coefficient": 0.33, "stock_gear_ratio": 3.76, "cooling_capacity_index": 0.75, "suspension_index": 0.70, "tire_grip_index": 0.72, "image": "/supra_jza80.webp"},
    {"code": "E30_325", "name": "BMW 3-Series E30", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 1150, "stock_hp": 168, "engine_bay_width_mm": 730, "wheelbase_mm": 2570, "drag_coefficient": 0.35, "stock_gear_ratio": 3.73, "cooling_capacity_index": 0.62, "suspension_index": 0.60, "tire_grip_index": 0.60, "image": "/e30_325.webp"},
    {"code": "AE86", "name": "Toyota Corolla AE86", "layout": "longitudinal", "drivetrain": "RWD", "recipient_weight_kg": 950, "stock_hp": 120, "engine_bay_width_mm": 710, "wheelbase_mm": 2400, "drag_coefficient": 0.38, "stock_gear_ratio": 4.30, "cooling_capacity_index": 0.58, "suspension_index": 0.58, "tire_grip_index": 0.58, "image": "/ae86.webp"},
]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def get_engine(code: str) -> dict[str, Any]:
    if code == "CUSTOM":
        return {
            "code": "CUSTOM",
            "name": "Custom Engine",
            "family": "honda_k",
            "layout": "longitudinal",
            "displacement_l": 2.0,
            "cylinders": 4,
            "compression_ratio": 10.0,
            "engine_weight_kg": 180,
            "base_hp": 200,
            "base_torque_nm": 200,
            "forced_induction": 0,
            "fuel_type": "gasoline",
            "donor_mount_width_mm": 700,
            "image": "/engine_img.webp"
        }
    return deepcopy(next(engine for engine in BASE_ENGINES if engine["code"] == code))


def get_chassis(code: str) -> dict[str, Any]:
    if code == "CUSTOM":
        return {
            "code": "CUSTOM",
            "name": "Custom Chassis",
            "layout": "longitudinal",
            "drivetrain": "RWD",
            "recipient_weight_kg": 1200,
            "stock_hp": 150,
            "engine_bay_width_mm": 750,
            "wheelbase_mm": 2500,
            "drag_coefficient": 0.32,
            "stock_gear_ratio": 4.10,
            "cooling_capacity_index": 0.65,
            "suspension_index": 0.65,
            "tire_grip_index": 0.65,
            "image": "/car_img.webp"
        }
    return deepcopy(next(chassis for chassis in CHASSIS if chassis["code"] == code))


def _drivetrain_match(engine: dict[str, Any], chassis: dict[str, Any]) -> float:
    if engine["layout"] == chassis["layout"]:
        return 1.0
    if chassis["drivetrain"] == "AWD" and engine["layout"] == "longitudinal":
        return 0.82
    return 0.45


def build_feature_record(
    engine: dict[str, Any],
    chassis: dict[str, Any],
    *,
    tune_level: float,
    cooling_capacity_index: float | None = None,
    tire_grip_index: float | None = None,
    suspension_index: float | None = None,
    gear_ratio: float | None = None,
) -> dict[str, Any]:
    cooling = clamp(chassis["cooling_capacity_index"] if cooling_capacity_index is None else cooling_capacity_index, 0.35, 1.0)
    tire_grip = clamp(chassis["tire_grip_index"] if tire_grip_index is None else tire_grip_index, 0.35, 1.0)
    suspension = clamp(chassis["suspension_index"] if suspension_index is None else suspension_index, 0.35, 1.0)
    selected_gear_ratio = clamp(chassis["stock_gear_ratio"] if gear_ratio is None else gear_ratio, 2.70, 4.88)

    mount_clearance = (chassis["engine_bay_width_mm"] - engine["donor_mount_width_mm"]) / 180
    mount_complexity = clamp(0.55 - mount_clearance + (0.24 if engine["layout"] != chassis["layout"] else 0), 0.05, 1.0)
    total_weight = chassis["recipient_weight_kg"] + engine["engine_weight_kg"]
    weight_distribution_shift = clamp((engine["engine_weight_kg"] - 175) / 170, 0, 1)
    drivetrain_match = _drivetrain_match(engine, chassis)
    swap_difficulty = clamp(
        0.16 + mount_complexity * 0.42 + weight_distribution_shift * 0.22 + (1 - drivetrain_match) * 0.28 + engine["forced_induction"] * 0.06,
        0.08,
        1.0,
    )

    return {
        "engine_code": engine["code"],
        "chassis_code": chassis["code"],
        "engine_displacement_l": engine["displacement_l"],
        "cylinders": engine["cylinders"],
        "compression_ratio": engine["compression_ratio"],
        "engine_weight_kg": engine["engine_weight_kg"],
        "base_hp": engine["base_hp"],
        "base_torque_nm": engine["base_torque_nm"],
        "forced_induction": engine["forced_induction"],
        "engine_family_encoding": ENGINE_FAMILY_ENCODING[engine["family"]],
        "recipient_weight_kg": chassis["recipient_weight_kg"],
        "drivetrain_match": drivetrain_match,
        "mount_complexity": mount_complexity,
        "gear_ratio": selected_gear_ratio,
        "cooling_capacity_index": cooling,
        "suspension_index": suspension,
        "tire_grip_index": tire_grip,
        "drag_coefficient": chassis["drag_coefficient"],
        "power_to_weight_ratio": engine["base_hp"] / total_weight,
        "torque_per_litre": engine["base_torque_nm"] / engine["displacement_l"],
        "displacement_per_cylinder": engine["displacement_l"] / engine["cylinders"],
        "swap_difficulty_index": swap_difficulty,
        "tune_level": clamp(tune_level, 0, 1),
        "stock_hp": chassis["stock_hp"],
    }


def add_targets(record: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    hp = record["base_hp"] * (0.86 + record["tune_level"] * 0.20) + record["base_hp"] * record["forced_induction"] * 0.08 + record["cooling_capacity_index"] * 28 - record["swap_difficulty_index"] * 34 + rng.uniform(-9, 9)
    torque = record["base_torque_nm"] * (0.88 + record["tune_level"] * 0.16) + record["base_torque_nm"] * record["forced_induction"] * 0.06 + record["gear_ratio"] * 7 - record["mount_complexity"] * 22 + rng.uniform(-12, 12)
    total_weight = record["recipient_weight_kg"] + record["engine_weight_kg"]
    traction_penalty = 0.22 if record["drivetrain_match"] < 0.55 and hp > 280 else 0
    zero_to_sixty = 11.25 - (hp / total_weight) * 35 - record["tire_grip_index"] * 0.85 - record["suspension_index"] * 0.28 - (record["gear_ratio"] - 3.7) * 0.20 + record["drag_coefficient"] * 0.65 + record["swap_difficulty_index"] * 0.72 + traction_penalty + rng.uniform(-0.18, 0.18)

    enriched = dict(record)
    enriched["post_swap_hp"] = round(clamp(hp, 95, 760), 2)
    enriched["post_swap_torque_nm"] = round(clamp(torque, 120, 900), 2)
    enriched["zero_to_sixty_s"] = round(clamp(zero_to_sixty, 2.6, 10.5), 2)
    return enriched


def build_training_records(seed: int = 7) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []
    for engine in BASE_ENGINES:
        for chassis in CHASSIS:
            for _ in range(6):
                record = build_feature_record(
                    engine,
                    chassis,
                    tune_level=rng.uniform(0.20, 0.95),
                    cooling_capacity_index=chassis["cooling_capacity_index"] + rng.uniform(-0.10, 0.18),
                    tire_grip_index=chassis["tire_grip_index"] + rng.uniform(-0.08, 0.20),
                    suspension_index=chassis["suspension_index"] + rng.uniform(-0.08, 0.18),
                    gear_ratio=chassis["stock_gear_ratio"] + rng.uniform(-0.25, 0.35),
                )
                records.append(add_targets(record, rng))
    return records
