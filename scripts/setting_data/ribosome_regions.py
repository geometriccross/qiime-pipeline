from enum import Enum

# qiime dada2 denoise-paired \
# 	--quiet \
# 	--p-n-threads 0 \
# 	--p-trim-left-f 17 \
# 	--p-trim-left-r 21 \
# 	--p-trunc-len-f 250 \
# 	--p-trunc-len-r 250 \


class Region:
    def __init__(
        self,
        name: str,
        trim_left_f: int,
        trim_left_r: int,
        trunc_len_f: int,
        trunc_len_r: int,
    ):
        self.name = name
        self.trim_left_f = trim_left_f
        self.trim_left_r = trim_left_r
        self.trunc_len_f = trunc_len_f
        self.trunc_len_r = trunc_len_r

    def __repr__(self):
        return (
            f"Region(name={self.name}, "
            f"trim_left_f={self.trim_left_f}, trim_left_r={self.trim_left_r}, "
            f"trunc_len_f={self.trunc_len_f}, trunc_len_r={self.trunc_len_r})"
        )


class V3(Region):
    def __init__(self):
        super().__init__(
            name="V3",
            trim_left_f=17,
            trim_left_r=21,
            trunc_len_f=250,
            trunc_len_r=250,
        )


class Regions(Enum):
    V3 = V3()

    @classmethod
    def all_regions(cls):
        return [region.value for region in cls]
