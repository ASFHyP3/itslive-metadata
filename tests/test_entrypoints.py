def test_hyp3_itslive_metadata(script_runner):
    ret = script_runner.run(['python', '-m', 'hyp3_itslive_metadata', '-h'])
    assert ret.success
