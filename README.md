# qiime-pipeline

qiime2の解析を自動的に行うスクリプトです
qiimeのコマンドはコンテナ内部で実行されます

## require
python >=3.11

## useage
usage: pipeline [-h] [--data DATA [DATA ...]] [--dataset-region DATASET_REGION] [--image IMAGE] [--dockerfile DOCKERFILE] [--local-output LOCAL_OUTPUT] [--local-database LOCAL_DATABASE] [--sampling_depth SAMPLING_DEPTH] pipeline

Run the QIIME pipeline.

positional arguments:
  pipeline              
                        Specify the type of pipeline to execute.
                        These three pipelines exist:
                            basic:
                                Basic pipeline for 16S rRNA gene amplicon analysis.
                                alpha and beta diversity, taxonomic analysis.
                            rarefaction_curve:
                                Generate rarefaction curves.
                            ancom:
                                Perform ANCOM analysis targeting the Species column in the metadata.

options:
  -h, --help            show this help message and exit
  --data DATA [DATA ...]
                        
                        Pairs of fastq and metadata paths to use for the pipeline.
                        Example:
                            --data path/to/metadata_path:path/to/fastq_folder,
                                   path/to/another_metadata:path/to/another_fastq_folder
  --dataset-region DATASET_REGION
                        Region of the 16S rRNA gene for the dataset (default: V3V4).
  --image IMAGE         Docker image to use for the QIIME pipeline.
  --dockerfile DOCKERFILE
                        Path to the Dockerfile for building the container.
  --local-output LOCAL_OUTPUT
                        Output directory for the results.
  --local-database LOCAL_DATABASE
                        Path to the local database file.
  --sampling_depth SAMPLING_DEPTH
