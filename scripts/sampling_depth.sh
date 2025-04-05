#!/bin/bash

set -ex

mkdir -p "out/$batch_id"

batch_id=sampling_depth_$(./scripts/idgen.sh)
docker build . -t "$batch_id"
if docker run --name "$batch_id" \
	--mount type=bind,src="$(pwd)"/fastq,dst=/fastq,readonly \
	--mount type=bind,src="$(pwd)"/meta,dst=/meta,readonly \
	"$batch_id" bash -c "$cmd"
then
	cat - | xargs -I FILE docker cp "$batch_id":FILE "out/$batch_id/"
	find "out/$batch_id/" -type f -name ".qzv" | \
		xargs -0 ./scripts/view.sh  # run in the host
fi

# docker execではentorypointを経由せず直接コマンドを実行するためbase環境が認識されない
# そのためexecを使用する際にはbaseを認識させなければならない
de() {
	docker exec -it "$batch_id" micromamba run -n base bash -c "$@"
}

docker rm "$batch_id"
docker rmi "$batch_id"


