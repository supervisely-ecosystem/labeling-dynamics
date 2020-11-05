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
        aa.IMAGE_REVIEW_STATUS_UPDATED
    ]
    activity_json = api.team.get_activity(TEAM_ID, filter_actions=labeling_actions)
    activity_df = pd.DataFrame(activity_json)

    # sort by date?
    activity_df['date'] = pd.to_datetime(activity_df['date'])

    all_actions_count = activity_df.groupby("action")["action"].count().reset_index(name='count')
    all_actions_count = all_actions_count.sort_values("count", ascending=False)
    print("---\n", all_actions_count)

    user_total_actions = activity_df.groupby("user")["user"].count().reset_index(name='count')
    user_total_actions = user_total_actions.sort_values("count", ascending=False)
    print("---\n", user_total_actions)

    user_action_count = activity_df.groupby(["user", "action"])["action"].count().reset_index(name='count')
    user_action_count = user_action_count.sort_values(["user", "count"], ignore_index=True, ascending=(True, False))
    print("---\n", user_action_count)

    lj_actions_count = activity_df.groupby(["job", "action"])["action"].count().reset_index(name='count')
    lj_actions_count = lj_actions_count.sort_values(["job", "count"], ignore_index=True, ascending=(True, False))
    print("---\n", lj_actions_count)

    user_lj_actions_count = activity_df.groupby(["user", "job", "action"])["action"].count().reset_index(name='count')
    user_lj_actions_count = user_lj_actions_count.sort_values(["user", "job", "count"], ascending=(True, True, False))
    print("---\n", user_lj_actions_count)

    start_period = activity_df["date_time"].min()
    print("---\n", start_period)

    end_period = activity_df["date_time"].max()
    print("---\n", end_period)

# tag <pre></pre> скрол?? через div overflow-hidden fix width, height
# pandas to sly-table

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