def test_hyp3_itslive_metadata(script_runner):
    ret = script_runner.run(['python', '-m', 'hyp3_itslive_metadata', '-h'])
    assert ret.success


def test_metagen(script_runner):
    ret = script_runner.run(['metagen', '-h'])
    assert ret.success


def test_ingest(script_runner):
    ret = script_runner.run(['ingest', '-h'])
    assert ret.success


def test_generate_catalog(script_runner):
    ret = script_runner.run(['generate-catalog', '-h'])
    assert ret.success


def test_generate_from_parquet(script_runner):
    ret = script_runner.run(['generate-from-parquet', '-h'])
    assert ret.success


def test_search_items(script_runner):
    ret = script_runner.run(['search-items', '-h'])
    assert ret.success
