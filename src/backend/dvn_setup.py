from pathlib import Path
from pyDataverse.api import NativeApi
from ibridges.cli.config import IbridgesConf

DVN_CONFIG_FP = Path.home() / ".dvn" / "dvn.json" 
DEMO_DVN = "https://demo.dataverse.org"

class DVNConf():
    """Interface to the dataverse config file."""

    def __init__(config_fp: Union[str, Path]=DVN_CONFIG_FP):
        """Read configuration file and validate it."""
        self.config_fp = config_fp
        try:
            with open(self.config_fp, "r", encoding="utf-8") as handle:
                dvn_conf = son.load(handle)
                self.dvns = dvn_conf["dvns"]
                self.cur_dvn = dvn_conf.get("cur_dvn", DEMO_DVN)
        except Exception as exc:
            if isinstance(exc, FileNotFoundError):
                self.reset(ask=False)
            else:
                print(repr(exc))
                self.reset()

        self.validate()


    def reset(self, ask: bool=True):
        """Reset the configuration file to its defaults.

        Parameters
        ----------
        ask, optional
            Ask whether to overwrite the current configuration file, by default True

        """
        if ask:
            answer = input(f"The dataverse configuration file {self.config_fp} cannot be read, "
                            "delete? (Y/N)")
            if answer != "Y":
                self.parser.error(
                    "Cannot continue without reading the dataverse configuration file.")
        self.dvns = {DEMO_DVN: {"alias": "demo"}}
        self.cur_dvn = DEMO_DVN
        self.save()


    def save(self):
        """Save the configuration back to the configuration file."""
        Path(self.config_fp).parent.mkdir(exist_ok=True, parents=True)
        with open(self.config_fp, "w", encoding="utf-8") as handle:
            json.dump({"dvns": self.dvns}, handle, indent=4)


    def get_entry(self, url_or_alias: Union[str, None] = None) -> tuple[str, dict]:
        """Get the path and contents that belongs to a path or alias.

        Parameters
        ----------
        path_or_alias, optional
            Either an absolute path or an alias, by default None in which
            case the currently selected environment is chosen.

        Returns
        -------
        url:
            The url to the dataverse server, e.g. https://demo.dataverse.org.
        entry:
            Entry for the dataverse server, its alias and API token.

        Raises
        ------
        KeyError
            If the entry can't be found.

        """
        url_or_alias = self.cur_dvn if url_or_alias is None else url_or_alias
        for url, entry in self.dvns.items():
            if url == str(url_or_alias):
                return url, entry

        for url, entry in self.dvns.items():
            if entry.get("alias", None) == str(url_or_alias):
                return url, entry

        raise KeyError(f"Cannot find entry with name/path '{path_or_alias}'")
     
