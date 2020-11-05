import os
from dateutil import parser
import supervisely_lib as sly
from supervisely_lib.labeling_jobs.utils import total_items_count, labeled_items_count, reviewed_items_count, \
    accepted_items_count, rejected_items_count, get_job_url, is_on_review



my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
USER_ID = int(os.environ['modal.state.slyMemberId'])
non_zero_ftt = []

@my_app.callback("preprocessing")
@sly.timeit
def preprocessing(api: sly.Api, task_id, context, state, app_logger):
    team = api.team.get_info_by_id(TEAM_ID)
    user = api.user.get_info_by_id(USER_ID)
    all_jobs = api.labeling_job.get_list(team.id)

    jobs = []
    for job in all_jobs:
        if job.assigned_to_id == USER_ID:
            jobs.append(job)

    if len(jobs) == 0:
        raise RuntimeError("There are no labeling jobs assigned to {!r} in team {!r}".format(user.login, team.name))

    stats = [api.labeling_job.get_stats(job.id) for job in jobs]

    columns = ['ID', 'NAME', 'STATUS', 'CREATED_AT', 'ASSIGNED TO', 'TOTAL', 'LABELED', 'REVIEWED', 'ACCEPTED', 'REJECTED', 'FTT (%)']
    data = []
    for job, stat in zip(jobs, stats):
        data_row = []
        data_row.append(job.id)
        data_row.append('<a href="{0}" rel="noopener noreferrer" target="_blank">{1}</a>'
                        .format(get_job_url(api.server_address, job), job.name))
        data_row.append(job.status)
        data_row.append(parser.parse(job.created_at).strftime('%Y/%m/%d/ %H:%M'))
        data_row.append(job.assigned_to_login)
        data_row.append(total_items_count(job))
        data_row.append(labeled_items_count(job))
        data_row.append(reviewed_items_count(job))
        data_row.append(accepted_items_count(job))
        data_row.append(rejected_items_count(job))


        # print for debug
        print("-----------")
        print(job.name)
        print(job.status)
        print(accepted_items_count(job), "/", labeled_items_count(job))
        ftt = 0
        if accepted_items_count(job) == 0 or labeled_items_count(job) == 0:
            ftt = 0
        else:
            ftt = round(accepted_items_count(job) * 100 / labeled_items_count(job), 2)
            non_zero_ftt.append(ftt)
        print(ftt)
        data_row.append(ftt)
        data.append(data_row)

    jobs_table = {
        "columns": columns,
        "data": data
    }
    avg_ftt = 0
    if len(non_zero_ftt) > 0:
        avg_ftt = round(sum(non_zero_ftt) / len(non_zero_ftt), 2)

    fields = [
        {"field": "data.jobsTable", "payload": jobs_table},
        {"field": "data.memberLogin", "payload": user.login},
        {"field": "data.avgFtt", "payload": "{}%".format(avg_ftt)},
    ]
    api.task.set_fields(task_id, fields)

    api.task.set_field(task_id, "data.jobsTable", jobs_table)
    my_app.stop()

def main():
    sly.logger.info("Input params", extra={"teamId": TEAM_ID, "slyMemberId": USER_ID})
    data = {
        "jobsTable": {"columns": [], "data": []},
        "avgFtt": "in progress"
    }
    initial_events = [{"state": None, "context": None, "command": "preprocessing"}]

    # Run application service
    my_app.run(data=data, initial_events=initial_events)


if __name__ == "__main__":
    sly.main_wrapper("main", main)