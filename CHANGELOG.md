# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.7.0]

### Added
- A `meta` and a `bulk_meta`entrypoint was added to the new `hyp3.plugin` entry-point groups.

### Changed
_ The HyP3 `__main__` package entrypoint now allows selecting either the `meta` (default) or `bulk_meta` hyp3 plugin entrypoint with the `++plugin` parameter
- STAC item JSONs will be published to the same prefix in the `--publish-bucket` as the source granule and other metadata files.
- `generate.save_metadata` will now return the path to the STAC, premet, spatial, and kerchunk files (optionally) written. Note: the kerchunk file path is always returned but the file may not exist if the references weren't generated.
- `process.process_itslive_meta` will now return the path to the STAC, premet and spatial files created.

### Removed
- The now unused `--publish-prefix` argument to the HyP3 `meta` entrypoint has been removed.

## [0.6.0]

### Added
- `cryoforge` has been merged into this repository as `hyp3_itslive_metadata.cryoforge` instead of pulling it in as an external dependency.
  - the cryoforge `metagen`, `ingest`, `generate-gatalog`, `generate-from-parquet`, and `search-items` console script entrypoints have been added.
- Support for Sentinel-1 C & D platforms which are now both launched.

## [0.5.0]

### Changed
- Upgraded to cryoforge v0.4.0, which now provides scene_1_frame and scene_2_frame stac item properties.

## [0.4.0]

### Adds
* Adds a `--granule-uri` argument that allows pointing at a specific granule so we can run this independent of the product generation workflow
* Groups the `--bucket` and `--bucket-prefix` arguments into a HyP3 Content Bucket argument, which is mutually exclusive with `--granule-uri`
* Adds a `aws.determine_granule_uri_from_bucket` which looks in the bucket and prefix provided and either uses the info from `publish_info.json` to point to the published product, or finds the first `*.nc` file in the bucket and prefix and points to that
* Add `--publish-bucket` and `--publish-prefix` arguments to specify where the metadata files should be published to
* Added a `aws.upload_file_to_s3_with_publish_access_keys` function that uploads s3 products to a bucket using the access keys stored in the `PUBLISH_ACCESS_KEY_ID` and `PUBLISH_SECRET_ACCESS_KEY` environment variables

### Changed
* The STAC JSON `premet` and `spatial` files will be published to an additional bucket using "publish" access keys specific to that bucket. Accordingly:

### Removed
* Removed the `--stac-output` argument in favor of `--publish-bucket` and `--publish-prefix` arguments
*  Removed `--upload` arguments as it is implied by the `--publish-bucket` argument

## [0.3.0]
- creates temp file output dir in container 
- fixed entrypoint so it's micromamba compatible
- kerchunk reference is optional, defaults to False

## [0.1.0]

### Added
- hyp3-itslive-metadata plugin created with the [HyP3 Cookiecutter](https://github.com/ASFHyP3/hyp3-cookiecutter)
- switched to micromamba
- install neovim and unzip with conda-forge
