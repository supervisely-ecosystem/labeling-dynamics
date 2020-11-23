import os
from dateutil import parser
import datetime
import pandas as pd
import json
import pprint
from collections import defaultdict

import supervisely_lib as sly
from supervisely_lib.api.team_api import ActivityAction as aa

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
TEAM_ACTIVITY = None
DEFAULT_ALL_TIME = None
MEMBERS = None


def calc_stats(api, task_id, activity_df, before_activity, app_logger):
    global DEFAULT_ALL_TIME

    used_ids = set(before_activity['imageId'].unique().tolist())
    app_logger.info("Before Number of unique images: {}".format(len(used_ids)))

    #user-uniq-images
    user_images_counter = defaultdict(int)
    for member in MEMBERS:
        user_images_counter[member.login] = 0
    data_after = json.loads(activity_df.to_json(orient='records'))
    for obj in data_after:
        if obj['imageId'] not in used_ids:
            used_ids.add(obj['imageId'])
            user_images_counter[obj['user']] += 1

    user_images_table_data = []
    for idx, (login, count) in enumerate(user_images_counter.items()):
        user_images_table_data.append([idx, login, count])

    user_image_table = {
        "columns": ["#", "user", "unique images count"],
        "data": user_images_table_data
    }

    actions_count = activity_df.groupby("action")["action"].count().reset_index(name='count')
    actions_count = actions_count.sort_values("count", ignore_index=True, ascending=False)
    actions_count.reset_index(inplace=True)
    actions_count.rename(columns = {'index':'#'}, inplace=True)
    #actions_count = actions_count.append(actions_count.sum(numeric_only=True), ignore_index=True)
    # print("---\n", actions_count)

    user_total_actions = activity_df.groupby("user")["user"].count().reset_index(name='count')
    user_total_actions = user_total_actions.sort_values("count", ascending=False)
    user_total_actions.reset_index(inplace=True)
    user_total_actions.rename(columns={'index': '#'}, inplace=True)
    # print("---\n", user_total_actions)

    user_action_count = activity_df.groupby(["user", "action"])["action"].count().reset_index(name='count')
    user_action_count = user_action_count.sort_values(["user", "count"], ignore_index=True, ascending=(True, False))
    user_action_count.reset_index(inplace=True)
    user_action_count.rename(columns={'index': '#'}, inplace=True)
    # print("---\n", user_action_count)

    lj_actions_count = activity_df.groupby(["job", "action"])["action"].count().reset_index(name='count')
    lj_actions_count = lj_actions_count.sort_values(["job", "count"], ignore_index=True, ascending=(True, False))
    lj_actions_count.reset_index(inplace=True)
    lj_actions_count.rename(columns={'index': '#'}, inplace=True)
    # print("---\n", lj_actions_count)

    user_lj_actions_count = activity_df.groupby(["user", "job", "action"])["action"].count().reset_index(name='count')
    user_lj_actions_count = user_lj_actions_count.sort_values(["user", "job", "count"], ascending=(True, True, False))
    user_lj_actions_count.reset_index(inplace=True)
    user_lj_actions_count.rename(columns={'index': '#'}, inplace=True)
    # print("---\n", user_lj_actions_count)

    start_period = activity_df["date"].min()
    # print("---\n", start_period)

    end_period = activity_df["date"].max()
    # print("---\n", end_period)

    def _pd_to_sly_table(pd):
        return json.loads(pd.to_json(orient='split'))

    fields = []

    if DEFAULT_ALL_TIME is None:
        # initialize widget state only on start
        DEFAULT_ALL_TIME = [
            start_period.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            end_period.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        ]
        fields.append({"field": "state.dtRange", "payload": DEFAULT_ALL_TIME})
        fields.append({"field": "data.allTimeRange", "payload": DEFAULT_ALL_TIME})

    fields.extend([
        {"field": "data.userImageTable", "payload": user_image_table},
        {"field": "data.actionsCount", "payload": _pd_to_sly_table(actions_count)},
        {"field": "data.userTotalActions", "payload": _pd_to_sly_table(user_total_actions)},
        {"field": "data.userActionCount", "payload": _pd_to_sly_table(user_action_count)},
        {"field": "data.ljActionCount", "payload": _pd_to_sly_table(lj_actions_count)},
        {"field": "data.userLjActionCount", "payload": _pd_to_sly_table(user_lj_actions_count)},
    ])
    api.task.set_fields(task_id, fields)


@my_app.callback("preprocessing")
@sly.timeit
def preprocessing(api: sly.Api, task_id, context, state, app_logger):
    global TEAM_ACTIVITY, MEMBERS

    #team = api.team.get_info_by_id(TEAM_ID)
    MEMBERS = api.user.get_team_members(TEAM_ID)

    app_logger.info("Number of members in team: {}".format(len(MEMBERS)))

    app_logger.info("Members info:")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(MEMBERS)

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
    app_logger.info("Activity events count: {}".format(len(activity_json)))

    if len(activity_json) == 0:
        app_logger.info("There are no labeling events. App will be stopped.")
        api.task.set_field(task_id, "data.emptyActivity", True)
        my_app.stop()

    TEAM_ACTIVITY = pd.DataFrame(activity_json)
    app_logger.info("First five activity events:")
    print(TEAM_ACTIVITY[:5])

    TEAM_ACTIVITY['date'] = pd.to_datetime(TEAM_ACTIVITY['date'])
    TEAM_ACTIVITY = TEAM_ACTIVITY.sort_values("date", ascending=True)
    TEAM_ACTIVITY.reset_index(inplace=True)

    empty_df = pd.DataFrame(data=None, columns=TEAM_ACTIVITY.columns)
    calc_stats(api, task_id, TEAM_ACTIVITY, empty_df, app_logger)


@my_app.callback("apply_filter")
@sly.timeit
def apply_filter(api: sly.Api, task_id, context, state, app_logger):
    dt_range = state["dtRange"]
    if dt_range[0] is None or dt_range[1] is None:
        app_logger.warn("DateTime range is not defined")
        return
    begin = parser.parse(dt_range[0]) - datetime.timedelta(seconds=1)
    end = parser.parse(dt_range[1]) + datetime.timedelta(seconds=1)
    filtered = TEAM_ACTIVITY[(TEAM_ACTIVITY['date'] >= begin) & (TEAM_ACTIVITY['date'] <= end)]
    before_activity = TEAM_ACTIVITY[TEAM_ACTIVITY['date'] < begin]
    calc_stats(api, task_id, filtered, before_activity, app_logger)


@my_app.callback("stop")
@sly.timeit
def stop(api: sly.Api, task_id, context, state, app_logger):
    api.task.set_field(task_id, "data.stopped", True)


def main():
    sly.logger.info("Input params", extra={"teamId": TEAM_ID})
    data = {
        "userImageTable": {"columns": [], "data": []},
        "actionsCount": {"columns": [], "data": []},
        "userTotalActions": {"columns": [], "data": []},
        "userActionCount": {"columns": [], "data": []},
        "ljActionCount": {"columns": [], "data": []},
        "userLjActionCount": {"columns": [], "data": []},
        "allTimeRange": None,
        "stopped": False,
        "emptyActivity": False,
    }

    state={
        "dtRange": None,
    }
    initial_events = [{"state": None, "context": None, "command": "preprocessing"}]

    # Run application service
    my_app.run(data=data, state=state, initial_events=initial_events)


if __name__ == "__main__":
    sly.main_wrapper("main", main)