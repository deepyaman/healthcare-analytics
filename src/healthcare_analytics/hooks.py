# Copyright 2020 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited ("QuantumBlack") name and logo
# (either separately or in combination, "QuantumBlack Trademarks") are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
# or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

"""Project hooks."""
from pathlib import Path
from typing import AbstractSet, Any, Dict, Iterable, List, Optional

from kedro.config import ConfigLoader
from kedro.framework.hooks import hook_impl
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline, pipeline
from kedro.versioning import Journal

from healthcare_analytics.pipelines import feature, target


def _load_config(config_files: List[Path]) -> Dict[str, Any]:
    """Recursively load all configuration files, which satisfy
    a given list of glob patterns from a specific path.

    Args:
        config_files: Configuration files sorted in the order of precedence.

    Raises:
        ValueError: If 2 or more configuration files contain the same key(s).

    Returns:
        Resulting configuration dictionary.

    """
    # for performance reasons
    import anyconfig  # pylint: disable=import-outside-toplevel

    config = {}
    keys_by_filepath = {}  # type: Dict[Path, AbstractSet[str]]

    def _check_dups(file1: Path, conf: Dict[str, Any]) -> None:
        dups = set()
        for file2, keys in keys_by_filepath.items():
            common = ", ".join(sorted(conf.keys() & keys))
            if common:
                if len(common) > 100:
                    common = common[:100] + "..."
                dups.add("{}: {}".format(str(file2), common))

        if dups:
            msg = "Duplicate keys found in {0} and:\n- {1}".format(
                file1, "\n- ".join(dups)
            )
            raise ValueError(msg)

    for config_file in config_files:
        cfg = {
            k: v
            for k, v in anyconfig.load(config_file, ac_template=True).items()
            if not k.startswith("_")
        }
        _check_dups(config_file, cfg)
        keys_by_filepath[config_file] = cfg.keys()
        config.update(cfg)
    return config


class ProjectHooks:
    @hook_impl
    def register_pipelines(self) -> Dict[str, Pipeline]:
        """Register the project's pipeline.

        Returns:
            A mapping from a pipeline name to a ``Pipeline`` object.

        """
        feature_pipeline = feature.create_pipeline()
        target_pipeline = target.create_pipeline()

        return {
            "__default__": Pipeline(
                [
                    pipeline(
                        feature_pipeline,
                        inputs={
                            "raw_data": "raw_train",
                            "raw_patient_profile": "raw_patient_profile",
                            "raw_health_camp_detail": "raw_health_camp_detail",
                        },
                        namespace="train",
                    ),
                    pipeline(
                        feature_pipeline,
                        inputs={
                            "raw_data": "raw_test",
                            "raw_patient_profile": "raw_patient_profile",
                            "raw_health_camp_detail": "raw_health_camp_detail",
                        },
                        namespace="test",
                    ),
                    target_pipeline,
                ]
            )
        }

    @hook_impl
    def register_config_loader(self, conf_paths: Iterable[str]) -> ConfigLoader:
        import kedro.config.config

        kedro.config.config._load_config = _load_config
        return ConfigLoader(conf_paths)

    @hook_impl
    def register_catalog(
        self,
        catalog: Optional[Dict[str, Dict[str, Any]]],
        credentials: Dict[str, Dict[str, Any]],
        load_versions: Dict[str, str],
        save_version: str,
        journal: Journal,
    ) -> DataCatalog:
        return DataCatalog.from_config(
            catalog, credentials, load_versions, save_version, journal
        )
