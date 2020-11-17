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

"""
This is a boilerplate pipeline 'target'
generated using Kedro 0.16.6
"""

from kedro.pipeline import Pipeline, node

from healthcare_analytics import utils

from .nodes import create_health_score_target, create_stall_visited_target


def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                utils.make_partial(
                    create_health_score_target, health_score_column="Health_Score"
                ),
                ["raw_train", "raw_first_health_camp_attended"],
                "tgt_first_health_camp_outcome_favorable",
            ),
            node(
                utils.make_partial(
                    create_health_score_target, health_score_column="Health Score"
                ),
                ["raw_train", "raw_second_health_camp_attended"],
                "tgt_second_health_camp_outcome_favorable",
            ),
            node(
                utils.make_partial(
                    create_stall_visited_target,
                    stall_visited_column="Number_of_stall_visited",
                ),
                ["raw_train", "raw_third_health_camp_attended"],
                "tgt_third_health_camp_outcome_favorable",
            ),
            node(
                utils.join_all,
                [
                    "tgt_first_health_camp_outcome_favorable",
                    "tgt_second_health_camp_outcome_favorable",
                    "tgt_third_health_camp_outcome_favorable",
                ],
                "tgt_joined",
            ),
            node(utils.methodcaller("sum", axis=1), "tgt_joined", "tgt_combined",),
            node(
                utils.methodcaller(
                    "to_frame", name="tgt_health_camp_outcome_favorable"
                ),
                "tgt_combined",
                "tgt_health_camp_outcome_favorable",
            ),
        ]
    )
