# Operator Report

Total escalated incidents: 4

## INC-0001 | littering
- Camera: CAM-ENT-01
- Zone: apartment_lobby
- Time: 2026-04-11T09:12:10Z
- Confidence: 0.88
- Severity: medium
- Object: cup
- Trigger reasons: motion_in_roi, new_object_detected, drop_pattern_detected, stationary_object_threshold_exceeded, person_left_object_behind, person_object_separation_detected
- Rationale: A small discard-like object appeared through a drop pattern and stayed in the cleanup zone.
- Recommended action: Queue housekeeping alert and log repeat hotspot activity.

## INC-0002 | unattended_item
- Camera: CAM-STN-03
- Zone: station_waiting_area
- Time: 2026-04-11T09:14:45Z
- Confidence: 0.90
- Severity: high
- Object: backpack
- Trigger reasons: motion_in_roi, new_object_detected, stationary_object_threshold_exceeded, person_left_object_behind, person_object_separation_detected
- Rationale: The item remained stationary after the nearby person left or moved beyond the safety distance.
- Recommended action: Alert security staff for unattended-object verification.

## INC-0003 | illegal_dumping
- Camera: CAM-PARK-02
- Zone: parking_dropoff
- Time: 2026-04-11T09:19:02Z
- Confidence: 0.93
- Severity: high
- Object: box
- Trigger reasons: motion_in_roi, new_object_detected, stationary_object_threshold_exceeded, person_left_object_behind, possible_vehicle_dumping
- Rationale: A new object appeared after a vehicle-related event and remained in the monitored zone.
- Recommended action: Dispatch site staff and retain clip for audit review.

## INC-0005 | littering
- Camera: CAM-CIN-05
- Zone: cinema_exit
- Time: 2026-04-11T09:31:08Z
- Confidence: 0.88
- Severity: medium
- Object: wrapper
- Trigger reasons: motion_in_roi, new_object_detected, drop_pattern_detected, stationary_object_threshold_exceeded, person_left_object_behind, person_object_separation_detected
- Rationale: A small discard-like object appeared through a drop pattern and stayed in the cleanup zone.
- Recommended action: Queue housekeeping alert and log repeat hotspot activity.
