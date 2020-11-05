import os
from dateutil import parser
import pandas as pd

import supervisely_lib as sly
from supervisely_lib.api.team_api import ActivityAction as aa

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
TEAM_ACTIVITY = None

@my_app.callback("preprocessing")
@sly.timeit
def preprocessing(api: sly.Api, task_id, context, state, app_logger):
    team = api.team.get_info_by_id(TEAM_ID)

    labeling_actions = [
        aa.CREATE_FIGURE,
        aa.UPDATE_FIGURE,
        aa.DISABLE_FIGURE,
        aa.RESTORE_FIGURE,
        aa.ATTACH_TAG,
        aa.UPDATE_TAG_VALUE,
        aa.DETACH_TAG,
    ]
    activity_json = api.team.get_activity(TEAM_ID, filter_actions=labeling_actions)
    activity_df = pd.DataFrame(activity_json)

    all_actions_count = activity_df.groupby("action")["action"].count()

    actions_count = activity_df.groupby("action")["action"].count()


def main():
    sly.logger.info("Input params", extra={"teamId": TEAM_ID})
    data = {
        "jobsTable": {"columns": [], "data": []},
        "avgFtt": "in progress"
    }
    initial_events = [{"state": None, "context": None, "command": "preprocessing"}]

    # Run application service
    my_app.run(data=data, initial_events=initial_events)


if __name__ == "__main__":
    sly.main_wrapper("main", main)