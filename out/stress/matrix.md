## 1. Policy sensitivity: current submission vs alternative keys

| Key | Rows (union) | Exact | Exact % | Weighted % | Missed applies | Extra applies | Unknown/applies swaps |
|---|---|---|---|---|---|---|---|
| K_strict | 5298 | 4688 | 88.5 | 92.3 | 0 | 448 | 448 |
| K_lenient | 5298 | 4395 | 83.0 | 81.0 | 853 | 0 | 853 |
| K_cutoff | 5298 | 5288 | 99.8 | 99.8 | 8 | 0 | 8 |
| K_derivedunits | 5298 | 4777 | 90.2 | 88.3 | 521 | 0 | 521 |
| K_noprecedence | 5298 | 4928 | 93.0 | 92.6 | 267 | 0 | 2 |
| K_omit | 5380 | 5298 | 98.5 | 99.0 | 0 | 0 | 0 |

Per category (exact/rows) and per city, by key:

- **K_strict**: algorithmic_rent_setting 740/920; application_screening_fees 690/690; just_cause_eviction 718/945; rent_increase_limits 475/598; screening_restrictions 1430/1470; security_deposits 635/675
  cities: Berkeley 360/560; Boston 600/600; Cambridge 500/500; Hoboken 360/400; Jersey City 400/450; Los Angeles 673/885; Newark 448/450; San Diego 400/500; San Francisco 947/953
- **K_lenient**: algorithmic_rent_setting 920/920; application_screening_fees 550/690; just_cause_eviction 755/945; rent_increase_limits 495/598; screening_restrictions 1140/1470; security_deposits 535/675
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 200/400; Jersey City 200/450; Los Angeles 881/885; Newark 102/450; San Diego 400/500; San Francisco 952/953
- **K_cutoff**: algorithmic_rent_setting 920/920; application_screening_fees 690/690; just_cause_eviction 941/945; rent_increase_limits 594/598; screening_restrictions 1470/1470; security_deposits 673/675
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 400/400; Jersey City 450/450; Los Angeles 875/885; Newark 450/450; San Diego 500/500; San Francisco 953/953
- **K_derivedunits**: algorithmic_rent_setting 920/920; application_screening_fees 595/690; just_cause_eviction 853/945; rent_increase_limits 548/598; screening_restrictions 1278/1470; security_deposits 583/675
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 210/400; Jersey City 150/450; Los Angeles 885/885; Newark 419/450; San Diego 500/500; San Francisco 953/953
- **K_noprecedence**: algorithmic_rent_setting 920/920; application_screening_fees 690/690; just_cause_eviction 695/945; rent_increase_limits 478/598; screening_restrictions 1470/1470; security_deposits 675/675
  cities: Berkeley 520/560; Boston 600/600; Cambridge 500/500; Hoboken 400/400; Jersey City 450/450; Los Angeles 756/885; Newark 450/450; San Diego 450/500; San Francisco 802/953
- **K_omit**: algorithmic_rent_setting 920/920; application_screening_fees 690/690; just_cause_eviction 945/970; rent_increase_limits 598/630; screening_restrictions 1470/1470; security_deposits 675/700
  cities: Berkeley 560/560; Boston 600/600; Cambridge 500/500; Hoboken 400/400; Jersey City 450/450; Los Angeles 885/960; Newark 450/450; San Diego 500/500; San Francisco 953/960

## Decision table: candidate policy P scored against each key K (exact %, weighted % in brackets)

| P \ K | current | K_strict | K_lenient | K_cutoff | K_derivedunits | K_noprecedence | K_omit | worst exact | mean exact | worst weighted | mean weighted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| current | 100.0 (100.0) | 88.5 (92.3) | 83.0 (81.0) | 99.8 (99.8) | 90.2 (88.3) | 93.0 (92.6) | 98.5 (99.0) | 83.0 | 93.3 | 81.0 | 93.3 |
| strict | 88.5 (87.4) | 100.0 (100.0) | 73.3 (70.6) | 88.3 (87.2) | 78.7 (76.4) | 86.3 (83.3) | 87.1 (86.5) | 73.3 | 86.0 | 70.6 | 84.5 |
| lenient | 83.0 (89.2) | 73.3 (82.2) | 100.0 (100.0) | 82.8 (89.0) | 90.9 (94.0) | 77.9 (83.3) | 81.7 (88.4) | 73.3 | 84.2 | 82.2 | 89.4 |

No recommendation is made here; the policy choice is the reviewer's.
