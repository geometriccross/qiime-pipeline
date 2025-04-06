#!/bin/bash
# 親スクリプトで定義された変数や関数を使用しているため、warningをdisableする
# shellcheck disable=SC2154

de '/scripts/pipeline/rarefaction.sh -c /tmp/mani -x /tmp/meta' |
	tr -d "'\r\n" | # remove CRLR and single quote
	xargs -I FILE docker cp "$batch_id":FILE "out/$batch_id/"

find "out/$batch_id/" -type f -name "*.qzv" -print0 |
	xargs -0 ./scripts/view.sh # run in the host

