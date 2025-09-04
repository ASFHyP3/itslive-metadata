# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
