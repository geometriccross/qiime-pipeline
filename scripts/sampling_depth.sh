#!/bin/bash

set -ex

mkdir -p "out/$batch_id"

batch_id=sampling_depth_$(./scripts/idgen.sh)
docker build . -t "$batch_id"
docker run -dit --name "$batch_id" \
	--mount type=bind,src="$(pwd)"/fastq,dst=/fastq,readonly \
	--mount type=bind,src="$(pwd)"/meta,dst=/meta,readonly \
	"$batch_id" bash

# docker execではentorypointを経由せず直接コマンドを実行するためbase環境が認識されない
# そのためexecを使用する際にはbaseを認識させなければならない
de() {
	docker exec -it "$batch_id" micromamba run -n base bash -c "$@"
}

docker rm "$batch_id"
docker rmi "$batch_id"


