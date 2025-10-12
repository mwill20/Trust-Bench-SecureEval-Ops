from trust_bench_studio.utils.orchestrator_synthesis import synthesize_verdict


def test_veto_and_composite() -> None:
    summary_stub = type(
        'Summary',
        (),
        {
            'metrics': {
                'faithfulness': 0.9,
                'avg_latency': 2.0,
                'injection_block_rate': 0.92,
                'semgrep_findings': 0,
                'secret_findings': 0,
                'refusal_accuracy': 0.95,
            },
            'raw': {'config': {'thresholds': {'warn_threshold': 0.7}}},
            'agents': [],
        },
    )()

    verdict = synthesize_verdict(summary_stub, None)
    assert verdict['decision'] in {'pass', 'warn', 'fail'}
    assert 0.0 <= verdict['composite'] <= 1.0
    pillars = verdict['pillars']
    assert pillars['Athena']['status'] in {'complete', 'failed'}
    assert pillars['Aegis']['status'] == 'complete'

    summary_stub.metrics['injection_block_rate'] = 0.1
    summary_stub.metrics['semgrep_findings'] = 1
    verdict_fail = synthesize_verdict(summary_stub, None)
    assert verdict_fail['decision'] == 'fail'
    assert verdict_fail['pillars']['Aegis']['status'] == 'failed'
    assert any('security' in driver.lower() for driver in verdict_fail['drivers'])

