#!/bin/bash
# 親スクリプトで定義された変数や関数を使用しているため、warningをdisableする
# shellcheck disable=SC2154

de "/scripts/pipeline/basic.sh -s $SAMPLING_DEPTH"
de "/scripts/pipeline/taxonomy.sh"
# de "/scripts/pipeline/ancome.sh" # 時間がかかりすぎるためuncomment

# /tmp/out/.のように最後に.をつけることで、指定したディレクトリの中身を直接コピーすることとなる
docker cp "$batch_id":/tmp/out/. "out/$batch_id/"
