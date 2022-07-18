<div align="center" markdown>

<img src="https://i.imgur.com/Z112V53.png"/>

# Labeling Events Stats

<p align="center">

  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#History-Of-Runs">History of runs</a>
</p>

[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/labeling-events-stats)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/labeling-events-stats)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/labeling-events-stats)](https://supervise.ly)

</div>

## Overview

Supervisely stores full activity log almost for every action. This app uses activity log to restore all labeeling actions in team (table can be huge) and performs some basic aggregations shown on the screenshot below. All tables can be sorted by any column. The following types of events are considered as labeling actions:

- `CREATE_FIGURE`
- `UPDATE_FIGURE`
- `DISABLE_FIGURE`
- `RESTORE_FIGURE`
- `ATTACH_TAG`
- `UPDATE_TAG_VALUE`
- `DETACH_TAG`
- `IMAGE_REVIEW_STATUS_UPDATED` 

Following metrics are available (every metric is calculated for the selected date-time interval):
- number of unique annotated images for every user
- number of events for every labeling action for the entire team
- number of labeling events that every user performed
- number of events for every user for every action. If you sort this table by user you will see labeling actions for every user. If you will sort this table by labeling actions, then you can compare users within every action
- number of events for every action for every labeling job. Sort table by labeling job to compare actions within one job, sort by action to compare jobs with each other
- number of events for every user for every labeling job for every action (sort by different columns to see different perspectives like described above)

<img src="https://i.imgur.com/HRCbXpl.png"/>

Date-Time Range filter is the following:

<img src="https://i.imgur.com/g7TwBPP.png"/>

## Step 1. Add app from Ecosystem
Log in to the team, then go to `Ecosystem`->`Apps` page. Find app and press `Get` button. Now app is added to your team.

## Step 2. Run app

Go to `Plugins & Apps` section and press `Run` button in front of the app.

## Step 3. Try different time intervals

By default app shows maximum time interval that covers all labeling events in a team. You can change it and press `Apply Filter` button to see statistics for the interested period of time. 

## Step 4. Stop app

Press `App settings` -> `Stop` button right in application session

<img src="https://i.imgur.com/00d29VG.png"/>

---

or in app sessions table.

<img src="https://i.imgur.com/o6ZsNPX.png"/>


## History of runs

To see history of runs go to `Apps` page, click to applications sessions. In front of every session you can see buttons (`View` and `Logs`). Press `View` button to open stopped application session in `Read Only` mode.

<img src="https://i.imgur.com/EVaMydM.png"/>
