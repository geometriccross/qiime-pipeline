#!/bin/bash

set -ex

cmd="$(cat - << EOF
	/scripts/create_Mfiles.py --id-prefix id --out-meta ~/meta --out-mani ~/mani
	/scripts/check_manifest.py ~/mani
	
	 # /scripts/pipeline/rarefaction.sh -c ~/mani -x ~/meta
EOF
)"


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

docker rm "$batch_id"
docker rmi "$batch_id"


