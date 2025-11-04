import os
import tomllib
from typing import Any
import zipfile

instance_config = """
[General]
ConfigVersion=1.2
InstanceType=OneSix
iconKey=icon
name={name}
""".strip()

mmc_pack = """
{
    "components": [
        {
            "important": true,
            "uid": "net.minecraft",
            "version": "{versions_minecraft}"
        },
        {
            "uid": "net.fabricmc.fabric-loader",
            "version": "{versions_fabric}"
        },
        {
            "cachedName": "unsup",
            "cachedVersion": "{versions_unsup}",
            "uid": "com.unascribed.unsup"
        }
    ],
    "formatVersion": 1
}
""".strip()

unsup_patch = """
{
	"formatVersion": 1,
	"name": "unsup",
	"uid": "com.unascribed.unsup",
	"version": "{versions_unsup}",
	"+agents": [
		{
			"name": "com.unascribed:unsup:{versions_unsup}",
			"url": "https://repo.sleeping.town"
		}
	]
}
""".strip()

unsup_config = """
version=1
source_format=packwiz
source=https://potluck.devos.one/pack.toml
preset=minecraft

[branding]
icon=G2EGID4Ub8oO1SH4OSK3CttGhA42vOP7h/SvEIibONdGNqJq2qjzs847KNLgEfc/17znFXR6p2e3SrACG202HlVYhQ+jG2ig4w/Px1q609miAuAQ7wWJVYFOKM4GAGxDKGSFI83vH4zLFyYlQmlOhhOoCPqWzdE6Vx1c1HL52zZm46zGDEeEo6HLEfSDKsITRNCqWviP9j5pWTbn///VdM6n8AIOzglzfK/11k5vWjfajLIIO2kWRvGnVvERTdNpIxG/lxESZXVw0mXUKrVVigJAgTosgBrOCUBTDCgCFoWAoSEPQ4JyjwBKCU1i4S9vIqeUOXGhBAHs8GfOZGwj//87dncInom1A6MRRbJyPvEMhj2TeOGour/ul41IKngoGrmhtpoAQOX79s0hgtIyYHR7gkiJRMn3DFmNGLjxot/AsiINapzgoCFOOZRBLYAcyPkNeVM2MnWj+OLhpxCicivXGiusYwHTDS+cJ27wBFEs4CMWMpYOpPlMLIQAcRdEbwcLlk/1hbWJyq4exg1uhkfQvcIc37fF+oxkiJFUSxlr3UBOD8NM6kYmIt7LcPgvQBDTv/LbD1lp+1NK+RIT+oFup8IJW2HLSsVtKZvXkeupPQhvnmCCJz7PDmOiIo62g1FTZe2GSmMvdIcPsds60XuK1E17ONmYjYpOGlx50R+ESnNZ0kJoiKosScrB9MRPX+ZIAJQBQ44hO6SzUrfnqGdv37XNWLYtzzOGD4Oh3oHqIYu6YdAlNtZVppcxNZqFackDEfcjcTYEb4X5fqkmhAD7hAoEsEW+51SmLhL4pVT4dwNZqBmxHWfQV319dou9oK+BicAl9oYu6pbOS+qKxO7nqIvovx7onM7rCgZDR4kJtToVmRMtwEMZPB7nFaIgSNhTEce7obrBKIXTYpVhk62pP+91/Uwsuw1ndcvKjO3OEaESMdKRWzZcaf+CZ4Zhf93zR1EtDT4Hn+SVXsHUJYFBJYmBWsvBuq+aJpl298dCE7lTtTMFc7HzhjVB3dJdiT6HIhDGB7P6Zuwn9tWhlcFbOq2WBMhGlwxJPwsr/gRsLPbS6McyOOQD+JNMa8PG8drR3g2av4iCG0/Xy2dhlXF46KubrPpuWI5fDEdpOPiQWCIon6nESwIGqh/GfBjKeuWJ19x56zWuVhTrXf+VRXWD17aGzv0uIjU870P/+uAlZjuPrUEwkfV89OzIbNQ2USYs6+mC5FOD7ar9VY9MjUE4TYw8HXXkYbF49j0nrm7aIhjXFjKwBGspydqwEWIxahtIP7TFAnv/e/kx2FTdYPVcGH886pwso3MXcH4cbfSHMTQaCCmloU8Fok2ET/Tcvl8euxFyXdw3YSr5kZkTCNsGz/1nJ8yjH4RfkoKqUaUqfvNFW2zaqG1P7BwnG7NIeKjXjRh5B9loE8HahIMp9uKmwkxsfH40N/nQwYXhweTioK3c0UYsdA9Pvf2zHAPcIv/FnVaa6a6kmHaW9kChG7Qv1nDooC1E8vbHfD6aqAohlv2oLU5soP2w7CI5h8of75pyPVvZMq2wpnJERV7P7no+Vdt2uQjOVtyKIm2Uj+ykPFVgrP2bm9sO2pQvLU/UDcqVH+vX+HL6zbJw+A/55V39Hqc84ukyXxeYu/PXzZwuyvZNYaJAVr67gQ7dISRNFviKxv4hxYkLxGSB
modpack_name={name}
""".strip()

build_directory = "build"


def init_template(template: str, constants: dict[str, Any], prefix=None):
    templated = template
    for key, value in constants.items():
        if isinstance(value, list):
            continue

        if prefix:
            key = f"{prefix}_{key}"

        if isinstance(value, dict):
            templated = init_template(templated, value, key)
        else:
            templated = templated.replace("{" + key + "}", value)
    return templated


def main():
    with open(os.path.join("pack", "pack.toml"), "rb") as pack_file:
        packwiz_pack = tomllib.load(pack_file)

    os.makedirs(build_directory, exist_ok=True)

    with zipfile.ZipFile(
        os.path.join(build_directory, f"{packwiz_pack['name']}.zip"),
        "w",
        compression=zipfile.ZIP_DEFLATED,
    ) as output_pack:
        with output_pack.open("instance.cfg", "w") as instance_config_file:
            instance_config_file.write(
                init_template(instance_config, packwiz_pack).encode()
            )

        with output_pack.open("mmc-pack.json", "w") as mmc_pack_file:
            mmc_pack_file.write(init_template(mmc_pack, packwiz_pack).encode())

        with output_pack.open(
            "patches/com.unascribed.unsup.json", "w"
        ) as unsup_patch_file:
            unsup_patch_file.write(init_template(unsup_patch, packwiz_pack).encode())

        with output_pack.open(".minecraft/unsup.ini", "w") as unsup_config_file:
            unsup_config_file.write(init_template(unsup_config, packwiz_pack).encode())

        with output_pack.open("icon.png", "w") as pack_icon_file:
            with open("icon.png", "rb") as icon_file:
                pack_icon_file.write(icon_file.read())


if __name__ == "__main__":
    main()
