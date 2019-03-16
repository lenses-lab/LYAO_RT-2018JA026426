## US Naval Observatory Nautical Twilight Calendars

[USNO Sunrise/Sunset Calendar Generator](https://aa.usno.navy.mil/data/docs/RS_OneYear.php)

#### Using Form B - Locations Worldwide, one can input:

* year
* Type of Table = Nautical Twilight
* Place Name Label
* Longitude
* Latitude
* Time Zone = 0 hours (for UTC)

#### And hit "Compute Table" to generate an html table of times for every calendar day of year for their desired observing location. Save the html file as a text file.

Some editing may be necessary to ensure that the table is parse-able for all days of year, particularly around time changes. For example, compute a fresh Nautical Twilight table for Pine Bluff Observatory (W 89d 40m, N 43d 05m), year 2000 and compare to the one in this directory. The fresh one has two rows for day 27, due to time change on October 27th. The edited time table simply removed the empty row. Similarly, Jan 19 has a missing time in the fresh table. To fix this, the empty time was replaced with an appropriate time.
