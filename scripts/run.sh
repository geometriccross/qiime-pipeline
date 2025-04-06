#!/bin/bash

set -e

while getopts dvs: OPT; do
	case $OPT in
	v)
		set -ex
		;;
	d)
		DEBUG=true
		;;
	s)
		SAMPLING_DEPTH=$OPTARG
		;;
	*)
		DEBUG=false
		;;
	esac
done

batch_id=$(./scripts/idgen.sh)
mkdir -p "out/$batch_id"

docker build . -t "$batch_id"
docker run -dit --name "$batch_id" \
	--mount type=bind,src="$(pwd)"/db/classifier.qza,dst=/db/classifier.qza \
	--mount type=bind,src="$(pwd)"/fastq,dst=/fastq,readonly \
	--mount type=bind,src="$(pwd)"/meta,dst=/meta,readonly \
	"$batch_id" bash

# docker execではentorypointを経由せず直接コマンドを実行するためbase環境が認識されない
# そのためexecを使用する際にはbaseを認識させなければならない
de() {
	docker exec -i "$batch_id" micromamba run -n base bash -c "$@"
}

de '/scripts/create_Mfiles.py --id-prefix id --out-meta /tmp/meta --out-mani /tmp/mani'
de '/scripts/check_manifest.py /tmp/mani'
if [[ $DEBUG = true ]]; then
	# frequencyが50000未満のサンプルしかない場合、rarefaction.shは失敗する
	# alpha,beta解析を行う場合、それぞれ異なるcol要素を持っていないと失敗する
	de 'python /scripts/extract_id.py /tmp/meta id1 id2 id21 id25 > /tmp/meta_debug'
	de 'python /scripts/extract_id.py /tmp/mani id1 id2 id21 id25 > /tmp/mani_debug'
	de 'mv /tmp/meta_debug /tmp/meta'
	de 'mv /tmp/mani_debug /tmp/mani'
fi

# if variable was not set
if [ -z ${SAMPLING_DEPTH+x} ]; then
	source ./scripts/sampling_depth.sh
else
	source ./scripts/metagenome.sh -s "$SAMPLING_DEPTH"
fi

docker stop "$batch_id"
docker rm "$batch_id"
docker rmi "$batch_id"
