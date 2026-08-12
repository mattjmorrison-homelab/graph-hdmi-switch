
# setup - nix-shell -p uv python312

for the application flow...

1. build the container

- python, uv to manage dependencies
- only ever build from the uv.lock
-

1. publish the container to the registry

2. pull down the container to run the tests

- can we have the container have a different entry point that can be targeted that will contain all of the test dependencies and a different "runtime" entry point that will not but will only contain the production runtime environment - while still allowing the test environment contained within the container to run the real code that will run in the wild for real?

how will this work? Run on a push to main and go through the pipeline, as long as it makes it through the pipeline then trigger the deploy? or will it need to run through the pipeline on a pull request then upon merging the pull request the artifact to deploy will already be tagged and ready for argocd to run with?
