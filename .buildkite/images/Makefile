py27 = 2.7.17
py35 = 3.5.8
py36 = 3.6.10
py37 = 3.7.6
py38 = 3.8.1

####################################################################################################
# Update snapshots
####################################################################################################
snap:
	./docker/snapshot-update.sh

####################################################################################################
# Buildkite images
####################################################################################################
build-integration-38:
	./docker/build.sh $(py38) $(VERSION)

push-integration-38:
	./docker/push.sh $(py38) $(VERSION)

build-integration-37:
	./docker/build.sh $(py37) $(VERSION)

push-integration-37:
	./docker/push.sh $(py37) $(VERSION)

build-integration-36:
	./docker/build.sh $(py36) $(VERSION)

push-integration-36:
	./docker/push.sh $(py36) $(VERSION)

build-integration-35:
	./docker/build.sh $(py35) $(VERSION)

push-integration-35:
	./docker/push.sh $(py35) $(VERSION)

build-integration-27:
	./docker/build.sh $(py27) $(VERSION)

push-integration-27:
	./docker/push.sh $(py27) $(VERSION)

build-integration: build-integration-37 build-integration-36 build-integration-35 build-integration-27
push-integration: push-integration-37 push-integration-36 push-integration-35 push-integration-27
