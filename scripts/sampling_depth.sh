#!/bin/bash

set -e

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

de '/scripts/create_Mfiles.py --id-prefix id --out-meta /tmp/meta --out-mani /tmp/mani'
de '/scripts/check_manifest.py /tmp/mani'
de '/scripts/pipeline/rarefaction.sh -c /tmp/mani -x /tmp/meta' |
	xargs -I FILE docker cp "$batch_id":FILE "out/$batch_id/"

find "out/$batch_id/" -type f -name ".qzv" |
	xargs -0 ./scripts/view.sh # run in the host

docker stop "$batch_id"
docker rm "$batch_id"
docker rmi "$batch_id"
