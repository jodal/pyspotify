from fabric.api import local, task


@task
def preprocess_header():
    local('cpp -nostdinc spotify/api.h > spotify/api.processed.h || true')
