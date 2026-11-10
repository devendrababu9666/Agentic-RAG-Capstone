import json
from pathlib import Path

SCENARIOS_FILE = Path("evaluation/test_scenarios.json")
REPORT_FILE = Path("reports/evaluation_run.json")

REQUIRED_FIELDS = {
    "id",
    "name",
    "question",
    "expected_outcome",
    "requirement",
    "status",
}


def main():
    if not SCENARIOS_FILE.is_file():
        raise SystemExit(f"Scenario file not found: {SCENARIOS_FILE}")

    scenarios = json.loads(
        SCENARIOS_FILE.read_text(encoding="utf-8-sig")
    )

    if not isinstance(scenarios, list) or not scenarios:
        raise SystemExit("The scenario file must contain a non-empty JSON list.")

    seen_ids = set()
    results = []

    for scenario in scenarios:
        missing = REQUIRED_FIELDS - scenario.keys()
        if missing:
            raise SystemExit(
                f"{scenario.get('id', '<unknown>')}: "
                f"missing fields {sorted(missing)}"
            )

        scenario_id = scenario["id"]

        if scenario_id in seen_ids:
            raise SystemExit(f"Duplicate scenario ID: {scenario_id}")

        seen_ids.add(scenario_id)

        if not isinstance(scenario["question"], str):
            raise SystemExit(f"{scenario_id}: question must be a string.")

        # This runner validates test definitions only. It does not
        # claim that application behaviour has passed the test.
        results.append({
            "id": scenario_id,
            "name": scenario["name"],
            "requirement": scenario["requirement"],
            "expected_outcome": scenario["expected_outcome"],
            "definition_valid": True,
            "execution_status": "NOT_RUN",
            "actual_outcome": None,
        })

    report = {
        "scenario_count": len(results),
        "definition_validation": "PASSED",
        "application_tests_passed": 0,
        "application_tests_failed": 0,
        "application_tests_not_run": len(results),
        "results": results,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("Scenario definition validation: PASSED")
    print(f"Scenarios validated: {len(results)}")
    print("Application tests executed: 0")
    print(f"Report written to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
