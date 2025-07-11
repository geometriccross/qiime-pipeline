from __future__ import annotations
import tomlkit

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

    def to_toml(self) -> tomlkit.TOMLDocument:
        """
        Convert the region to a TOML document.
        """
        doc = tomlkit.document()
        doc.add("name", self.name)
        doc.add("trim_left_f", self.trim_left_f)
        doc.add("trim_left_r", self.trim_left_r)
        doc.add("trunc_len_f", self.trunc_len_f)
        doc.add("trunc_len_r", self.trunc_len_r)
        return doc

    @classmethod
    def from_toml(self, toml_doc: tomlkit.TOMLDocument) -> Region:
        """
        Initialize the region from a TOML document.
        """
        return Region(
            name=toml_doc["name"],
            trim_left_f=toml_doc["trim_left_f"],
            trim_left_r=toml_doc["trim_left_r"],
            trunc_len_f=toml_doc["trunc_len_f"],
            trunc_len_r=toml_doc["trunc_len_r"],
        )


class V3V4(Region):
    def __init__(self):
        super().__init__(
            name="V3V4",
            trim_left_f=17,
            trim_left_r=21,
            trunc_len_f=250,
            trunc_len_r=250,
        )
