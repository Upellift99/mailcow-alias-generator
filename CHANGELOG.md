# Changelog

## [1.0.6](https://github.com/Upellift99/mailcow-alias-generator/compare/v1.0.5...v1.0.6) (2026-08-29)


### Bug Fixes

* bump gunicorn from 26.1.0 to 26.2.0 ([#34](https://github.com/Upellift99/mailcow-alias-generator/issues/34)) ([f1abe68](https://github.com/Upellift99/mailcow-alias-generator/commit/f1abe684defcdcc1baf8046f6ef6b8a15a5f6d90))

## [1.0.5](https://github.com/Upellift99/mailcow-alias-generator/compare/v1.0.4...v1.0.5) (2026-08-22)


### Bug Fixes

* bump gunicorn from 26.0.0 to 26.1.0 ([#31](https://github.com/Upellift99/mailcow-alias-generator/issues/31)) ([5c4c36a](https://github.com/Upellift99/mailcow-alias-generator/commit/5c4c36af136123234309b5406822b51264bf99d0))

Gunicorn 26.1.0 is a routine upstream patch, **not a security fix for this image**.
The "Security" heading in its release notes raises the version floors of gunicorn's
*optional* extras — tornado, h2, setuptools, pymdown-extensions, httpx — and none of
them are installed here: the container runs plain sync workers (`gunicorn --workers 2`),
so nothing in that section is reachable. No urgent redeploy is warranted.

The one upstream change that does reach this deployment is WSGI body framing on
HEAD and 1xx/204/304 responses: `Content-Length` is now stripped per RFC 9110 §6.4.2
and body bytes are dropped instead of being written. The app returns JSON on normal
paths, so this only affects the health-check and preflight edges. Gunicorn also drops
`packaging` as a runtime dependency, leaving one fewer package in the image.

Upgrading needs no configuration change and nothing new to watch.

## [1.0.4](https://github.com/Upellift99/mailcow-alias-generator/compare/v1.0.3...v1.0.4) (2026-08-01)


### Bug Fixes

* update altcha requirement from &lt;3.0.0,&gt;=2.0.2 to &gt;=2.1.0,&lt;3.0.0 ([#29](https://github.com/Upellift99/mailcow-alias-generator/issues/29)) ([24420cb](https://github.com/Upellift99/mailcow-alias-generator/commit/24420cb32e9c499f20bca1043ad7066d09823c5c))

## [1.0.3](https://github.com/Upellift99/mailcow-alias-generator/compare/v1.0.2...v1.0.3) (2026-07-25)


### Bug Fixes

* **ci:** retry the Docker Hub pulls in both workflows ([#27](https://github.com/Upellift99/mailcow-alias-generator/issues/27)) ([62271a1](https://github.com/Upellift99/mailcow-alias-generator/commit/62271a1c9c6c59acf6234f74c88ebf706bcc1b30))

## [1.0.2](https://github.com/Upellift99/mailcow-alias-generator/compare/v1.0.1...v1.0.2) (2026-07-25)


### Bug Fixes

* **ci:** publish the image on release again ([#25](https://github.com/Upellift99/mailcow-alias-generator/issues/25)) ([70340d4](https://github.com/Upellift99/mailcow-alias-generator/commit/70340d41a37f8a5a7765adc6685b18864c12de66))

## [1.0.1](https://github.com/Upellift99/mailcow-alias-generator/compare/v1.0.0...v1.0.1) (2026-07-25)


### Refactoring

* derive the test solve bound from ALTCHA_MAX_NUMBER ([#22](https://github.com/Upellift99/mailcow-alias-generator/issues/22)) ([efeac3c](https://github.com/Upellift99/mailcow-alias-generator/commit/efeac3cdd995800e4a96c975d9e7646c9d7f8328))


### Documentation

* add draft page for mailcow third-party docs submission ([7e5829d](https://github.com/Upellift99/mailcow-alias-generator/commit/7e5829d4f4cdf1509a4e602f6546ac1fc96875de))
* simplify Docker quick start (no repo clone needed) ([4ba4e99](https://github.com/Upellift99/mailcow-alias-generator/commit/4ba4e99239f92f0123d9041912444cfa8a68bc66))
* streamline the README ([5e4df2a](https://github.com/Upellift99/mailcow-alias-generator/commit/5e4df2a6f5169eaa8e932e18867dbb5c84ece72e))


### Build System

* **deps-dev:** bump pytest from 9.0.3 to 9.1.1 ([#16](https://github.com/Upellift99/mailcow-alias-generator/issues/16)) ([438e064](https://github.com/Upellift99/mailcow-alias-generator/commit/438e064da83d863881a413cf8e41ef285d8b0154))
* **deps:** bump actions/checkout from 6 to 7 ([#14](https://github.com/Upellift99/mailcow-alias-generator/issues/14)) ([177e5c9](https://github.com/Upellift99/mailcow-alias-generator/commit/177e5c9566f9b5ec39aa6d1628faff9acf95b8fa))
* **deps:** bump actions/setup-python from 6 to 7 ([#19](https://github.com/Upellift99/mailcow-alias-generator/issues/19)) ([51ee8ea](https://github.com/Upellift99/mailcow-alias-generator/commit/51ee8eab7f88bf3ba64f048a22c043126f0e5085))
* **deps:** bump flask-limiter from 3.8.0 to 4.1.1 ([#15](https://github.com/Upellift99/mailcow-alias-generator/issues/15)) ([40da996](https://github.com/Upellift99/mailcow-alias-generator/commit/40da996e35f049278b93be3bcd1538a0c5fd8283))
* **deps:** migrate to altcha 2.x ([#20](https://github.com/Upellift99/mailcow-alias-generator/issues/20)) ([431d80d](https://github.com/Upellift99/mailcow-alias-generator/commit/431d80da2b6d49fa07e99f8f3c75ddaf3938251c)), closes [#18](https://github.com/Upellift99/mailcow-alias-generator/issues/18)
