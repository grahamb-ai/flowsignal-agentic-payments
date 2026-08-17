from agentic_demo import evaluate_scenario


def test_ec001_6_refuse_state_changed_does_not_form_represented_consequence():
    result = evaluate_scenario("AP-003")
    assert result["execution_response"]["decision"] == "REFUSE"
    assert result["execution_gateway"]["status"] == "BLOCKED"
    assert result["financial_consequence"] == "NO EXECUTION"


def test_ec001_6_refuse_expired_mandate_does_not_form_represented_consequence():
    result = evaluate_scenario("AP-005")
    assert result["execution_response"]["decision"] == "REFUSE"
    assert result["execution_gateway"]["status"] == "BLOCKED"
    assert result["financial_consequence"] == "NO EXECUTION"


def test_ec001_6_action_substitution_block_does_not_form_represented_consequence():
    result = evaluate_scenario("AP-006")
    assert result["execution_gateway"]["status"] == "BLOCKED"
    assert result["execution_gateway"]["reason_code"] == "ACTION_BINDING_MISMATCH"
    assert result["financial_consequence"] == "NO EXECUTION"
