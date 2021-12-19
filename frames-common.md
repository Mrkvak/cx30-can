## Multi-byte variables

| ID  | B0 | B1 | B2 | B3 | B4 | B5 | B6 | B7 | Description             |
| --  | -- | -- | -- | -- | -- | -- | -- | -- | --                      |
| 40A | 01 | XX | XX | XX | XX | XX | XX | XX | First 7 bytes of VIN in ASCII |
| 40A | 02 | XX | XX | XX | XX | XX | XX | XX | Second 7 bytes of VIN in ASCII |
| 40A | 03 | XX | XX | XX | XX | 00 | 00 | 00 | Last 3 bytes of VIN in ASCII |
| 40A | 04 | XX | XX | XX | XX | 00 | 00 | 00 | Model name? DME1  in my case, DM would fit.|

## Single-bit variables
| ID  | Byte | Bit  | Default/Idle |  Description                         |
| --  |  --  | --   |      --      |     --                               |
| **091** |  |      |              | **Light/wipers stalks**            |
| 091 |  01  | 1    | 0x00         | 1 = fog lamp                         |
| 091 |  01  | 2..3 | 0x00         |                                      |
| 091 |  01  | 4    | 0x00         | 1 = high beams                       |
| 091 |  01  | 5    | 0x00         | 1 = headlights                       |
| 091 |  01  | 6    | 0x00         | 1 = Parking lights                   |
| 091 |  01  | 7..8 | 0xc0         | Always on ?                          |
| 091 |  02  | 1    | 0x00         |                                      |
| 091 |  02  | 2    | 0x00         | 1 = auto headlights button pressed   |
| 091 |  02  | 3..4 | 0x00         |                                      |
| 091 |  02  | 5    | 0x00         | 1 = right turn signal                |
| 091 |  02  | 6    | 0x00         | 1 = left turn signal                 |
| 091 |  02  | 7    | 0x00         | stalk held in "off" position         |
| 091 |  02  | 8    | 0x00         |                                      |
| 091 |  03  | 1    | 0x00         | 1 = rear window washer               |
| 091 |  03  | 2    | 0x00         | 1 = front window washer              |
| 091 |  03  | 3..4 | 0x00         | 01 = rear wiper fast, 11 = rear wiper slow                  |
| 091 |  03  | 5..6 | 0x00         | 01 = intermittent/signleshot, 10 = fast, 11 = auto   |
| 091 |  03  | 7..8 | 0xc0         | Always on ?                          |
| 091 |  04  | 1..8 | 0x00         |                                      |
| 091 |  05  | 1..8 | 0x00         |                                      |
| 091 |  06  | 1..8 | 0x00         | Intermittent wipers delay (0x00, 0x32, 0x46, 0x5a) |
| 091 |  07  | 1..4 |              | Sequence number                      |
| 091 |  07  | 5..8 | 0x00         |                                      |
| 091 |  08  | 1..8 |              | Checksum, target value is 0x67       |
| **099** |  |      |              | **Lights state?**                    |
| 099 |  01  | 1..8 | 0x00         | C2 = auto, headlights on, 84 = parking lt. on, C6 = manual, headights on, E7= highbeams on |
| 099 |  02  | 1..8 | 0x70         |                                      |
| 099 |  03  | 1..8 | 0x00         |                                      |
| 099 |  04  | 1..8 | 0x00         |                                      |
| 099 |  05  | 1..8 | 0x1f         |                                      |
| 099 |  06  | 1..8 | 0xfe         |                                      |
| 099 |  07  | 1..4 |              | Sequence number                      |
| 099 |  07  | 5..8 | 0x10         |                                      |
| 099 |  08  | 1..8 |              | Checksum (target 5f)                 |



| **440** |  |      |              | **???**                            |
| 440 |  01  | 1..7 | 0x60         |                                      |
| 440 |  01  |  8   |       0      | 1 = driver door open                 |
| 440 |  02  | 1..8 | 0x00         |                                      |
| 440 |  03  | 1..8 | 0x00         |                                      |
| 440 |  04  | 1..8 | 0x00         |                                      |
| 440 |  05  | 1..8 | 0x20         |                                      |
| 440 |  06  | 1..8 | 0x01         |                                      |
| 440 |  07  | 1..4 |              | Sequence number                      |
| 440 |  07  | 5..8 | 0x08         |                                      |
| 440 |  08  | 1..8 |              | Checksum, target value is 0xB4       |
|

| **581** |  |      |              | ** ??? **                            |
| 581 |  01  | 1..8 | 0x01         |                                      |
| 581 |  02  | 1..8 | 0x00         |                                      |
| 581 |  03  | 1    | 0x00         | 1 = Dome light on                    |
| 581 |  03  | 2    | 0x00         | 1 = parking lights / instr lights on |
| 581 |  03  | 3    | 0x00         | 1 = hazard lights on                 |
| 581 |  03  | 5..8 | 0xa0         |                                      |
| 581 |  04  | 1..8 | 0x00         | 0x10 with hazards, 0x80 with parking |
| 581 |  05  | 1..8 | 0x10         |                                      |
| 581 |  06  | 1..8 | 0x00         |                                      |
| 581 |  07  | 1..8 | 0x13         |                                      |
| 581 |  08  | 1..8 | 0x01         |                                      |
|     |      |      |              |                                      |
     |      |      |              |                                      |

