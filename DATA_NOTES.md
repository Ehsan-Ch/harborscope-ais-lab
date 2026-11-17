# Source attribution and use notes

Source credit: **NOAA Office for Coastal Management, Bureau of Ocean Energy Management and U.S. Coast Guard Navigation Center**, Nationwide Automatic Identification System2024 / Marine Cadastre.

- [Dataset metadata](https://www.fisheries.noaa.gov/inport/item/73064)
- [Current archive index](https://noaaocm.blob.core.windows.net/ais/csv2/csv2024/index.html)
- [Field dictionary](https://coast.noaa.gov/data/marinecadastre/ais/data-dictionary.pdf)
- [Provider vessel-traffic overview](https://coast.noaa.gov/digitalcoast/data/vesseltraffic.html)

Archive retrieved17November2026; exact URL, byte count and local integrity hash are in `data/source_manifest.json`. The metadata records no access constraints and specifies coastal/ocean planning as the use constraint/purpose. This project is a historical coastal shipping-data research exercise and preserves source credit. No exclusive license is asserted over government source observations. Users should consult the provider's current metadata and notices for their intended reuse.

Changes: nationwide observations were spatially/type-filtered, validated, reduced to project vessel IDs and segmented into low-speed observed episodes. Raw MMSI identifiers, names, IMO and call signs are omitted from the reduced output. Project IDs are not a guarantee of anonymity or unlinkability to the source.

The MIT `LICENSE` covers this project's original source code. It does not claim ownership of or relicense the underlying source observations. The source archive itself is not redistributed in this repository. No provider affiliation, endorsement, authoritative port boundary or navigational suitability is implied.
