import argparse


class AppConfig:
    Workspace: str = ""
    Filename: str = ""

    @staticmethod
    def parse_arg() -> None:
        parser = argparse.ArgumentParser(
            prog="py-yaml-composer",
            description="Template based simple Yaml composer",
            epilog="Generates Yaml file from templates.",
        )

        parser.add_argument(
            "filename",
            help="Yaml Template file location (Absolute or Relative to Workspace)",
        )
        parser.add_argument(
            "-w",
            "--workspace",
            default="/yaml_workspace",
            help="Workspace location used to load/process/generate yaml files.",
        )
        args = parser.parse_args()

        AppConfig.Filename = args.filename
        AppConfig.Workspace = (
            args.workspace if args is not None and args != "" else "."
        )
