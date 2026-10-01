from core.models.ai_plan import AIPlan


def test_invalid_plan():

    invalid_response = {
        "goal": "Create a portfolio website",
        "steps": [
            {
                "reason": "This step has no description"
            }
        ]
    }

    try:

        AIPlan.model_validate(invalid_response)

        print("[SAFETY TEST] ERROR")
        print("[SAFETY TEST] Invalid plan was accepted")

    except Exception as error:

        print("[SAFETY TEST] PASS")
        print("[SAFETY TEST] Invalid AI plan was rejected")
        print(f"[SAFETY TEST] Reason: {error}")


if __name__ == "__main__":
    test_invalid_plan()
