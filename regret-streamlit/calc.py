"""
calc.py — Core financial calculation logic for the Regret Calculator.
"""

from dataclasses import dataclass, field
from typing import List
import uuid
import math

SCENARIO_COLORS = ["#e8c547", "#3ecfb2", "#4a9eff", "#e85d8a", "#b88aff"]

FREQ_OPTIONS = {
    "per day":      365,
    "per workday":  260,
    "per week":     52,
    "per month":    12,
    "per year":     1,
}

FREQ_LABELS = {v: k for k, v in FREQ_OPTIONS.items()}

PRESET_HABITS = [
    {"name": "Daily coffee / latte",       "cost": 6.50,  "freq": 365},
    {"name": "Lunch out (workdays)",        "cost": 14.00, "freq": 260},
    {"name": "Netflix / streaming",         "cost": 18.00, "freq": 12 },
    {"name": "Spotify / music",             "cost": 11.00, "freq": 12 },
    {"name": "Gym membership",              "cost": 55.00, "freq": 12 },
    {"name": "Weekly takeout / delivery",   "cost": 38.00, "freq": 52 },
    {"name": "Daily snack / energy drink",  "cost": 4.00,  "freq": 365},
    {"name": "Impulse online shopping",     "cost": 45.00, "freq": 12 },
    {"name": "Drinks / bar nights",         "cost": 60.00, "freq": 12 },
    {"name": "Other subscriptions",         "cost": 25.00, "freq": 12 },
]


@dataclass
class Habit:
    name: str
    cost: float
    freq: int
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def yearly(self) -> float:
        return self.cost * self.freq

    @property
    def daily(self) -> float:
        return self.yearly / 365


@dataclass
class Scenario:
    name: str
    color: str
    habits: List[Habit] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    @property
    def yearly_total(self) -> float:
        return sum(h.yearly for h in self.habits)

    @property
    def daily_total(self) -> float:
        return self.yearly_total / 365


def future_value(annual: float, years: int, rate_pct: float) -> float:
    """Calculate future value of regular annual investment."""
    if rate_pct == 0:
        return annual * years
    r = rate_pct / 100
    return annual * ((math.pow(1 + r, years) - 1) / r)


def calc_scenario(scenario: Scenario, years: int, rate_pct: float) -> dict:
    """Return full projection for a scenario."""
    yearly = scenario.yearly_total
    return {
        "yearly":         yearly,
        "daily":          yearly / 365,
        "total_spent":    yearly * years,
        "invested_value": future_value(yearly, years, rate_pct),
        "spent_by_year":  [round(yearly * (i + 1)) for i in range(years)],
        "invest_by_year": [round(future_value(yearly, i + 1, rate_pct)) for i in range(years)],
    }


def make_default_scenarios() -> List[Scenario]:
    s1 = Scenario("Current spending", SCENARIO_COLORS[0], habits=[
        Habit("Daily coffee",   6.50, 365),
        Habit("Netflix",        18.0, 12),
        Habit("Gym membership", 55.0, 12),
        Habit("Weekly takeout", 38.0, 52),
    ])
    s2 = Scenario("Cut the extras", SCENARIO_COLORS[1], habits=[
        Habit("Netflix", 18.0, 12),
    ])
    return [s1, s2]


def fmt_usd(n: float) -> str:
    return f"${n:,.0f}"


def fmt_usd_dec(n: float) -> str:
    return f"${n:,.2f}"
