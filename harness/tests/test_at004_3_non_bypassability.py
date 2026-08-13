from agentic_demo import evaluate_scenario


def test_at004_3_execution_permitted_requires_gateway_validation():
    result = evaluate_scenario('AP-001')

    assert result['financial_consequence'] == 'EXECUTION PERMITTED'

    assert result['execution_gateway'] is not None, (
        'Execution was reported as PERMITTED without consuming '
        'the Execution Gateway determination'
    )

    assert result['execution_gateway']['status'] == 'PERMITTED'
