# Research note — observed vessel dwell and reporting gaps

## Question

How can a shipping-data pipeline summarize stationary-looking vessel activity without treating gaps in AIS coverage as known waiting time? This study uses a fixed rectangle around the Los Angeles/Long Beach area, one day of data and transparent segmentation rules. The area, vessel types, day, speed, gap and minimum-span parameters were recorded before extraction. This is a locally documented protocol, not an externally registered study.

## Provenance and schema

The source is NOAA/BOEM/USCG Nationwide AIS2024, on1January2024. [NOAA's metadata](https://www.fisheries.noaa.gov/inport/item/73064) describes filtering original observations to a one-minute frequency and identifies the coastal/ocean-planning purpose. The archive covers nationwide observations; this report analyzes a small commercial-vessel subset.

The old NOAA ZIP URL returned404. The current official Azure-hosted index lists `ais-2024-01-01.csv.zst`, a196,492,824-byte file, with a2026 distribution timestamp. The locally computed SHA256 is pinned in the manifest; no provider checksum comparison is claimed. The downloaded file has lowercase fields (`base_date_time`, `latitude`, `longitude`, `vessel_type`, etc.), whereas the2024 portion of the published data dictionary shows older capitalized names. The extraction code explicitly supports both observed field-name families and saves the actual header in `data/extraction.json`.

The [NOAA data dictionary](https://coast.noaa.gov/data/marinecadastre/ais/data-dictionary.pdf) defines SOG in knots and timestamps in UTC. [IMO operational AIS guidance](https://www.navcen.uscg.gov/sites/default/files/pdf/ais/references/IMO_A1106_29_Revised_guidelines.pdf) explains that navigational status is manually entered and should be updated as activity changes. Hence codes1 and5 are treated as reported context, not independently observed anchoring or mooring.

## Retention and cleaning

We stream all7,293,408 nationwide records. Coordinates outside valid domains or nonfinite values are rejected;105,092 reports fall in the study rectangle. Cargo/tanker type codes70–89 retain12,506 rows from36 vessels (22cargo,14tanker). Eight study-area rows have an unknown/unparseable type and are excluded before the commercial filter. Quality-ledger counters describe each stage, not a universal accuracy estimate for the source.

Commercial retained rows must have a nine-digit MMSI, finite speed between0 and50knots, status0–15 and the study-day timestamp. Duplicate vessel/time records are grouped: identical values keep one; conflicts reject all affected rows to avoid file-order-dependent selection. Neither occurred in this retained sample. Project IDs are assigned by sorted source MMSI and the identity strings are discarded from exported points. Reidentification from the original public data remains possible.

## Segmentation

SOG≤0.5knots is low-speed. Low-speed status5 becomes reported-moored; status1 becomes reported-anchor; other values become other-low-speed. Faster reports are moving, regardless of reported navigation status.

For each vessel, reports are time-sorted. A run continues only while state is unchanged, each inter-report interval is≤15minutes, and each point stays within500metres of the run's first report. A run with at least two reports and a span≥20minutes becomes an episode. Durations are last timestamp minus first timestamp; no extrapolated minutes are added at either boundary. State changes, reporting gaps and radius violations split runs. Mean coordinates locate episodes on the plot, and are not berth assignments.

The radius rule limits slowly drifting tracks; it does not prove a vessel was stationary at a fixed berth. The speed value can be stale or inaccurate. Actual activity between reports is unknown, even for an accepted interval. All episodes are observed fragments, and none should be called complete physical port visits without additional evidence.

## Results and sensitivity

Default rules yield38 episodes across32 vessels:16reported-moored,18reported-anchor and4other-low-speed. Their summed elapsed spans are582.8 vessel-hours; this is cumulative across vessels, not582.8 hours of wall-clock time. Median span is1193.4minutes (19.9hours).

Twenty-seven episodes start at the first retained observation for a vessel, and21 end at the last. One ends at a radius split and16 at state changes. These boundary counts are strong reasons not to interpret the median as port turnaround or service duration. Entering/leaving the study rectangle, missing coverage and the day cutoff can all affect the observation boundary.

With all other defaults fixed, a5-minute gap rule yields250 episodes and539.45vessel-hours, with a72-minute median;15 and30minutes yield38 episodes and582.81vessel-hours. A stricter gap threshold fragments observed spans, while a permissive threshold assumes continuity over longer unseen intervals. Neither setting is optimized as ground truth. The5/15/30 comparison is descriptive sensitivity, not uncertainty bounds or evidence about port productivity.

## Track display

Displayed tracks sample the first report, approximately five-minute-separated reports, and the final report for each vessel, yielding6006 positions. The plot uses longitude and latitude in a local approximation with longitude scaled by cosine of the area's mean latitude. There is no coastline, shoreline exclusion, bathymetry or terminal polygon. Lines break when sampled reports are more than15minutes apart; a line segment is a visual interpolation, not a known traveled route. The replay clock only filters track positions. Full-day episode circles and totals are intentionally retrospective and remain labeled as such.

## Limits and next work

This is one holiday, one rectangle and a cargo/tanker subset. AIS requires both transmission and reception; absent data are not absent vessels. Status can be manually wrong or stale. No inferred destinations, cargo volumes, berth occupancy, arrivals/departures, congestion, emissions or waiting costs are reported. Vessel types are reported AIS categories and are not registry-verified.

For a wider operational study, obtain weeks of data, preserve positions outside the port area to verify transitions, add authoritative berth/anchorage polygons, quantify coverage gaps and compare inferred events with independent port-call logs. The current sample cannot validate such claims.

## Reproduce and inspect

The retained CSV is sufficient to reproduce episodes, track sampling and sensitivity with `python build.py --from-points`. The full source archive is required to independently reproduce the spatial/type extraction. CI verifies the retained-data stage and tests synthetic boundary cases. A SHA256 pin provides repeatability and corruption detection, not an independent guarantee of the provider's positional accuracy.
